import streamlit as st

from lib.api import cached_health, cached_metrics, cached_models
from lib.config import load_config
from lib.history import load_entries
from lib.ui import badge, divider_label, footer, hero_title, inject_base_style, stat_card, status_pill

inject_base_style()
cfg = load_config()

# ---------------------------------------------------------------- Sidebar
st.sidebar.markdown("### 🧠 NeuroSignal")
st.sidebar.caption("AQ-10 based ASD screening platform")

health = cached_health()
models = cached_models()

with st.sidebar.container():
    status_pill(bool(health), "API online" if health else "API unreachable")
    if health:
        st.sidebar.caption(f"{health.get('models_loaded', 0)} model(s) loaded · {cfg['api_url']}")
    else:
        st.sidebar.caption(f"Trying {cfg['api_url']} — check Settings.")

st.sidebar.divider()

model_map = {m["display_name"]: m["key"] for m in models.get("models", [])} if models and models.get("models") else {}
if model_map:
    default_display = next((d for d, k in model_map.items() if k == cfg.get("default_model_key")), list(model_map.keys())[0])
    selected_display = st.sidebar.selectbox(
        "Default model (Screening)",
        options=list(model_map.keys()),
        index=list(model_map.keys()).index(default_display) if default_display in model_map else 0,
    )
    st.session_state["selected_model_key"] = model_map.get(selected_display)
    st.sidebar.caption(f"Selected: {selected_display}")
else:
    st.session_state.setdefault("selected_model_key", "default")

st.sidebar.divider()
st.sidebar.caption("Navigate")
st.sidebar.page_link("pages/1_Screening.py", label="Screening", icon="📝")
st.sidebar.page_link("pages/2_Models.py", label="Model performance", icon="📊")
st.sidebar.page_link("pages/4_History.py", label="History", icon="🕘")
st.sidebar.page_link("pages/5_Settings.py", label="Settings", icon="⚙️")
st.sidebar.page_link("pages/3_About.py", label="About", icon="ℹ️")

# ---------------------------------------------------------------- Hero
badge("Initial screening tool · not diagnostic")
hero_title("Signal, not certainty.<br/>An AQ-10 read in under two minutes.")

model_names = [m["display_name"] for m in models["models"]] if models and models.get("models") else [
    "Logistic Regression", "Random Forest", "SVM (RBF)", "Decision Tree",
]

st.markdown(
    "Built on the standard **AQ-10** questionnaire and an ensemble of machine "
    "learning models trained on real screening data. Every model votes, you "
    "see the consensus and the disagreement — never a black box, and never "
    "a substitute for a professional evaluation."
)

st.divider()

# ---------------------------------------------------------------- Stat row
entries = load_entries()
metrics = cached_metrics()
best_f1 = None
if metrics and metrics.get("models"):
    f1s = [v["metrics"].get("f1_score") for v in metrics["models"].values() if v.get("metrics", {}).get("f1_score") is not None]
    if f1s:
        best_f1 = max(f1s)

c1, c2, c3, c4 = st.columns(4)
with c1:
    stat_card("Models loaded", str(health.get("models_loaded", "—")) if health else "—")
with c2:
    stat_card("Best F1 score", f"{best_f1:.3f}" if best_f1 is not None else "—")
with c3:
    stat_card("Screenings run", str(len(entries)))
with c4:
    stat_card("Active model set", ", ".join(model_names[:2]) + ("…" if len(model_names) > 2 else "") if model_names else "—")

st.markdown("<br/>", unsafe_allow_html=True)

# ---------------------------------------------------------------- Steps
divider_label("How it works")

steps = [
    ("01", "Answer 10 statements", "The short AQ-10 questionnaire: a simple Agree / Disagree set of items."),
    ("02", "Add basic details", "Age, gender, family history, and a few demographic fields used by the models."),
    ("03", "Compare candidate models", "Run every model or one specific model, and see where they agree or split."),
]

cols = st.columns(3)
for col, (n, title, body) in zip(cols, steps):
    with col:
        st.markdown(f'<div class="ns-card"><span class="ns-mono" style="color:var(--accent-bright);font-weight:700;">{n}</span>'
                     f'<div style="font-weight:700;margin-top:6px;">{title}</div>'
                     f'<div style="color:var(--text-muted);font-size:0.88rem;margin-top:4px;">{body}</div></div>',
                     unsafe_allow_html=True)

st.divider()

c1, c2 = st.columns(2)
with c1:
    if st.button("Start screening →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Screening.py")
with c2:
    if st.button("View model performance", use_container_width=True):
        st.switch_page("pages/2_Models.py")

footer()
