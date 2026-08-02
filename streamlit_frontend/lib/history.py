"""Persistent screening history.

Every completed screening is appended to `data/history.json` on disk (in
addition to being kept in `st.session_state` for the current session), so
past results survive a browser refresh or app restart. This is local
file storage only — nothing is sent anywhere except the FastAPI backend
the app already talks to for predictions.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_PATH = DATA_DIR / "history.json"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_entries() -> List[Dict[str, Any]]:
    _ensure_dir()
    if not HISTORY_PATH.exists():
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write(entries: List[Dict[str, Any]]) -> None:
    _ensure_dir()
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def add_entry(payload: Dict[str, Any], response: Dict[str, Any], limit: int = 200) -> Dict[str, Any]:
    """Append a new screening result and prune to `limit` most recent."""
    entry = {
        "id": uuid.uuid4().hex[:12],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": payload,
        "response": response,
    }
    entries = load_entries()
    entries.append(entry)
    if len(entries) > limit:
        entries = entries[-limit:]
    _write(entries)
    return entry


def delete_entry(entry_id: str) -> None:
    entries = [e for e in load_entries() if e.get("id") != entry_id]
    _write(entries)


def clear_all() -> None:
    _write([])


def as_dataframe() -> pd.DataFrame:
    entries = load_entries()
    rows = []
    for e in entries:
        resp = e.get("response", {})
        rows.append(
            {
                "id": e.get("id"),
                "timestamp": e.get("created_at", "")[:19].replace("T", " "),
                "consensus": resp.get("consensus_class"),
                "agreement_pct": round((resp.get("agreement_ratio") or 0) * 100, 1),
                "aq10_total": resp.get("aq10_total_score"),
                "age": e.get("input", {}).get("age"),
                "gender": e.get("input", {}).get("gender"),
                "country": e.get("input", {}).get("country_of_res"),
                "best_model": resp.get("best_model_key"),
            }
        )
    return pd.DataFrame(rows)


def export_csv() -> str:
    df = as_dataframe()
    return df.to_csv(index=False)
