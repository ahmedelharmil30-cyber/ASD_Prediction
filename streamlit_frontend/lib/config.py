"""Persistent app configuration.

Settings set on the Settings page are written to `data/config.json` so
they survive restarts, independent of Streamlit's in-memory session
state. Environment variables (and `.env`) still provide the initial
defaults on first run, mirroring the old behavior.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULTS: Dict[str, Any] = {
    "api_url": os.environ.get("API_URL", "http://localhost:8000").rstrip("/"),
    "request_timeout": float(os.environ.get("API_TIMEOUT", 15)),
    "max_retries": int(os.environ.get("API_MAX_RETRIES", 2)),
    "backoff_factor": float(os.environ.get("API_BACKOFF", 0.5)),
    "default_model_key": os.environ.get("DEFAULT_MODEL_KEY", "default"),
    "run_mode": "all",  # "all" | "single" — which models to call by default
    "persist_history": True,
    "history_limit": 200,
    "accent": os.environ.get("ACCENT", "teal"),  # teal | violet | amber | rose
    "compact_mode": False,
    "show_raw_json": False,
    "cache_ttl_health": 20,
    "cache_ttl_models": 60,
    "cache_ttl_metadata": 120,
    "cache_ttl_metrics": 120,
}

ACCENTS = {
    "teal": {"primary": "#14B8A6", "primary_bright": "#2DD4BF", "glow": "rgba(20,184,166,0.35)"},
    "violet": {"primary": "#7C3AED", "primary_bright": "#A78BFA", "glow": "rgba(124,58,237,0.35)"},
    "amber": {"primary": "#D97706", "primary_bright": "#F59E0B", "glow": "rgba(217,119,6,0.35)"},
    "rose": {"primary": "#E11D48", "primary_bright": "#FB7185", "glow": "rgba(225,29,72,0.35)"},
}


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load persisted config, falling back to defaults for missing keys."""
    _ensure_dir()
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                cfg.update({k: v for k, v in stored.items() if k in DEFAULTS})
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    _ensure_dir()
    clean = {k: cfg.get(k, v) for k, v in DEFAULTS.items()}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)


def reset_config() -> Dict[str, Any]:
    _ensure_dir()
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
    return dict(DEFAULTS)


def get_accent(cfg: Dict[str, Any]) -> Dict[str, str]:
    return ACCENTS.get(cfg.get("accent", "teal"), ACCENTS["teal"])
