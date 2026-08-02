"""Shared design system: theme injection + reusable UI components.

Visual identity: a calm clinical-tech dashboard. Deep charcoal surfaces,
a signal-accent color (configurable on the Settings page), a geometric
display face for headings and a monospaced face for scores/metrics —
so numbers read like instrument readings, not decoration.
"""
from __future__ import annotations

import math
from typing import Optional

import streamlit as st

from lib.config import get_accent, load_config

BRAND = "NeuroSignal · ASD Screening Platform"


def _css(cfg: dict) -> str:
    accent = get_accent(cfg)
    primary = accent["primary"]
    bright = accent["primary_bright"]
    glow = accent["glow"]

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {{
        --accent: {primary};
        --accent-bright: {bright};
        --accent-glow: {glow};
        --bg: #0A0E14;
        --surface: #10151F;
        --surface-2: #151B27;
        --border: rgba(148, 163, 184, 0.14);
        --text: #E7ECF3;
        --text-muted: #8B96A7;
        --success: #34D399;
        --warning: #FBBF24;
        --danger: #F87171;
        --font-display: 'Space Grotesk', 'Inter', sans-serif;
        --font-body: 'Inter', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }}

    html, body, [class*="css"] {{ font-family: var(--font-body); }}
    .stApp {{ background: radial-gradient(ellipse 120% 60% at 50% -10%, rgba(20,184,166,0.08), transparent), var(--bg); }}

    h1, h2, h3, h4 {{ font-family: var(--font-display) !important; letter-spacing: -0.01em; }}
    .block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 980px; }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0C1119 0%, #0A0E14 100%);
        border-right: 1px solid var(--border);
    }}
    section[data-testid="stSidebar"] .stButton>button {{ width: 100%; }}

    /* ---------- Buttons ---------- */
    .stButton>button, .stFormSubmitButton>button {{
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }}
    .stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"] {{
        background: linear-gradient(135deg, var(--accent), var(--accent-bright)) !important;
        border: none !important;
        color: #051014 !important;
        box-shadow: 0 4px 18px var(--accent-glow);
    }}
    .stButton>button[kind="primary"]:hover, .stFormSubmitButton>button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 24px var(--accent-glow);
    }}
    .stButton>button:not([kind="primary"]):hover {{
        border-color: var(--accent) !important;
        color: var(--accent-bright) !important;
    }}

    /* ---------- Inputs ---------- */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] > div, .stTextArea textarea {{
        background: var(--surface) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
    }}
    div[role="radiogroup"] label {{
        background: var(--surface);
        border: 1px solid var(--border);
        padding: 6px 14px;
        border-radius: 999px;
        margin-right: 6px !important;
    }}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid var(--border); }}
    .stTabs [data-baseweb="tab"] {{
        font-family: var(--font-display);
        font-weight: 600;
        color: var(--text-muted);
    }}
    .stTabs [aria-selected="true"] {{ color: var(--accent-bright) !important; }}

    /* ---------- Custom components ---------- */
    .ns-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 14px; border-radius: 999px;
        background: var(--accent-glow); color: var(--accent-bright);
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em;
        border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
        margin-bottom: 0.9rem; font-family: var(--font-display);
    }}

    .ns-hero-title {{
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 2.6rem;
        line-height: 1.08;
        background: linear-gradient(135deg, var(--text) 30%, var(--accent-bright) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }}

    .ns-card {{
        border: 1px solid var(--border); border-radius: 16px;
        padding: 1.35rem 1.5rem; background: var(--surface);
        margin-bottom: 1rem;
        transition: border-color 0.15s ease;
    }}
    .ns-card:hover {{ border-color: color-mix(in srgb, var(--accent) 35%, var(--border)); }}

    .ns-stat {{
        border: 1px solid var(--border); border-radius: 14px;
        padding: 1rem 1.1rem; background: var(--surface-2);
    }}
    .ns-stat .ns-stat-label {{
        font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;
        color: var(--text-muted); font-weight: 600;
    }}
    .ns-stat .ns-stat-value {{
        font-family: var(--font-mono); font-size: 1.5rem; font-weight: 600;
        color: var(--text); margin-top: 2px;
    }}

    .ns-recommend {{
        border-radius: 14px; padding: 1rem 1.25rem; margin-top: 0.85rem;
        background: rgba(251, 191, 36, 0.10); border: 1px solid rgba(251, 191, 36, 0.35);
        color: #FCD34D; font-size: 0.95rem;
    }}

    .ns-notice {{ border-radius: 12px; padding: 0.85rem 1.1rem; font-size: 0.9rem; border: 1px solid; margin-bottom: 0.8rem; }}
    .ns-notice-info {{ background: rgba(56,189,248,0.08); border-color: rgba(56,189,248,0.3); color: #7DD3FC; }}
    .ns-notice-success {{ background: rgba(52,211,153,0.08); border-color: rgba(52,211,153,0.3); color: #6EE7B7; }}
    .ns-notice-warning {{ background: rgba(251,191,36,0.08); border-color: rgba(251,191,36,0.3); color: #FCD34D; }}
    .ns-notice-danger {{ background: rgba(248,113,113,0.08); border-color: rgba(248,113,113,0.3); color: #FCA5A5; }}

    .ns-pill {{
        display: inline-block; padding: 3px 10px; border-radius: 999px;
        font-size: 0.72rem; font-weight: 700; font-family: var(--font-mono);
        background: var(--surface-2); border: 1px solid var(--border); color: var(--text-muted);
        margin-right: 6px;
    }}

    .ns-status-dot {{
        display: inline-block; width: 9px; height: 9px; border-radius: 50%;
        margin-right: 7px; position: relative; top: -1px;
    }}
    .ns-status-online {{ background: var(--success); box-shadow: 0 0 0 3px rgba(52,211,153,0.18); animation: ns-pulse 2s infinite; }}
    .ns-status-offline {{ background: var(--danger); box-shadow: 0 0 0 3px rgba(248,113,113,0.18); }}
    @keyframes ns-pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0.35); }}
        70% {{ box-shadow: 0 0 0 8px rgba(52,211,153,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0); }}
    }}

    .ns-footer {{ color: var(--text-muted); font-size: 0.78rem; margin-top: 2.5rem; text-align: center; }}
    .ns-divider-label {{
        font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 0.08em; margin: 1.6rem 0 0.6rem 0;
    }}
    .ns-mono {{ font-family: var(--font-mono); }}
    </style>
    """


def inject_base_style() -> None:
    cfg = load_config()
    st.set_page_config(
        page_title=BRAND,
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(_css(cfg), unsafe_allow_html=True)


def badge(text: str) -> None:
    st.markdown(f'<span class="ns-badge">◆ {text}</span>', unsafe_allow_html=True)


def hero_title(text: str) -> None:
    st.markdown(f'<div class="ns-hero-title">{text}</div>', unsafe_allow_html=True)


def divider_label(text: str) -> None:
    st.markdown(f'<div class="ns-divider-label">{text}</div>', unsafe_allow_html=True)


def status_pill(online: bool, label: str) -> None:
    cls = "ns-status-online" if online else "ns-status-offline"
    st.markdown(
        f'<span class="ns-status-dot {cls}"></span><span>{label}</span>',
        unsafe_allow_html=True,
    )


def notice(text: str, kind: str = "info") -> None:
    st.markdown(f'<div class="ns-notice ns-notice-{kind}">{text}</div>', unsafe_allow_html=True)


def stat_card(label: str, value: str) -> None:
    st.markdown(
        f'<div class="ns-stat"><div class="ns-stat-label">{label}</div>'
        f'<div class="ns-stat-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def pill(text: str) -> str:
    return f'<span class="ns-pill">{text}</span>'


def footer() -> None:
    st.markdown(
        '<div class="ns-footer">Screening tool only — not a diagnosis. '
        "Consult a licensed professional for a formal evaluation.</div>",
        unsafe_allow_html=True,
    )


def gauge_color(risk_pct: float) -> str:
    if risk_pct >= 75:
        return "#F87171"
    if risk_pct >= 35:
        return "#FBBF24"
    return "#34D399"


def render_gauge(risk_pct: float, label: str = "Predicted ASD likelihood") -> None:
    """SVG arc gauge with a soft glow behind the active arc."""
    cfg = load_config()
    accent = get_accent(cfg)
    color = gauge_color(risk_pct)
    pct = max(0.0, min(100.0, risk_pct))
    angle = 180 * (pct / 100.0)

    cx, cy, r = 100, 100, 80
    x = cx - r * math.cos(math.radians(angle))
    y = cy - r * math.sin(math.radians(angle))
    large_arc = 1 if angle > 180 else 0

    svg = f"""
    <svg viewBox="0 0 200 122" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:300px;margin:auto;display:block;">
      <defs>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1B2330" stroke-width="16" stroke-linecap="round"/>
      <path d="M 20 100 A 80 80 0 {large_arc} 1 {x:.1f} {y:.1f}" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round" filter="url(#glow)"/>
      <text x="100" y="90" text-anchor="middle" font-family="'JetBrains Mono', monospace" font-size="30" font-weight="600" fill="#E7ECF3">{pct:.1f}%</text>
    </svg>
    """
    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;color:var(--text-muted);font-size:0.85rem;margin-top:-6px;'>{label}</p>",
        unsafe_allow_html=True,
    )
