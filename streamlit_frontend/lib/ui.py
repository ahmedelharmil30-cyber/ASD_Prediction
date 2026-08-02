"""Small shared UI helpers so every page looks consistent."""
from __future__ import annotations

import streamlit as st

BRAND = "ASD Prediction Platform"

CUSTOM_CSS = """
<style>
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 900px; }
.asd-badge {
    display: inline-block; padding: 5px 14px; border-radius: 999px;
    background: rgba(124, 58, 237, 0.18); color: #EDE9FE; font-size: 0.8rem; font-weight: 700;
    margin-bottom: 0.9rem;
}
.asd-card {
    border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 16px;
    padding: 1.25rem 1.5rem; background: rgba(15, 23, 42, 0.95);
    margin-bottom: 1rem;
}
.asd-recommend {
    border-radius: 16px; padding: 1rem 1.25rem; margin-top: 0.85rem;
    background: rgba(250, 204, 21, 0.12); border: 1px solid rgba(252, 211, 77, 0.5);
    color: #FACC15; font-size: 0.95rem;
}
.asd-footer { color: #94A3B8; font-size: 0.8rem; margin-top: 2rem; text-align: center; }
</style>
"""


def inject_base_style() -> None:
    st.set_page_config(
        page_title=BRAND,
        page_icon="🧩",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def badge(text: str) -> None:
    st.markdown(f'<span class="asd-badge">{text}</span>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        '<div class="asd-footer">Screening tool only — not a diagnosis. '
        "Consult a licensed professional for a formal evaluation.</div>",
        unsafe_allow_html=True,
    )


def gauge_color(risk_pct: float) -> str:
    if risk_pct >= 75:
        return "#DC2626"  # red
    if risk_pct >= 35:
        return "#D97706"  # amber
    return "#16A34A"  # green


def render_gauge(risk_pct: float, label: str = "Predicted ASD likelihood") -> None:
    """Simple gauge built with an SVG arc — no extra chart dependency needed."""
    color = gauge_color(risk_pct)
    pct = max(0.0, min(100.0, risk_pct))
    angle = 180 * (pct / 100.0)
    import math

    cx, cy, r = 100, 100, 80
    x = cx - r * math.cos(math.radians(angle))
    y = cy - r * math.sin(math.radians(angle))
    large_arc = 1 if angle > 180 else 0

    svg = f"""
    <svg viewBox="0 0 200 115" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:280px;margin:auto;display:block;">
      <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#E5E7EB" stroke-width="16" stroke-linecap="round"/>
      <path d="M 20 100 A 80 80 0 {large_arc} 1 {x:.1f} {y:.1f}" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round"/>
      <text x="100" y="95" text-anchor="middle" font-size="28" font-weight="700" fill="#F8FAFC">{pct:.1f}%</text>
    </svg>
    """
    st.markdown(svg, unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#CBD5E1;'>{label}</p>", unsafe_allow_html=True)
