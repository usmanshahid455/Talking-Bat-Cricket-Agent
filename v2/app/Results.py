import streamlit as st, pandas as pd
from utils import api_get

def show_results():
    st.subheader("✅ Recent Results")
    try:
        data = api_get("/matches", {"offset": 0})
        rows = []
        for m in data.get("data", []):
            status = (m.get("status") or "").lower()
            if any(word in status for word in ["won", "completed", "finished", "stumps", "result"]):
                rows.append({
                    "Match ID": m.get("id"),
                    "Name": m.get("name"),
                    "Venue": m.get("venue"),
                    "Date": m.get("date"),
                    "Series": m.get("series"),
                    "Type": (m.get("matchType") or "").upper(),
                    "Status": m.get("status"),
                })
        df = pd.DataFrame(rows)
        if df.empty:
            st.info("No recent results found.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"API Error: {e}")