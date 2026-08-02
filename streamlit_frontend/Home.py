import streamlit as st

from lib.api import cached_health, cached_models
from lib.ui import (
    BRAND,
    card_close,
    card_open,
    footer,
    hero,
    inject_base_style,
    section_label,
    sidebar_brand,
    sidebar_status,
    step_card,
)

inject_base_style()
sidebar_brand()

health = cached_health()
models = cached_models()

sidebar_status(
    online=bool(health),
    detail=(
        f"{health.get('models_loaded', 0)} model(s) loaded"
        if health
        else "Start the backend (uvicorn) to connect."
    ),
)

model_names = (
    [m["display_name"] for m in models["models"]]
    if models and models.get("models")
    else ["Logistic Regression", "Random Forest", "SVM (RBF)", "Decision Tree"]
)

# Model selector (affects screening pages)
model_map = (
    {m["display_name"]: m["key"] for m in models.get("models", [])}
    if models and models.get("models")
    else {}
)
st.sidebar.divider()
if model_map:
    section_label_html = "Screening model"
    st.sidebar.caption("SCREENING MODEL")
    selected_display = st.sidebar.selectbox(
        "Choose model", options=list(model_map.keys()), index=0, label_visibility="collapsed"
    )
    st.session_state.setdefault("selected_model_key", model_map.get(selected_display))
    st.sidebar.caption(f"Active: **{selected_display}**")
else:
    st.session_state.setdefault("selected_model_key", "default")

st.sidebar.divider()
st.sidebar.caption(
    "Navigate using the pages above — **Screening**, **Models**, and **About**."
)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
hero(
    eyebrow="Initial screening tool · not diagnostic",
    title="Early insight into autism spectrum indicators",
    subtitle=(
        "A precision platform built on the clinically standard <b>AQ-10</b> questionnaire, "
        "cross-validated against multiple machine learning models trained on real screening "
        "data — giving you a fast, evidence-informed first read in under two minutes."
    ),
)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("ML models available", len(model_names))
with c2:
    st.metric("Questionnaire length", "10 items")
with c3:
    st.metric("Avg. completion time", "~2 min")

st.caption("Models loaded: " + ", ".join(model_names))

section_label("How it works")
steps = [
    ("01", "Answer 10 statements", "The short AQ-10 questionnaire: a simple Agree / Disagree set of items."),
    ("02", "Add basic details", "Age, gender, family history, and a few demographic fields used by the models."),
    ("03", "Compare candidate models", "Review the backend-loaded models and their test-set performance metrics."),
]
cols = st.columns(3)
for col, (n, title, body) in zip(cols, steps):
    step_card(col, n, title, body)

st.write("")
c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 Start screening", type="primary", use_container_width=True):
        st.switch_page("pages/1_Screening.py")
with c2:
    if st.button("📊 View model performance", use_container_width=True):
        st.switch_page("pages/2_Models.py")

st.write("")
card_open("Why " + BRAND)
st.markdown(
    """
- **Multi-model consensus** — every prediction is cross-checked across several trained classifiers, not just one.
- **Transparent metrics** — accuracy, precision, recall, and F1 for each model are always visible on the Models page.
- **Private by design** — nothing you enter is stored server-side; history lives only in this browser session.
"""
)
card_close()

footer()
