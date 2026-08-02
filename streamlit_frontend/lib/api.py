"""Thin HTTP client for the FastAPI backend.

Mirrors the old frontend/lib/api.ts one-for-one: same endpoints, same
error-handling behavior (network failure vs. non-2xx response), so the
backend does not need to change at all.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")


class ApiError(Exception):
    """Raised for both network failures and non-2xx API responses."""

    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.message = message
        self.status = status


def _request(method: str, path: str, **kwargs) -> Dict[str, Any]:
    try:
        resp = requests.request(method, f"{API_URL}{path}", timeout=15, **kwargs)
    except requests.exceptions.RequestException:
        raise ApiError(
            "Could not reach the API server. Make sure the backend is "
            "running and API_URL is correct.",
            0,
        )

    if not resp.ok:
        detail = resp.reason
        try:
            body = resp.json()
            detail = body.get("detail", detail)
        except ValueError:
            pass
        raise ApiError(detail, resp.status_code)

    return resp.json()


# --- Public API, mirroring lib/api.ts -------------------------------------

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


@st.cache_data(ttl=60, show_spinner=False)
def cached_models() -> Optional[Dict[str, Any]]:
    try:
        return get_models()
    except ApiError:
        return None


def predict_all(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/predict/all", json=payload)


@st.cache_data(ttl=30, show_spinner=False)
def cached_health() -> Optional[Dict[str, Any]]:
    try:
        return health()
    except ApiError:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def cached_metadata() -> Optional[Dict[str, Any]]:
    try:
        return get_metadata()
    except ApiError:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def cached_metrics() -> Optional[Dict[str, Any]]:
    try:
        return get_metrics()
    except ApiError:
        return None
