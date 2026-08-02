from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from lib.api import ApiError, cached_metadata, predict_all, predict, cached_models
from lib.constants import AQ10_ITEMS_FALLBACK, COUNTRIES, ETHNICITIES, HISTORY_SESSION_KEY, RELATIONS
from lib.ui import footer, inject_base_style, render_gauge

inject_base_style()
st.title("AQ-10 Screening")
st.caption("Answer honestly — there are no right or wrong answers.")

if HISTORY_SESSION_KEY not in st.session_state:
    st.session_state[HISTORY_SESSION_KEY] = []

meta = cached_metadata()
aq10_items = meta["aq10_items"] if meta and meta.get("aq10_items") else AQ10_ITEMS_FALLBACK

with st.form("screening_form"):
    st.subheader("1. AQ-10 statements")
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

    st.subheader("2. About you")
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

    submitted = st.form_submit_button("Get my results →", type="primary", use_container_width=True)

    # model choice inside the form: either run all models or a single selected model
    models_info = cached_models()
    model_choices = ["All models"]
    model_key_map = {}
    if models_info and models_info.get("models"):
        for m in models_info["models"]:
            model_choices.append(m["display_name"])
            model_key_map[m["display_name"]] = m["key"]
    model_choice = st.selectbox("Run", options=model_choices, index=0, help="Choose a specific model or run all models")

if submitted:
    if any(v is None for v in scores.values()) or not all(
        f"a{i}" in st.session_state and st.session_state[f"a{i}"] is not None for i in range(1, 11)
    ):
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
                if model_choice == "All models":
                    response = predict_all(payload)
                else:
                    # run a single selected model and normalize response to the multi-model shape
                    sel_key = model_key_map.get(model_choice, st.session_state.get("selected_model_key", "default"))
                    single = predict(payload, model=sel_key)
                    # single: {"result": PredictionResult, "aq10_total_score": int}
                    res = single["result"]
                    response = {
                        "results": [res],
                        "best_model_key": res.get("model_key"),
                        "aq10_total_score": single.get("aq10_total_score"),
                        "consensus_class": res.get("predicted_class"),
                        "agreement_ratio": 1.0,
                    }
        except ApiError as exc:
            st.error(f"Prediction failed: {exc.message}")
        else:
            st.session_state[HISTORY_SESSION_KEY].append(
                {
                    "id": f"{datetime.now(timezone.utc).timestamp():.0f}",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "input": payload,
                    "response": response,
                }
            )
            st.session_state["last_result"] = response

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
    st.caption(f"{agreement_pct}% of models agree · AQ-10 total score: {result['aq10_total_score']}/10")
    if best.get("accuracy") is not None:
        st.caption(f"Best model ({best['model_name']}) accuracy: {best['accuracy'] * 100:.1f}%")

    st.markdown(f'<div class="asd-recommend">{best["recommendation"]}</div>', unsafe_allow_html=True)

    with st.expander("Compare all models"):
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

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

footer()
