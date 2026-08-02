
# 🧩 ASD Prediction — FastAQ (Streamlit + FastAPI)

![Build](https://img.shields.io/badge/build-local-green) ![Python](https://img.shields.io/badge/python-3.11-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

FastAQ is a compact, professional-feeling research demo for exploratory autism screening using the AQ‑10 questionnaire and multiple ML models. Designed for clarity and reproducibility: train in the notebook, serve with FastAPI, and explore with Streamlit.

Demo
![demo](docs/demo-placeholder.gif)

**What's inside**
- **End-to-end**: data → notebook training → saved `joblib` models → FastAPI → Streamlit UI
- **Multiple models**: compare Logistic Regression, Random Forest, SVM (RBF), and Decision Tree
- **Observability**: endpoints expose metadata and per-model metrics for reproducible comparison

**Why use this**
- Rapid local prototyping of feature and model ideas
- Clear separation of concerns so you can swap preprocessing, models, or UI independently
- Great for teaching ML model lifecycle and deployment basics

**Repository at a glance**
- `backend/` — FastAPI app (model loading, `/predict`, `/models`, `/metadata`, `/metrics`)
- `streamlit_frontend/` — interactive UI to run/compare models and view results
- `models/` — serialized model artifacts and metadata
- `End_To_End.ipynb` — training & evaluation notebook

**Architecture (high level)**

```mermaid
flowchart LR
	A[Datasets (CSV/arff)] --> B[End_To_End.ipynb]\n
	B --> C[Trained models (joblib) in /models]\n+  C --> D[FastAPI backend]\n+  D --> E[Streamlit frontend]\n+  E -->|calls| D
```

Quick start — Backend (Windows)
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to exercise the API.

Quick start — Frontend (Streamlit)
```powershell
cd streamlit_frontend
pip install -r requirements.txt
streamlit run Home.py
```

Open the Streamlit URL (usually `http://localhost:8501`) and use the sidebar to choose a model.

Configuration
- API base URL is configured via `API_URL` environment variable in the Streamlit frontend. Default: `http://localhost:8000`.

API endpoints
- `GET /health` — service health and models loaded
- `GET /models` — list models with display names and metric summary
- `GET /metadata` — feature lists, AQ‑10 questions, dataset sizes
- `GET /metrics` — per-model metrics (accuracy, f1, precision, recall)
- `POST /predict?model=<key>` — single-model prediction
- `POST /predict/all` — multi-model consensus prediction

Usage examples
- Run the Streamlit UI and submit the AQ‑10 form to compare all models or run a specific one via the new model selector.

Contributing
- Keep PRs small and focused. Add tests if you change backend logic. Update `requirements.txt` when adding packages.

Notes & next improvements
- Add CI (GitHub Actions) to run lint/tests — happy to add a starter workflow
- Add visual demo GIF and smaller screenshots under `docs/` for the README hero
- Optionally add a Vercel/Render deploy button if you want hosted demos

License
- See [LICENSE](LICENSE) for license details.

If you'd like, I can now:
- add CI badges and a GitHub Actions workflow, or
- add polished screenshots/GIF and update the `docs/` folder.

