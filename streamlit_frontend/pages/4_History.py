import math
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from lib.history import as_dataframe, clear_all, delete_entry, export_csv, load_entries
from lib.ui import divider_label, footer, inject_base_style, notice, pill, stat_card

inject_base_style()
st.title("Screening history")
st.caption("Every screening you've run is stored locally in data/history.json — nothing leaves this machine.")

entries = load_entries()

if not entries:
    notice(
        "No screenings yet. Run one from the <b>Screening</b> page and it will show up here.",
        kind="info",
    )
    st.page_link("pages/1_Screening.py", label="Go to Screening →", icon="📝")
else:
    df = as_dataframe()
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["date"] = df["timestamp_dt"].dt.date

    likely = int((df["consensus"] == "YES").sum())
    unlikely = int((df["consensus"] == "NO").sum())
    last_7d = int((df["timestamp_dt"] >= pd.Timestamp.now() - pd.Timedelta(days=7)).sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Total screenings", str(len(df)))
    with c2:
        stat_card("Flagged likely", str(likely))
    with c3:
        stat_card("Avg. AQ-10 score", f"{df['aq10_total'].mean():.1f}" if len(df) else "—")
    with c4:
        stat_card("Last 7 days", str(last_7d))

    # ---------------------------------------------------------------- Filters
    st.divider()
    divider_label("Filter")

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        consensus_filter = st.multiselect(
            "Consensus", options=sorted(df["consensus"].dropna().unique().tolist()), default=[]
        )
    with fc2:
        gender_filter = st.multiselect(
            "Gender", options=sorted(df["gender"].dropna().unique().tolist()), default=[]
        )
    with fc3:
        search = st.text_input("Search by country or model", value="")

    fc4, fc5, fc6 = st.columns(3)
    with fc4:
        min_age = int(df["age"].min()) if df["age"].notna().any() else 0
        max_age = int(df["age"].max()) if df["age"].notna().any() else 100
        if min_age >= max_age:
            max_age = min_age + 1
        age_range = st.slider("Age range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
    with fc5:
        min_score = int(df["aq10_total"].min()) if df["aq10_total"].notna().any() else 0
        max_score = int(df["aq10_total"].max()) if df["aq10_total"].notna().any() else 10
        if min_score >= max_score:
            max_score = min_score + 1
        score_range = st.slider("AQ-10 score range", min_value=min_score, max_value=max_score, value=(min_score, max_score))
    with fc6:
        valid_dates = df["date"].dropna()
        if len(valid_dates):
            min_d, max_d = valid_dates.min(), valid_dates.max()
        else:
            min_d = max_d = datetime.now().date()
        date_range = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    filtered = df.copy()
    if consensus_filter:
        filtered = filtered[filtered["consensus"].isin(consensus_filter)]
    if gender_filter:
        filtered = filtered[filtered["gender"].isin(gender_filter)]
    if search:
        s = search.lower()
        filtered = filtered[
            filtered["country"].astype(str).str.lower().str.contains(s)
            | filtered["best_model"].astype(str).str.lower().str.contains(s)
        ]
    filtered = filtered[
        (filtered["age"].isna() | filtered["age"].between(age_range[0], age_range[1]))
        & (filtered["aq10_total"].isna() | filtered["aq10_total"].between(score_range[0], score_range[1]))
    ]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
        filtered = filtered[
            filtered["date"].isna() | ((filtered["date"] >= start_d) & (filtered["date"] <= end_d))
        ]

    if st.button("↺ Reset filters"):
        st.rerun()

    # ---------------------------------------------------------------- Trends
    st.divider()
    divider_label("Trends")

    if len(filtered):
        tc1, tc2 = st.columns(2)
        with tc1:
            st.caption("Screenings per day")
            per_day = filtered.groupby("date").size().rename("count")
            st.bar_chart(per_day, use_container_width=True)
        with tc2:
            st.caption("Avg. AQ-10 score over time")
            avg_by_day = filtered.groupby("date")["aq10_total"].mean().rename("avg_score")
            st.line_chart(avg_by_day, use_container_width=True)

        tc3, tc4 = st.columns(2)
        with tc3:
            st.caption("Consensus breakdown")
            breakdown = filtered["consensus"].value_counts()
            st.bar_chart(breakdown, use_container_width=True)
        with tc4:
            st.caption("By country (top 8)")
            by_country = filtered["country"].value_counts().head(8)
            st.bar_chart(by_country, use_container_width=True)
    else:
        notice("No entries match the current filters.", kind="info")

    # ---------------------------------------------------------------- Table + pagination
    st.divider()
    divider_label(f"{len(filtered)} result(s)")

    sorted_filtered = filtered.sort_values("timestamp_dt", ascending=False).reset_index(drop=True)

    pc1, pc2 = st.columns([1, 3])
    with pc1:
        page_size = st.selectbox("Rows per page", options=[10, 25, 50, 100], index=1)

    total_rows = len(sorted_filtered)
    total_pages = max(1, math.ceil(total_rows / page_size))
    st.session_state.setdefault("history_page", 1)
    st.session_state["history_page"] = min(st.session_state["history_page"], total_pages)

    with pc2:
        st.session_state["history_page"] = st.number_input(
            f"Page (1–{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=st.session_state["history_page"],
            step=1,
        )

    page = st.session_state["history_page"]
    start = (page - 1) * page_size
    end = start + page_size
    page_df = sorted_filtered.iloc[start:end].drop(columns=["timestamp_dt", "date"])

    st.dataframe(page_df, use_container_width=True, hide_index=True)

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("← Previous", disabled=page <= 1, use_container_width=True):
            st.session_state["history_page"] = page - 1
            st.rerun()
    with nav2:
        st.markdown(f"<p style='text-align:center;color:var(--text-muted);'>Page {page} of {total_pages}</p>", unsafe_allow_html=True)
    with nav3:
        if st.button("Next →", disabled=page >= total_pages, use_container_width=True):
            st.session_state["history_page"] = page + 1
            st.rerun()

    st.download_button(
        "⬇ Export filtered as CSV",
        data=filtered.drop(columns=["timestamp_dt", "date"]).to_csv(index=False),
        file_name="screening_history_filtered.csv",
        mime="text/csv",
        use_container_width=False,
    )
    st.download_button(
        "⬇ Export all as CSV",
        data=export_csv(),
        file_name="screening_history.csv",
        mime="text/csv",
        use_container_width=False,
    )

    # ---------------------------------------------------------------- Entry detail
    st.divider()
    divider_label("Entry detail")
    ids = sorted_filtered["id"].tolist()
    if ids:
        chosen_id = st.selectbox("Select an entry", options=ids)
        entry = next((e for e in entries if e.get("id") == chosen_id), None)
        if entry:
            resp = entry["response"]
            best_key = resp.get("best_model_key")
            best = next((r for r in resp["results"] if r["model_key"] == best_key), resp["results"][0])
            st.markdown(
                pill(f"consensus {resp.get('consensus_class')}")
                + pill(f"AQ-10 {resp.get('aq10_total_score')}/10")
                + pill(f"{round(resp.get('agreement_ratio', 0) * 100)}% agreement"),
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="ns-recommend">{best.get("recommendation", "")}</div>', unsafe_allow_html=True)
            with st.expander("Raw input & response JSON"):
                st.json(entry)
            if st.button("🗑 Delete this entry", key=f"del_{chosen_id}"):
                delete_entry(chosen_id)
                st.rerun()

    st.divider()
    with st.expander("Danger zone"):
        st.warning("This permanently deletes all locally stored screening history.")
        confirm = st.checkbox("I understand this cannot be undone")
        if st.button("Clear all history", type="primary", disabled=not confirm):
            clear_all()
            st.success("History cleared.")
            st.rerun()

footer()
