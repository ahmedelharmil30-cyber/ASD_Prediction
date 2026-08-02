import streamlit as st

from lib.api import clear_session_cache, cached_models, recent_calls, test_connection
from lib.config import ACCENTS, DEFAULTS, load_config, reset_config, save_config
from lib.history import clear_all as clear_history
from lib.history import load_entries
from lib.ui import divider_label, footer, inject_base_style, notice, pill

inject_base_style()
st.title("Settings")
st.caption("Configure how this app talks to the backend, which model runs by default, and how history is kept.")

cfg = load_config()

tab_conn, tab_models, tab_history, tab_appearance, tab_diag = st.tabs(
    ["Connection", "Models", "History", "Appearance", "Diagnostics"]
)

# ------------------------------------------------------------- Connection
with tab_conn:
    divider_label("Backend API")
    with st.form("conn_form"):
        api_url = st.text_input("API URL", value=cfg["api_url"], help="Base URL of the FastAPI backend, e.g. http://localhost:8000")
        c1, c2, c3 = st.columns(3)
        with c1:
            timeout = st.number_input("Request timeout (s)", min_value=1.0, max_value=120.0, value=float(cfg["request_timeout"]), step=1.0)
        with c2:
            retries = st.number_input("Max retries", min_value=0, max_value=10, value=int(cfg["max_retries"]), step=1)
        with c3:
            backoff = st.number_input("Backoff factor", min_value=0.0, max_value=5.0, value=float(cfg["backoff_factor"]), step=0.1)
        saved = st.form_submit_button("Save connection settings", type="primary", use_container_width=True)

    if saved:
        cfg.update(api_url=api_url.rstrip("/"), request_timeout=timeout, max_retries=retries, backoff_factor=backoff)
        save_config(cfg)
        clear_session_cache()
        st.success("Saved. Caches cleared so the new settings take effect immediately.")
        st.rerun()

    st.divider()
    if st.button("Test connection now"):
        with st.spinner("Pinging the backend…"):
            result = test_connection()
        if result["ok"]:
            notice(f"Connected in {result['latency_ms']} ms.", kind="success")
            with st.expander("Response"):
                st.json(result.get("data", {}))
        else:
            notice(f"<b>{result['kind'] or 'error'}</b> — {result['message']}", kind="danger")

# ------------------------------------------------------------------ Models
with tab_models:
    divider_label("Default model")
    models_info = cached_models()
    if models_info and models_info.get("models"):
        display_to_key = {m["display_name"]: m["key"] for m in models_info["models"]}
        key_to_display = {v: k for k, v in display_to_key.items()}
        current_display = key_to_display.get(cfg.get("default_model_key"), list(display_to_key.keys())[0])
        chosen = st.selectbox(
            "Model used when 'single model' mode is selected on the Screening page",
            options=list(display_to_key.keys()),
            index=list(display_to_key.keys()).index(current_display),
        )
        run_mode = st.radio(
            "Default run mode on the Screening page",
            options=["all", "single"],
            format_func=lambda v: "Run all models (consensus)" if v == "all" else "Run one model only",
            index=0 if cfg.get("run_mode", "all") == "all" else 1,
            horizontal=True,
        )
        if st.button("Save model preferences", type="primary"):
            cfg.update(default_model_key=display_to_key[chosen], run_mode=run_mode)
            save_config(cfg)
            st.success("Saved.")
            st.rerun()

        st.divider()
        divider_label("Available models")
        for m in models_info["models"]:
            st.markdown(
                f'<div class="ns-card"><b>{m["display_name"]}</b> '
                + pill(m["key"])
                + (pill("default") if m["key"] == cfg.get("default_model_key") else "")
                + "</div>",
                unsafe_allow_html=True,
            )
    else:
        notice("Could not load the model list from the backend — check the Connection tab.", kind="warning")

# ----------------------------------------------------------------- History
with tab_history:
    divider_label("Local history storage")
    persist = st.toggle("Save every screening to disk (data/history.json)", value=cfg.get("persist_history", True))
    limit = st.slider("Keep at most N recent screenings", min_value=10, max_value=1000, value=int(cfg.get("history_limit", 200)), step=10)
    if st.button("Save history preferences", type="primary"):
        cfg.update(persist_history=persist, history_limit=limit)
        save_config(cfg)
        st.success("Saved.")

    st.divider()
    entries = load_entries()
    st.caption(f"Currently storing {len(entries)} screening(s) on disk.")
    with st.expander("Danger zone"):
        confirm = st.checkbox("I understand this permanently deletes all local history")
        if st.button("Clear all history now", disabled=not confirm):
            clear_history()
            st.success("History cleared.")
            st.rerun()

# -------------------------------------------------------------- Appearance
with tab_appearance:
    divider_label("Accent color")
    accent_choice = st.radio(
        "Pick an accent used across gauges, badges, and buttons",
        options=list(ACCENTS.keys()),
        format_func=lambda k: k.capitalize(),
        index=list(ACCENTS.keys()).index(cfg.get("accent", "teal")),
        horizontal=True,
    )
    swatches = "".join(
        f'<span style="display:inline-block;width:22px;height:22px;border-radius:6px;'
        f'background:{v["primary"]};margin-right:8px;vertical-align:middle;'
        f'border:2px solid {"#fff" if k == accent_choice else "transparent"};"></span>'
        for k, v in ACCENTS.items()
    )
    st.markdown(swatches, unsafe_allow_html=True)

    if st.button("Apply accent color", type="primary"):
        cfg.update(accent=accent_choice)
        save_config(cfg)
        st.success("Applied.")
        st.rerun()

    st.divider()
    if st.button("Reset all settings to defaults"):
        reset_config()
        clear_session_cache()
        st.success("Reset to defaults.")
        st.rerun()

# --------------------------------------------------------------- Diagnostics
with tab_diag:
    divider_label("Recent API calls (this session)")
    calls = list(reversed(recent_calls()))
    if not calls:
        st.caption("No API calls made yet this session.")
    else:
        import pandas as pd

        st.dataframe(pd.DataFrame(calls), use_container_width=True, hide_index=True)

    st.divider()
    divider_label("Current configuration")
    st.json({k: cfg.get(k, v) for k, v in DEFAULTS.items()})

footer()
