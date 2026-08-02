"""Advanced shared design system for every page.

This module is presentation-only: fonts, colors, cards, gauges, layout
chrome, nav, etc. It never talks to the network — all backend I/O still
goes exclusively through lib/api.py, untouched by this redesign.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import streamlit as st

BRAND = "NeuroScreen AI"
TAGLINE = "AQ-10 Clinical Screening Intelligence"

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#05070D",
    "bg_soft": "#0A0E18",
    "surface": "#0F1420",
    "surface_2": "#141A2A",
    "border": "rgba(148, 163, 184, 0.14)",
    "border_strong": "rgba(148, 163, 184, 0.28)",
    "text": "#F1F5F9",
    "text_dim": "#94A3B8",
    "text_faint": "#64748B",
    "violet": "#8B5CF6",
    "violet_soft": "rgba(139, 92, 246, 0.14)",
    "cyan": "#22D3EE",
    "cyan_soft": "rgba(34, 211, 238, 0.14)",
    "green": "#34D399",
    "amber": "#FBBF24",
    "red": "#F87171",
    "gradient": "linear-gradient(135deg, #8B5CF6 0%, #6366F1 45%, #22D3EE 100%)",
}

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* ---- page shell ------------------------------------------------------- */
.stApp {{
    background:
        radial-gradient(ellipse 900px 500px at 15% -10%, rgba(139,92,246,0.16), transparent 60%),
        radial-gradient(ellipse 800px 500px at 100% 0%, rgba(34,211,238,0.10), transparent 55%),
        {COLORS['bg']};
}}
.block-container {{
    padding-top: 2.2rem;
    padding-bottom: 4rem;
    max-width: 980px;
}}
#MainMenu, footer {{visibility: hidden;}}

/* ---- typography --------------------------------------------------------*/
h1, h2, h3, h4 {{
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.02em;
    color: {COLORS['text']} !important;
}}
h1 {{ font-weight: 800 !important; }}
p, span, li, label, .stMarkdown {{ color: {COLORS['text']}; }}
.stCaption, small {{ color: {COLORS['text_dim']} !important; }}

/* ---- hero ---------------------------------------------------------------*/
.ns-hero {{
    position: relative;
    padding: 2.4rem 2.2rem;
    border-radius: 24px;
    background: linear-gradient(160deg, rgba(139,92,246,0.16), rgba(34,211,238,0.06));
    border: 1px solid {COLORS['border_strong']};
    overflow: hidden;
    margin-bottom: 1.6rem;
}}
.ns-hero::before {{
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(circle at 90% 10%, rgba(139,92,246,0.35), transparent 55%);
    pointer-events: none;
}}
.ns-eyebrow {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 13px; border-radius: 999px;
    background: {COLORS['violet_soft']}; border: 1px solid rgba(139,92,246,0.35);
    color: #D8CCFB; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.04em;
    text-transform: uppercase; margin-bottom: 1rem;
}}
.ns-hero h1 {{ font-size: 2.35rem; margin: 0 0 0.5rem 0; line-height: 1.12; }}
.ns-hero .ns-sub {{ color: {COLORS['text_dim']}; font-size: 1.02rem; max-width: 640px; line-height: 1.55; }}

/* ---- pill / status ------------------------------------------------------*/
.ns-pill {{
    display: inline-flex; align-items: center; gap: 7px;
    padding: 5px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
    border: 1px solid {COLORS['border_strong']}; background: {COLORS['surface_2']};
}}
.ns-dot {{ width: 7px; height: 7px; border-radius: 50%; display: inline-block; }}
.ns-dot-green {{ background: {COLORS['green']}; box-shadow: 0 0 8px {COLORS['green']}; }}
.ns-dot-red {{ background: {COLORS['red']}; box-shadow: 0 0 8px {COLORS['red']}; }}
.ns-dot-amber {{ background: {COLORS['amber']}; box-shadow: 0 0 8px {COLORS['amber']}; }}

/* ---- cards ---------------------------------------------------------------*/
.ns-card {{
    border: 1px solid {COLORS['border']};
    background: linear-gradient(180deg, {COLORS['surface']}, {COLORS['bg_soft']});
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}}
.ns-card:hover {{ border-color: {COLORS['border_strong']}; }}
.ns-card-title {{
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
    color: {COLORS['text_faint']}; margin-bottom: 0.6rem;
}}

/* ---- step numbers --------------------------------------------------------*/
.ns-step-num {{
    font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.95rem;
    color: transparent; background: {COLORS['gradient']}; -webkit-background-clip: text;
    background-clip: text; display: inline-block; margin-bottom: 0.35rem;
}}

/* ---- recommendation banner ------------------------------------------------*/
.ns-recommend {{
    border-radius: 16px; padding: 1.1rem 1.35rem; margin-top: 0.9rem;
    background: linear-gradient(135deg, rgba(251,191,36,0.14), rgba(251,191,36,0.05));
    border: 1px solid rgba(251,191,36,0.4);
    color: #FDE68A; font-size: 0.96rem; line-height: 1.5;
}}
.ns-result-good {{
    background: linear-gradient(135deg, rgba(52,211,153,0.14), rgba(52,211,153,0.04));
    border: 1px solid rgba(52,211,153,0.4); color: #A7F3D0;
}}
.ns-result-bad {{
    background: linear-gradient(135deg, rgba(248,113,113,0.14), rgba(248,113,113,0.04));
    border: 1px solid rgba(248,113,113,0.4); color: #FECACA;
}}

/* ---- footer ---------------------------------------------------------------*/
.ns-footer {{
    color: {COLORS['text_faint']}; font-size: 0.8rem; margin-top: 3rem;
    text-align: center; border-top: 1px solid {COLORS['border']}; padding-top: 1.4rem;
}}

/* ---- widgets restyle -------------------------------------------------------*/
div[data-testid="stForm"] {{
    border: 1px solid {COLORS['border']};
    border-radius: 20px;
    padding: 1.8rem 1.9rem;
    background: {COLORS['surface']};
}}
.stButton > button, .stFormSubmitButton > button {{
    border-radius: 12px !important;
    font-weight: 700 !important;
    border: 1px solid {COLORS['border_strong']} !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
    background: {COLORS['gradient']} !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(139,92,246,0.35) !important;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
    transform: translateY(-1px);
    box-shadow: 0 10px 28px rgba(139,92,246,0.5) !important;
}}
div[data-baseweb="select"] > div, .stNumberInput input, .stTextInput input {{
    border-radius: 10px !important;
    background: {COLORS['surface_2']} !important;
}}
div[role="radiogroup"] label {{
    background: {COLORS['surface_2']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 4px 12px !important;
    margin-right: 6px !important;
}}
[data-testid="stMetric"] {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 1rem 1.1rem;
}}
[data-testid="stMetricValue"] {{ color: {COLORS['text']} !important; font-weight: 800 !important; }}
[data-testid="stMetricLabel"] {{ color: {COLORS['text_dim']} !important; }}
[data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; border: 1px solid {COLORS['border']}; }}
.stExpander {{
    border-radius: 14px !important; border: 1px solid {COLORS['border']} !important;
    background: {COLORS['surface']} !important;
}}
hr {{ border-color: {COLORS['border']} !important; }}

/* sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLORS['bg_soft']}, {COLORS['bg']});
    border-right: 1px solid {COLORS['border']};
}}
</style>
"""


