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
    likely = int((df["consensus"] == "YES").sum())
    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Total screenings", str(len(df)))
    with c2:
        stat_card("Flagged likely", str(likely))
    with c3:
        stat_card("Avg. AQ-10 score", f"{df['aq10_total'].mean():.1f}" if len(df) else "—")

    st.divider()
    divider_label("Filter")
    fc1, fc2 = st.columns(2)
    with fc1:
        consensus_filter = st.multiselect(
            "Consensus", options=sorted(df["consensus"].dropna().unique().tolist()), default=[]
        )
    with fc2:
        search = st.text_input("Search by country or model", value="")

    filtered = df.copy()
    if consensus_filter:
        filtered = filtered[filtered["consensus"].isin(consensus_filter)]
    if search:
        s = search.lower()
        filtered = filtered[
            filtered["country"].astype(str).str.lower().str.contains(s)
            | filtered["best_model"].astype(str).str.lower().str.contains(s)
        ]

    st.divider()
    divider_label(f"{len(filtered)} result(s)")
    st.dataframe(
        filtered.sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Export as CSV",
        data=export_csv(),
        file_name="screening_history.csv",
        mime="text/csv",
        use_container_width=False,
    )

    st.divider()
    divider_label("Entry detail")
    ids = filtered.sort_values("timestamp", ascending=False)["id"].tolist()
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
