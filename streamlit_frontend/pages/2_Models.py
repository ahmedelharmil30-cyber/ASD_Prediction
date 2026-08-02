import pandas as pd
import streamlit as st

from lib.api import ApiError, cached_metadata, cached_metrics, cached_models
from lib.ui import footer, inject_base_style

inject_base_style()
st.title("Model performance")
st.caption("Cross-validated metrics for every trained model, computed once on a held-out test set.")

metadata = cached_metadata()
metrics = cached_metrics()
models_info = cached_models()

if not metadata or not metrics:
    st.error(
        "Could not load model metadata from the API. Make sure the "
        "backend is running and models have been trained "
        "(End_To_End.ipynb) and saved to the models/ folder."
    )
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Dataset size", f"{metadata['dataset_size']:,}")
    c2.metric("Training rows", f"{metadata['train_size']:,}")
    c3.metric("Test rows", f"{metadata['test_size']:,}")

    st.divider()
    st.subheader("Models")
    default_key = metadata.get("default_model")
    # allow the user to pick a model to highlight
    model_map = {k: v for k, v in metrics["models"].items()} if metrics and metrics.get("models") else {}
    highlight_display = None
    highlight_key = None
    if models_info and models_info.get("models"):
        display_to_key = {m["display_name"]: m["key"] for m in models_info["models"]}
        choice = st.selectbox("Highlight model", options=["(none)"] + list(display_to_key.keys()), index=0)
        if choice != "(none)":
            highlight_display = choice
            highlight_key = display_to_key[choice]
    rows = []
    for key, info in metrics["models"].items():
        m = info["metrics"]
        rows.append(
            {
                "Model": info["display_name"],
                "Default": "★" if key == default_key else "",
                "Accuracy": m.get("accuracy"),
                "Precision": m.get("precision"),
                "Recall": m.get("recall"),
                "F1 score": m.get("f1_score"),
                "CV F1": m.get("cv_f1"),
            }
        )
    df = pd.DataFrame(rows).sort_values("F1 score", ascending=False, na_position="last")
    styled = df.style.format(
        {c: "{:.3f}" for c in ["Accuracy", "Precision", "Recall", "F1 score", "CV F1"]},
        na_rep="—",
    )
    if highlight_display:
        # highlight the selected model row (by display name) or default star
        def _row_style(row):
            return [
                "background: rgba(124,58,237,0.12)" if (row["Default"] == "★" or row["Model"] == highlight_display) else ""
                for _ in row
            ]

        styled = styled.apply(_row_style, axis=1)

    st.dataframe(styled, use_container_width=True, hide_index=True)

    numeric_df = df.set_index("Model")[["Accuracy", "F1 score"]].dropna(how="all")
    if not numeric_df.empty:
        st.bar_chart(numeric_df)

    st.divider()
    st.subheader("Feature schema")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("**Numeric features**")
        st.write(metadata["numeric_features"])
    with fc2:
        st.markdown("**Categorical features**")
        st.write(metadata["categorical_features"])

    st.caption(f"Target column: `{metadata['target']}` · Generated: {metadata.get('generated_at', 'unknown')}")

footer()
