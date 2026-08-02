from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from lib.api import ApiError, cached_metadata, cached_models, predict, predict_all
from lib.config import load_config
from lib.constants import AQ10_ITEMS_FALLBACK, COUNTRIES, ETHNICITIES, HISTORY_SESSION_KEY, RELATIONS
from lib.history import add_entry
from lib.ui import divider_label, footer, inject_base_style, notice, pill, render_gauge

inject_base_style()
cfg = load_config()

st.title("AQ-10 Screening")
st.caption("Answer honestly — there are no right or wrong answers.")

if HISTORY_SESSION_KEY not in st.session_state:
    st.session_state[HISTORY_SESSION_KEY] = []

meta = cached_metadata()
aq10_items = meta["aq10_items"] if meta and meta.get("aq10_items") else AQ10_ITEMS_FALLBACK

# Live progress — counts answered radios across reruns
answered = sum(1 for i in range(1, 11) if st.session_state.get(f"a{i}") is not None)
st.progress(answered / 10, text=f"{answered}/10 statements answered")

models_info = cached_models()
model_choices = ["All models (consensus)"]
model_key_map = {}
if models_info and models_info.get("models"):
    for m in models_info["models"]:
        model_choices.append(m["display_name"])
        model_key_map[m["display_name"]] = m["key"]

with st.form("screening_form"):
    divider_label("1 · AQ-10 statements")
    st.caption("For each statement, choose the option that fits you best.")
    scores = {}
    for i, question in enumerate(aq10_items, start=1):
        choice = st.radio(
            f"**{i}.** {question}",
            options=["Disagree", "Agree"],
            horizontal=True,
            index=None,
            key=f"a{i}",
        )
        scores[f"A{i}_Score"] = 1 if choice == "Agree" else 0

    divider_label("2 · About you")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
        gender = st.selectbox("Gender", options=["Female", "Male"])
        ethnicity = st.selectbox("Ethnicity", options=ETHNICITIES)
        relation = st.selectbox("Who is completing this?", options=RELATIONS)
    with col2:
        country = st.selectbox("Country of residence", options=COUNTRIES, index=COUNTRIES.index("United States"))
        jaundice = st.radio("Born with jaundice?", options=["No", "Yes"], horizontal=True)
        austim = st.radio("Family history of autism?", options=["No", "Yes"], horizontal=True)
        used_app_before = st.radio("Used a screening app before?", options=["No", "Yes"], horizontal=True)

    divider_label("3 · Model")
    default_index = 0
    default_key = st.session_state.get("selected_model_key")
    if default_key:
        for idx, disp in enumerate(model_choices):
            if model_key_map.get(disp) == default_key:
                default_index = idx
                break
    model_choice = st.selectbox(
        "Which model(s) should run?",
        options=model_choices,
        index=default_index,
        help="Run the full ensemble for a consensus view, or a single model for a fast, specific answer.",
    )

    submitted = st.form_submit_button("Get my results →", type="primary", use_container_width=True)

if submitted:
    if answered < 10:
        st.warning("Please answer all 10 statements before submitting.")
    else:
        payload = {
            **scores,
            "age": float(age),
            "gender": "f" if gender == "Female" else "m",
            "ethnicity": ethnicity,
            "jaundice": "yes" if jaundice == "Yes" else "no",
            "austim": "yes" if austim == "Yes" else "no",
            "country_of_res": country,
            "used_app_before": "yes" if used_app_before == "Yes" else "no",
            "relation": relation,
        }
        try:
            with st.spinner("Running the models…"):
                if model_choice == "All models (consensus)":
                    response = predict_all(payload)
                else:
                    sel_key = model_key_map.get(model_choice, st.session_state.get("selected_model_key", "default"))
                    single = predict(payload, model=sel_key)
                    res = single["result"]
                    response = {
                        "results": [res],
                        "best_model_key": res.get("model_key"),
                        "aq10_total_score": single.get("aq10_total_score"),
                        "consensus_class": res.get("predicted_class"),
                        "agreement_ratio": 1.0,
                    }
        except ApiError as exc:
            kind_msg = {
                "timeout": "The backend took too long to respond.",
                "connection": "Couldn't connect to the backend API.",
                "http": "The backend rejected the request.",
            }.get(exc.kind, "Something went wrong.")
            notice(f"<b>Prediction failed.</b> {kind_msg} {exc.message}", kind="danger")
        else:
            entry = {
                "id": f"{datetime.now(timezone.utc).timestamp():.0f}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "input": payload,
                "response": response,
            }
            st.session_state[HISTORY_SESSION_KEY].append(entry)
            st.session_state["last_result"] = response
            if cfg.get("persist_history", True):
                try:
                    add_entry(payload, response, limit=cfg.get("history_limit", 200))
                except OSError:
                    pass

result = st.session_state.get("last_result")
if result:
    st.divider()
    st.subheader("Results")

    consensus = result["consensus_class"]
    agreement_pct = round(result["agreement_ratio"] * 100, 1)
    best_key = result["best_model_key"]
    best = next((r for r in result["results"] if r["model_key"] == best_key), result["results"][0])

    render_gauge(best["risk_percentage"])

    badge_color = "🔴" if consensus == "YES" else "🟢"
    st.markdown(
        f"### {badge_color} Consensus: **{'ASD traits likely' if consensus == 'YES' else 'ASD traits unlikely'}**"
    )
    st.markdown(
        pill(f"{agreement_pct}% agreement") + pill(f"AQ-10 score {result['aq10_total_score']}/10")
        + (pill(f"{best['model_name']} · {best['accuracy'] * 100:.1f}% acc") if best.get("accuracy") is not None else ""),
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="ns-recommend">{best["recommendation"]}</div>', unsafe_allow_html=True)

    if len(result["results"]) > 1:
        with st.expander("Compare all models", expanded=True):
            rows = []
            for r in result["results"]:
                accuracy = r.get("accuracy")
                rows.append(
                    {
                        "Model": r["model_name"],
                        "Prediction": r["predicted_class"],
                        "Accuracy": f"{accuracy * 100:.1f}%" if accuracy is not None else "—",
                        "Confidence": f"{r['confidence'] * 100:.1f}%",
                        "Risk %": r["risk_percentage"],
                        "Time (ms)": r["processing_time_ms"],
                    }
                )
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            chart_df = pd.DataFrame(rows).set_index("Model")[["Risk %"]]
            st.bar_chart(chart_df, use_container_width=True)

    st.caption(
        "This tool provides an initial screening indication only and is "
        "not a clinical diagnosis. Please consult a licensed professional "
        "for a formal evaluation."
    )

if st.session_state[HISTORY_SESSION_KEY]:
    st.divider()
    with st.expander(f"Past screenings this session ({len(st.session_state[HISTORY_SESSION_KEY])})"):
        for entry in reversed(st.session_state[HISTORY_SESSION_KEY][-10:]):
            resp = entry["response"]
            st.markdown(
                f"- **{entry['created_at'][:19].replace('T', ' ')} UTC** — "
                f"consensus **{resp['consensus_class']}**, "
                f"agreement {round(resp['agreement_ratio'] * 100)}%, "
                f"AQ-10 total {resp['aq10_total_score']}/10"
            )
        st.page_link("pages/4_History.py", label="Open full history →", icon="🕘")

footer()
