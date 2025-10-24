# app/3_Results.py
import streamlit as st
import pandas as pd
from app.utils import api_get

st.title("✅ Recent Results")

try:
    data = api_get("/matches", {"offset": 0})
    rows = []
    for m in data.get("data", []):
        status = (m.get("status") or "").lower()
        if status.startswith(("completed", "won", "finished")) or "stumps" in status or "result" in status:
            rows.append({
                "Match ID": m.get("id"),
                "Name": m.get("name"),
                "Type": (m.get("matchType") or "").upper(),
                "Venue": m.get("venue"),
                "Date": m.get("date"),
                "Series": m.get("series"),
                "Status": m.get("status"),
            })
    df = pd.DataFrame(rows)
    if df.empty:
        st.write("No recent results found.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"API error: {e}")
