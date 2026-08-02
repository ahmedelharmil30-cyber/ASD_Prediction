# ASD Prediction

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-%3E%3D0.70-brightgreen.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/streamlit-%3E%3D1.0-orange.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This project provides an end-to-end autism screening demo built around the AQ-10 questionnaire. It combines a machine learning workflow in a Jupyter notebook, a FastAPI backend for serving predictions, and a Streamlit frontend for an interactive user experience.

> This repository is intended for education and prototyping. It is not a medical diagnostic system.

## Features

- Train and evaluate multiple ASD prediction models in the notebook
- Serve predictions through a FastAPI API
- Explore models and results through a Streamlit web app
- Expose model metadata and metrics endpoints for easier inspection

## Project Structure

```text
ASD_Prediction/
├── End_To_End.ipynb           # training and model development
├── backend/                   # FastAPI application
├── streamlit_frontend/        # Streamlit user interface
├── models/                    # trained model artifacts
├── datasets/                  # CSV and ARFF datasets
└── LICENSE
```

## Quick Start (Windows)

### 1. Clone the repository

```powershell
git clone <your-repository-url>
cd ASD_Prediction
```

### 2. Start the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
if exist .env.example copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

The API documentation will be available at:

- http://localhost:8000/docs

### 3. Start the frontend

Open a second terminal and run:

```powershell
cd streamlit_frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:API_URL = "http://localhost:8000"
streamlit run Home.py
```

Then open:

- http://localhost:8501

## Training the Models

Open the notebook in [End_To_End.ipynb](End_To_End.ipynb) to train or retrain the models. The generated model files should be placed in the [models](models) directory so the backend can load them.

## API Overview

The backend exposes endpoints such as:

- `GET /health` for health checks
- `GET /models` for available models
- `GET /metadata` for feature and dataset information
- `POST /predict` for single-model prediction
- `POST /predict/all` for multi-model prediction

## Troubleshooting

- If you see a `ModuleNotFoundError` for `app`, run the backend from the [backend](backend) folder.
- If the Streamlit app cannot reach the API, make sure the backend is running and that `API_URL` points to `http://localhost:8000`.
- If the model files are missing, verify that the `.joblib` files are present in [models](models).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
