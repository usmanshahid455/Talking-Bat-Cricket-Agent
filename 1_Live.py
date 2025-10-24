# app/1_Live.py
import streamlit as st
import pandas as pd
from app.utils import api_get, auto_refresh

st.title("🔴 Live Matches")
auto_refresh()

try:
    data = api_get("/currentMatches", {"offset": 0})
    matches = data.get("data", [])
    if not matches:
        st.write("No live matches at the moment.")
    else:
        rows = []
        for m in matches:
            ti = m.get("teamInfo", [{}, {}])
            teamA = ti[0].get("name", "TBD")
            teamB = ti[1].get("name", "TBD")
            rows.append({
                "Match ID": m.get("id"),
                "Series": m.get("series"),
                "Type": (m.get("matchType") or "").upper(),
                "Teams": f"{teamA} vs {teamB}",
                "Status": m.get("status", ""),
                "Venue": m.get("venue", ""),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("Click 'Scorecard' page and paste a Match ID to open details.")
except Exception as e:
    st.error(f"API error: {e}")
