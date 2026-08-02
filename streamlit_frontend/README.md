# NeuroSignal — ASD Prediction Platform (Streamlit frontend)

An advanced Streamlit dashboard for the AQ-10 ASD screening tool. It talks
to the **same, unmodified FastAPI backend** (`backend/`) over HTTP — no
backend changes are needed.

## What's new in this version

- **Redesigned UI** — a distinct clinical-tech dashboard theme (Space
  Grotesk / Inter / JetBrains Mono type system, glass cards, glowing
  gauge, live status pill), consistent across every page.
- **Configuration page (Settings)** — edit the API URL, request timeout,
  retry/backoff policy, default model, history retention, and accent
  color at runtime. Settings persist to `data/config.json`, so you don't
  need to restart the app or edit `.env` to change them.
- **Hardened backend client** (`lib/api.py`) — a pooled `requests.Session`
  with automatic retries + exponential backoff on transient failures
  (connection resets, 502/503/504), classified errors (timeout /
  connection / http), and a live request log surfaced on the Settings →
  Diagnostics tab.
- **Model chooser** — run the full ensemble for a consensus view, or pick
  one specific model, from both the Screening page and Settings.
- **Persistent history** — every screening is saved to `data/history.json`
  on disk (not just the browser session), with a dedicated History page:
  filter, inspect raw request/response JSON, export to CSV, delete
  individual entries, or clear everything.
- **Connection diagnostics** — a one-click "Test connection" button and a
  rolling log of recent API calls with status + latency.

## Setup

```bash
cd streamlit_frontend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` (or just set the environment variables
directly) for first-run defaults — everything here can also be changed
later from the in-app **Settings** page:

```bash
cp .env.example .env
```

## Run

Start the backend first (from `backend/`):

```bash
uvicorn app.main:app --reload --port 8000
```

Then, in another terminal, start the Streamlit app:

```bash
cd streamlit_frontend
set -a && source .env && set +a   # loads env vars into the shell (Linux/macOS)
streamlit run Home.py
```

On Windows (CMD), set the variable directly instead of sourcing `.env`:

```bat
set API_URL=http://localhost:8000
streamlit run Home.py
```

The app opens at `http://localhost:8501` by default. If the API URL
changes later (different host, different port), just update it on the
**Settings → Connection** tab — no restart needed.

## Structure

```
streamlit_frontend/
├── Home.py                    # dashboard landing page
├── pages/
│   ├── 1_Screening.py         # AQ-10 form + demographics + model choice + results
│   ├── 2_Models.py            # per-model metrics / leaderboard
│   ├── 3_About.py             # project info
│   ├── 4_History.py           # persistent screening history, filters, export
│   └── 5_Settings.py          # connection, models, history, appearance, diagnostics
├── lib/
│   ├── api.py                 # HTTP client: retries, timeouts, error classes, call log
│   ├── config.py              # persisted app configuration (data/config.json)
│   ├── history.py             # persisted screening history (data/history.json)
│   ├── constants.py           # AQ-10 items / dropdown options (fallback)
│   └── ui.py                  # design system: theme injection + shared components
├── data/                      # created at runtime — config.json, history.json (gitignored)
├── .streamlit/config.toml     # Streamlit theme
├── .env.example                # first-run defaults (optional; Settings page overrides)
└── requirements.txt
```

## Notes

- No screening data is sent anywhere except the FastAPI backend you point
  this app at. Persisted history and config live only in `data/` next to
  this app.
- This tool provides an initial screening indication only and is **not**
  a clinical diagnosis.