def inject_base_style() -> None:
    st.set_page_config(
        page_title=BRAND,
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Layout building blocks
# ---------------------------------------------------------------------------

def sidebar_brand() -> None:
    st.sidebar.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.1rem;">
            <div style="width:34px;height:34px;border-radius:10px;background:{COLORS['gradient']};
                        display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🧠</div>
            <div>
                <div style="font-weight:800;font-size:1.02rem;line-height:1.1;">{BRAND}</div>
                <div style="color:{COLORS['text_faint']};font-size:0.72rem;">{TAGLINE}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)


def status_pill(online: bool, label: str) -> str:
    dot = "ns-dot-green" if online else "ns-dot-red"
    return f'<span class="ns-pill"><span class="ns-dot {dot}"></span>{label}</span>'


def sidebar_status(online: bool, detail: str) -> None:
    pill = status_pill(online, "API online" if online else "API offline")
    st.sidebar.markdown(pill, unsafe_allow_html=True)
    st.sidebar.caption(detail)


def badge(text: str) -> None:
    st.markdown(f'<span class="ns-eyebrow">✦ {text}</span>', unsafe_allow_html=True)


def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="ns-hero">
            <span class="ns-eyebrow">✦ {eyebrow}</span>
            <h1>{title}</h1>
            <div class="ns-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_open(title: Optional[str] = None) -> None:
    inner = f'<div class="ns-card-title">{title}</div>' if title else ""
    st.markdown(f'<div class="ns-card">{inner}', unsafe_allow_html=True)


