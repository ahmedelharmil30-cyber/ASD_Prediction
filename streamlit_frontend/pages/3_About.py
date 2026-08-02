import streamlit as st

from lib.api import cached_models
from lib.ui import footer, inject_base_style

inject_base_style()
st.title("About this project")

models = cached_models()
model_names = [m["display_name"] for m in models["models"]] if models and models.get("models") else [
    "Logistic Regression", "Random Forest", "SVM (RBF)", "Decision Tree",
]

st.markdown(
    "This platform is a complete (backend + frontend) initial-screening tool "
    "for autism spectrum disorder (ASD) indicators, based on the short "
    "**AQ-10** questionnaire, built on top of several machine learning models:"
)
st.markdown(f"**{', '.join(model_names)}**.")

with st.container(border=True):
    st.markdown("#### Technical stack")
    st.markdown(
        """
- **Backend:** FastAPI + scikit-learn, serving `/predict`, `/predict/all`, `/models`, `/metadata`, and `/metrics`.
- **Frontend:** Streamlit, talking to the backend over HTTP through a pooled session with automatic retries and backoff.
- **Configuration:** editable at runtime on the **Settings** page — API URL, timeout, retry policy, default model, and accent color — persisted locally in `data/config.json`.
- **History:** every screening is saved to `data/history.json` on disk (in addition to the current browser session), viewable and exportable on the **History** page.
- **Deployment:** Streamlit Community Cloud (or any host) for the frontend, with the backend hosted separately as a standard FastAPI deployment.
"""
    )

with st.container(border=True):
    st.markdown("#### Ethical & medical notice")
    st.markdown(
        """
This tool is a **screening aid**, not a diagnostic instrument. A "likely"
result does not mean a person has autism, and an "unlikely" result does
not rule it out. Only a licensed clinical psychologist, psychiatrist, or
developmental pediatrician can provide a formal diagnosis. If you have
concerns about yourself or someone you care for, please reach out to a
qualified healthcare professional.
"""
    )

with st.container(border=True):
    st.markdown("#### Data & training")
    st.markdown(
        """
Models are trained in `End_To_End.ipynb` on combined AQ-10 screening
datasets spanning toddlers through adults, with careful attention to
avoiding data leakage (grouped train/test splits, SMOTE applied only to
training folds, and regularization-heavy hyperparameter grids to keep
reported accuracy honest rather than inflated by memorization).
"""
    )

with st.container(border=True):
    st.markdown("#### Privacy")
    st.markdown(
        """
Screening answers never leave your machine except as a request to the
backend API you configured. History is stored locally on disk next to
this app — nothing is uploaded to a third party. You can clear it any
time from the **History** or **Settings** page.
"""
    )

footer()
