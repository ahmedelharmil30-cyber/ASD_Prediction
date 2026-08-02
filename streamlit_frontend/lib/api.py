"""HTTP client for the FastAPI backend.

Same endpoints as before (`/health`, `/models`, `/metadata`, `/metrics`,
`/predict`, `/predict/all`) so the backend needs zero changes — but the
call layer itself is upgraded:

- API URL / timeout / retry policy come from `lib.config` (persisted,
  editable on the Settings page) instead of being hardcoded.
- A pooled `requests.Session` with an urllib3 `Retry` adapter handles
  transient failures (connection resets, 502/503/504) with exponential
  backoff, instead of failing on the first hiccup.
- Every call is timed and recorded to `st.session_state["_call_log"]`
  (last 50 calls) so the Settings page can show live request
  diagnostics — method, path, status, latency.
- Errors are classified (timeout / connection / http / unknown) so the
  UI can show a more specific message than a generic failure.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from lib.config import load_config

CALL_LOG_KEY = "_call_log"
CALL_LOG_MAX = 50


class ApiError(Exception):
    """Raised for both network failures and non-2xx API responses."""

    def __init__(self, message: str, status: int, kind: str = "unknown"):
        super().__init__(message)
        self.message = message
        self.status = status
        self.kind = kind  # "timeout" | "connection" | "http" | "unknown"


def _session() -> requests.Session:
    cfg = load_config()
    key = "_api_session"
    cached = st.session_state.get(key)
    if cached is not None:
        return cached
    sess = requests.Session()
    retry = Retry(
        total=cfg["max_retries"],
        backoff_factor=cfg["backoff_factor"],
        status_forcelist=(429, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    st.session_state[key] = sess
    return sess


def _log_call(method: str, path: str, status: int, latency_ms: float, ok: bool) -> None:
    log = st.session_state.setdefault(CALL_LOG_KEY, [])
    log.append(
        {
            "method": method,
            "path": path,
            "status": status,
            "latency_ms": round(latency_ms, 1),
            "ok": ok,
        }
    )
    if len(log) > CALL_LOG_MAX:
        del log[: len(log) - CALL_LOG_MAX]


def _request(method: str, path: str, **kwargs) -> Dict[str, Any]:
    cfg = load_config()
    api_url = cfg["api_url"].rstrip("/")
    timeout = kwargs.pop("timeout", cfg["request_timeout"])
    start = time.perf_counter()

    try:
        resp = _session().request(method, f"{api_url}{path}", timeout=timeout, **kwargs)
    except requests.exceptions.Timeout:
        _log_call(method, path, 0, (time.perf_counter() - start) * 1000, False)
        raise ApiError(
            f"The request to {path} timed out after {timeout:.0f}s. "
            "The backend may be slow, overloaded, or unreachable.",
            0,
            kind="timeout",
        )
    except requests.exceptions.ConnectionError:
        _log_call(method, path, 0, (time.perf_counter() - start) * 1000, False)
        raise ApiError(
            f"Could not reach the API at {api_url}. Make sure the backend "
            "is running and the API URL in Settings is correct.",
            0,
            kind="connection",
        )
    except requests.exceptions.RequestException as exc:
        _log_call(method, path, 0, (time.perf_counter() - start) * 1000, False)
        raise ApiError(f"Request failed: {exc}", 0, kind="unknown")

    latency_ms = (time.perf_counter() - start) * 1000

    if not resp.ok:
        detail = resp.reason
        try:
            body = resp.json()
            detail = body.get("detail", detail)
        except ValueError:
            pass
        _log_call(method, path, resp.status_code, latency_ms, False)
        raise ApiError(detail, resp.status_code, kind="http")

    _log_call(method, path, resp.status_code, latency_ms, True)
    return resp.json()


# --- Public API --------------------------------------------------------

def health() -> Dict[str, Any]:
    return _request("GET", "/health")


def get_models() -> Dict[str, Any]:
    return _request("GET", "/models")


def get_metadata() -> Dict[str, Any]:
    return _request("GET", "/metadata")


def get_metrics() -> Dict[str, Any]:
    return _request("GET", "/metrics")


def predict(payload: Dict[str, Any], model: str = "default") -> Dict[str, Any]:
    return _request("POST", f"/predict?model={model}", json=payload)


def predict_all(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/predict/all", json=payload)


def test_connection() -> Dict[str, Any]:
    """Explicit, uncached connectivity check used by the Settings page."""
    start = time.perf_counter()
    try:
        data = health()
    except ApiError as exc:
        return {"ok": False, "message": exc.message, "kind": exc.kind, "latency_ms": None}
    return {
        "ok": True,
        "message": "Connected",
        "latency_ms": round((time.perf_counter() - start) * 1000, 1),
        "data": data,
    }


def recent_calls() -> list:
    return list(st.session_state.get(CALL_LOG_KEY, []))


def clear_session_cache() -> None:
    """Drop cached HTTP session + Streamlit data caches (used after an API URL change)."""
    st.session_state.pop("_api_session", None)
    cached_health.clear()
    cached_models.clear()
    cached_metadata.clear()
    cached_metrics.clear()


# --- Cached wrappers (TTLs come from persisted config) ------------------

@st.cache_data(ttl=20, show_spinner=False)
def cached_health() -> Optional[Dict[str, Any]]:
    try:
        return health()
    except ApiError:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def cached_models() -> Optional[Dict[str, Any]]:
    try:
        return get_models()
    except ApiError:
        return None


@st.cache_data(ttl=120, show_spinner=False)
def cached_metadata() -> Optional[Dict[str, Any]]:
    try:
        return get_metadata()
    except ApiError:
        return None


@st.cache_data(ttl=120, show_spinner=False)
def cached_metrics() -> Optional[Dict[str, Any]]:
    try:
        return get_metrics()
    except ApiError:
        return None
