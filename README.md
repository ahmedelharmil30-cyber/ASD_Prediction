# 🧠 ASD Screening Platform

A polished end-to-end autism screening platform built on the AQ-10 questionnaire and four machine learning models: Logistic Regression, Random Forest, SVM (RBF), and KNN.

> ⚠️ This project is a research and education tool, not a medical diagnostic system. Results should always be reviewed by a qualified healthcare professional.

---

## 📁 Project Structure

```text
ASD_Prediction/
├── backend/                       # FastAPI backend serving model APIs
│   ├── app/
│   │   ├── api/routes.py          # /health /models /metadata /metrics /predict /predict/all
│   │   ├── core/model_loader.py   # model loader and metadata normalization
│   │   ├── services/predictor.py  # prediction logic
│   │   ├── schemas/prediction.py  # Pydantic request/response models
│   │   ├── config.py              # env-driven settings
│   │   └── main.py                # application entrypoint
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                      # Next.js 14 + TypeScript + Tailwind CSS
│   ├── app/
│   │   ├── page.tsx               # homepage
│   │   ├── screening/page.tsx     # AQ-10 questionnaire + results
│   │   ├── models/page.tsx        # model comparison
│   │   └── about/page.tsx         # project overview
│   ├── components/                # UI components
│   ├── lib/                       # api client, types, constants
│   ├── package.json
│   └── .env.example
│
├── frontend-streamlit-legacy/     # legacy Streamlit interface (archived)
├── models/                        # trained joblib model files + metadata
├── datasets/                      # raw input datasets
├── processed/                     # cleaned, processed dataset output
├── End_To_End.ipynb               # original training notebook
├── PROJECT_PLAN.md                # project plan and execution roadmap
└── README.md                      # this file
```

---

## 🚀 Running Locally (No Docker)

### Backend

```bash
cd backend
python -m venv .venv
# macOS/Linux
type .venv/bin/activate
# Windows
# .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` to verify the backend API documentation.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
# ensure NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Then open `http://localhost:3000`.

> The trained models already exist under `models/*.joblib`, so you do not need to retrain the platform unless you want to refresh the model pipeline with new data.

---

## 🧪 Docker Removed

Docker support has been removed from this repository. Please run the backend and frontend locally using the commands above.

If you previously relied on Docker, use a Python virtual environment for the backend and `npm` for the frontend.

---

## 📤 Publish to GitHub

```bash
cd ASD_Prediction
git init
git add .
git commit -m "Initial commit: ASD screening platform (FastAPI + Next.js)"
git branch -M main
git remote add origin https://github.com/<username>/<repo-name>.git
git push -u origin main
```

> `.env`, `node_modules/`, and `.next/` are already excluded in `.gitignore`.
> The `models/*.joblib` files are included and are under ~18MB total, so Git LFS is not required.

---

## ☁️ Deployment Guidance

This repository is best deployed as two separate pieces:

- **Frontend:** deploy the Next.js app on Vercel or any static/React hosting provider.
- **Backend:** deploy the FastAPI service on a Python-capable host such as Railway, Render, Fly.io, or a dedicated VM.

### Frontend → Vercel

1. Push the repo to GitHub.
2. Create a new Vercel project and connect the repo.
3. Set the project root to `frontend`.
4. Add `NEXT_PUBLIC_API_URL` pointing to the published backend URL.
5. Deploy.

### Backend → Python host

Use a standard FastAPI deployment approach:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> Do not deploy the backend as a serverless function unless you are comfortable with loading models at cold start.

### CORS Reminder

Make sure the deployed frontend origin is included in `ALLOWED_ORIGINS` on the backend, otherwise browser requests will be blocked.

---

## 🔌 Backend API Endpoints

| Method | Endpoint       | Description                                                           |
|--------|----------------|-----------------------------------------------------------------------|
| GET    | `/health`      | Check service health and model availability                           |
| GET    | `/models`      | List available models and their metrics                               |
| GET    | `/metadata`    | Feature metadata, AQ-10 questions, and dataset details                |
| GET    | `/metrics`     | Performance metrics for each model                                    |
| POST   | `/predict`     | Predict using one model (`?model=default` or model key)              |
| POST   | `/predict/all` | Predict with all models and return consensus + agreement score        |

Interactive Swagger docs are available at `/docs` when the backend is running.

---

## 📊 Data Note

This repository ships with sample AQ-10-style data covering Adult, Adolescent, and Child samples. All four models are trained on this available dataset.

If you have your own dataset with a matching schema, place it in `datasets/` and rerun `End_To_End.ipynb` to retrain the models.

---

## 🛠 Troubleshooting

- **Cannot reach the API server:** confirm the backend is running on the port configured in `NEXT_PUBLIC_API_URL`, and verify CORS includes the frontend origin.
- **`ModuleNotFoundError: No module named 'imblearn'`:** install dependencies from `backend/requirements.txt`. The saved models require `imbalanced-learn` because they are stored as `imblearn.pipeline.Pipeline` objects.
- **Frontend still points to old API URL:** `NEXT_PUBLIC_*` env vars are baked into the build, so rebuild/redeploy after updating them.

---

## 📄 License

See [LICENSE](./LICENSE).
