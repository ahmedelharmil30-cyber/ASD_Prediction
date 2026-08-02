# ASD Prediction Platform — Streamlit frontend

This replaces the old Next.js frontend. It talks to the **same, unmodified
FastAPI backend** (`backend/`) over HTTP — no backend changes are needed.

## Setup

```bash
cd streamlit_frontend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` (or just set the environment variable
directly) and point it at your running backend:

```bash
cp .env.example .env
# API_URL=http://localhost:8000
```

## Run

Start the backend first (from `backend/`):

```bash
uvicorn app.main:app --reload --port 8000
```

Then, in another terminal, start the Streamlit app:

```bash
cd streamlit_frontend
set -a && source .env && set +a   # loads API_URL into the shell (Linux/macOS)
streamlit run Home.py
```

On Windows (CMD), set the variable directly instead of sourcing `.env`:

```bat
set API_URL=http://localhost:8000
streamlit run Home.py
```

The app opens at `http://localhost:8501` by default.

## Structure

```
streamlit_frontend/
├── Home.py                  # landing page
├── pages/
│   ├── 1_Screening.py       # AQ-10 form + demographics + results
│   ├── 2_Models.py          # per-model metrics / comparison
│   └── 3_About.py           # project info
├── lib/
│   ├── api.py                # HTTP client for the FastAPI backend
│   ├── constants.py          # AQ-10 items / dropdown options (fallback)
│   └── ui.py                  # shared styling + gauge widget
├── .streamlit/config.toml    # theme
└── requirements.txt
```

## Notes

- Screening history is kept in `st.session_state` for the current browser
  session only — nothing is persisted server-side, same as the old
  frontend's localStorage-based history.
- `GET /metadata` is used to fetch the live AQ-10 question text and
  dataset stats; `lib/constants.py` is only a fallback if that call fails.
- If `/health` shows the API as unreachable in the sidebar, start the
  backend first and refresh.
