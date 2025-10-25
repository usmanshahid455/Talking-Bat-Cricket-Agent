import streamlit as st, pandas as pd
from utils import api_get

def show_live():
    st.subheader("🔴 Live Matches")
    try:
        data = api_get("/currentMatches", {"offset": 0})
        matches = data.get("data", [])
        if not matches:
            st.info("No live matches right now.")
            return
        rows = []
        for m in matches:
            tinfo = m.get("teamInfo", [{}, {}])
            rows.append({
                "Match ID": m.get("id"),
                "Teams": f"{tinfo[0].get('name','?')} vs {tinfo[1].get('name','?')}",
                "Status": m.get("status"),
                "Venue": m.get("venue"),
                "Type": (m.get("matchType") or "").upper(),
                "Series": m.get("series"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"API Error: {e}")