import streamlit as st

from lib.api import cached_health, cached_models
from lib.ui import badge, footer, inject_base_style

inject_base_style()

st.sidebar.title("🧩 ASD Prediction Platform")
st.sidebar.caption("AQ-10 based ASD screening")
health = cached_health()
models = cached_models()
if health:
    st.sidebar.success(f"API online · {health.get('models_loaded', 0)} model(s) loaded")
else:
    st.sidebar.error("API unreachable — start the backend (uvicorn) first.")

badge("Initial screening tool · not diagnostic")
st.title("Early understanding of autism spectrum indicators")
model_names = [m["display_name"] for m in models["models"]] if models and models.get("models") else [
    "Logistic Regression",
    "Random Forest",
    "SVM (RBF)",
    "Decision Tree",
]

st.markdown(
    "A platform built on the standard **AQ-10** questionnaire and multiple "
    "machine learning models trained on real screening data, giving you a "
    "quick first read — never a substitute for a professional evaluation."
)
st.caption(f"Models loaded: {', '.join(model_names)}")

# Model selector (affects screening pages)
model_map = {m['display_name']: m['key'] for m in models.get('models', [])} if models and models.get('models') else {}
if model_map:
    selected_display = st.sidebar.selectbox("Choose model (used by screening)", options=list(model_map.keys()), index=0)
    st.session_state.setdefault('selected_model_key', model_map.get(selected_display))
    st.sidebar.caption(f"Selected: {selected_display}")
else:
    st.session_state.setdefault('selected_model_key', 'default')

st.divider()

steps = [
    ("01", "Answer 10 statements",
     "The short AQ-10 questionnaire: a simple Agree / Disagree set of items."),
    ("02", "Add basic details",
     "Age, gender, family history, and a few demographic fields used by the models."),
    ("03", "Compare candidate models",
     "Review the backend-loaded models and their test-set performance metrics."),
]

cols = st.columns(3)
for col, (n, title, body) in zip(cols, steps):
    with col:
        st.markdown(f"##### {n}")
        st.markdown(f"**{title}**")
        st.caption(body)

st.divider()

c1, c2 = st.columns(2)
with c1:
    if st.button("Start screening →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Screening.py")
with c2:
    if st.button("View model performance", use_container_width=True):
        st.switch_page("pages/2_Models.py")

footer()
