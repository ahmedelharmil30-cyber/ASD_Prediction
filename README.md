# 🧩 ASD Prediction — FastAQ (Streamlit + FastAPI)

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-%3E%3D1.0-orange.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/fastapi-%3E%3D0.70-brightgreen.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A compact, research-oriented end-to-end autism-screening demo built around the AQ‑10 questionnaire. Train models in the provided notebook, serve them via a FastAPI backend, and explore predictions interactively with a Streamlit frontend.

This repository is intended for education and prototyping — it is not a medical diagnostic system.

Why this repo is "pro"
- Clear separation: training notebook, model artifacts, API server, and interactive UI
- Reproducible model metadata + metrics API for easy CI/validation
- Lightweight, dependency-minimal Streamlit UI you can extend quickly

Quick Links
- Training notebook: `End_To_End.ipynb`
- Models folder: `models/`
- Backend API: `backend/app/` (FastAPI)
- Streamlit UI: `streamlit_frontend/`

Pro Quick Start (Windows) — Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Verify the API at http://localhost:8000/docs

Pro Quick Start — Streamlit UI

```powershell
cd streamlit_frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

Open the Streamlit local URL (typically http://localhost:8501). The sidebar now exposes a professional model chooser and persistent selection during the session.

Core Features
- Multi-model predictions (single or ensemble) with a normalized API response
- Model metadata & per-model metrics endpoints (`/models`, `/metrics`, `/metadata`)
- Streamlit UI with selectable models, a polished results card and comparison table

Architecture (high level)

```mermaid
flowchart LR
	subgraph Train
		N[End_To_End.ipynb]\n(Notebook)
		N --> M[models/*.joblib]\n  end
	subgraph Serve
		M --> API[FastAPI backend]\n+    API -->|/predict| P[Prediction service]
		API -->|/models,/metrics| Meta[Metadata service]
	end
	subgraph UI
		S[Streamlit frontend] --> API
		Browser --> S
	end
	Browser --> API
```

Configuration
- `backend/.env.example`: backend settings (port, debug, allowed origins)
- `streamlit_frontend/.env` or environment variables: `API_URL` (defaults to `http://localhost:8000`)

Best Practices
- Keep `models/*.joblib` alongside `metadata.joblib` produced by training to ensure the API can load metrics and display names.
- For reproducible experiments, tag the training run that produced each `.joblib` (the training notebook stores `model_version` metadata).

Contributing
- Add a short PR describing the proposed change and any dataset or model updates.
- Run the training notebook and include a new `models/*.joblib` only if the model is small; otherwise provide steps to reproduce.

Want continuous checks?
- Add a GitHub Action that runs a lightweight smoke test: start the backend, call `/health`, call `/models`, and assert JSON shapes.

License
- MIT — see `LICENSE`.

Contact
- This is an educational demo. For collaboration or questions open an issue.
