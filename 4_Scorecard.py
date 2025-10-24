# app/4_Scorecard.py
import streamlit as st
import pandas as pd
from app.utils import api_get

st.title("📋 Scorecard")
match_id = st.text_input("Enter Match ID")

if match_id:
    try:
        info = api_get("/match_info", {"id": match_id})
        st.subheader("Raw match info (for verification)")
        st.json(info)
        # Attempt to show innings batting/bowling if available
        payload = info.get("data", {})
        innings = payload.get("scorecard", []) or payload.get("innings", [])
        if not innings:
            st.info("Innings tables not provided by the current plan/endpoint.")
        else:
            for i, inn in enumerate(innings, 1):
                st.markdown(f"### Innings {i} — {inn.get('name','')}")
                bat = pd.DataFrame(inn.get("batting", []))
                bowl = pd.DataFrame(inn.get("bowling", []))
                if not bat.empty:
                    st.markdown("**Batting**")
                    st.dataframe(bat, use_container_width=True, hide_index=True)
                if not bowl.empty:
                    st.markdown("**Bowling**")
                    st.dataframe(bowl, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error fetching scorecard: {e}")
