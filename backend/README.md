# ASD Prediction Platform — Backend

FastAPI backend serving predictions from four trained models (Logistic
Regression, Random Forest, SVM-RBF, KNN) plus a designated "best" model,
all loaded from the project's top-level `models/` folder.

## Folder structure

```
ASD_Prediction/
├── models/                        # trained .joblib artifacts (project root)
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py                # FastAPI app entrypoint
│       ├── config.py              # Settings (env vars)
│       ├── api/
│       │   └── routes.py          # all endpoints
│       ├── core/
│       │   └── model_loader.py    # ModelRegistry: loads & caches all models + metadata
│       ├── schemas/
│       │   └── prediction.py      # ASDInput + response models
│       ├── services/
│       │   └── predictor.py       # prediction logic (single + multi-model)
│       └── utils/
│           └── logger.py
```

## Setup

```powershell
cd "E:\ML project\ASD_Prediction\backend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Model files are expected at `ASD_Prediction\models\` (already present per
your project tree): `asd_model_logistic_regression.joblib`,
`asd_model_random_forest.joblib`, `asd_model_svm_rbf.joblib`,
`asd_model_knn.joblib`, `asd_best_model.joblib`, and
`asd_model_metadata.joblib`. If they live elsewhere, set `MODELS_DIR` in
`.env`.

## Run

**Always run this from the `backend/` folder** (the parent of `app/`) — this
is the fix for the `ModuleNotFoundError: No module named 'app'` you keep
hitting, which happens whenever `uvicorn app.main:app` is run from
`ASD_Prediction\` (the project root) instead of `ASD_Prediction\backend\`:

```powershell
cd "E:\ML project\ASD_Prediction\backend"
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Endpoints (no `/api/v1` prefix — matches `frontend/utils/api_client.py`)

- `GET /` — basic info
- `GET /health` — health check + how many models loaded
- `GET /models` — list of available models with metrics
- `GET /metadata` — dataset/feature metadata
- `GET /metrics` — per-model metrics
- `POST /predict?model=default` — single-model prediction
- `POST /predict/all` — run all models, return consensus

## Note on the earlier scaffold

An earlier response in this project mistakenly generated a generic scaffold,
and it got extracted on top of the real project — which overwrote the real
`config.py`, `main.py`, `requirements.txt`, and `.env.example` (identical
filenames). This zip restores those four files to match the real
`api/routes.py`, `core/model_loader.py`, `schemas/prediction.py`, and
`services/predictor.py` that survived the collision — everything else here
is untouched from your original code.