def card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def step_card(col, number: str, title: str, body: str) -> None:
    with col:
        card_open()
        st.markdown(f'<div class="ns-step-num">{number}</div>', unsafe_allow_html=True)
        st.markdown(f"**{title}**")
        st.caption(body)
        card_close()


def footer() -> None:
    st.markdown(
        f'<div class="ns-footer">{BRAND} is a screening aid only — not a diagnosis. '
        "Consult a licensed professional for a formal evaluation.</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Gauge + result visuals
# ---------------------------------------------------------------------------

def gauge_color(risk_pct: float) -> str:
    if risk_pct >= 75:
        return COLORS["red"]
    if risk_pct >= 35:
        return COLORS["amber"]
    return COLORS["green"]


def render_gauge(risk_pct: float, label: str = "Predicted ASD likelihood") -> None:
    """Polished SVG arc gauge with gradient track and glow needle-less arc."""
    color = gauge_color(risk_pct)
    pct = max(0.0, min(100.0, risk_pct))
    angle = 180 * (pct / 100.0)

    cx, cy, r = 100, 100, 78
    x = cx - r * math.cos(math.radians(angle))
    y = cy - r * math.sin(math.radians(angle))
    large_arc = 1 if angle > 180 else 0

    svg = f"""
    <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:300px;margin:auto;display:block;">
      <defs>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      <path d="M 22 100 A 78 78 0 0 1 178 100" fill="none" stroke="rgba(148,163,184,0.18)" stroke-width="14" stroke-linecap="round"/>
      <path d="M 22 100 A 78 78 0 {large_arc} 1 {x:.1f} {y:.1f}" fill="none" stroke="{color}" stroke-width="14"
            stroke-linecap="round" filter="url(#glow)"/>
      <text x="100" y="90" text-anchor="middle" font-size="30" font-weight="800" fill="#F1F5F9" font-family="Inter, sans-serif">{pct:.1f}%</text>
    </svg>
    """
    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;color:{COLORS['text_dim']};font-weight:600;'>{label}</p>",
        unsafe_allow_html=True,
    )


def result_banner(consensus_yes: bool, headline: str, detail: str) -> None:
    css_class = "ns-result-bad" if consensus_yes else "ns-result-good"
    icon = "🔴" if consensus_yes else "🟢"
    st.markdown(
        f"""
        <div class="ns-card {css_class}" style="text-align:center;">
            <div style="font-size:1.4rem;font-weight:800;margin-bottom:0.3rem;">{icon} {headline}</div>
            <div style="color:{COLORS['text_dim']};font-size:0.92rem;">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_box(text: str) -> None:
    st.markdown(f'<div class="ns-recommend">💡 {text}</div>', unsafe_allow_html=True)


def section_label(text: str) -> None:
    st.markdown(
        f"""<div style="font-size:0.78rem;font-weight:700;letter-spacing:0.05em;
        text-transform:uppercase;color:{COLORS['text_faint']};margin:1.4rem 0 0.5rem 0;">{text}</div>""",
        unsafe_allow_html=True,
    )
