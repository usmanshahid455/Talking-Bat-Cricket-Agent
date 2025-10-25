import streamlit as st, pandas as pd
from app.utils import api_get

def show_fixtures():
    st.subheader("📅 Fixtures (Upcoming)")
    try:
        data = api_get("/matches", {"offset": 0})
        rows = []
        for m in data.get("data", []):
            status = (m.get("status") or "").lower()
            if "not started" in status or "scheduled" in status or status in ("", "ns"):
                rows.append({
                    "Match ID": m.get("id"),
                    "Name": m.get("name"),
                    "Venue": m.get("venue"),
                    "Date": m.get("date"),
                    "Series": m.get("series"),
                    "Type": (m.get("matchType") or "").upper(),
                })
        df = pd.DataFrame(rows)
        if df.empty:
            st.info("No upcoming fixtures found.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"API Error: {e}")
