import streamlit as st, pandas as pd
from app.utils import api_get

def show_scorecard():
    st.subheader("📋 Scorecard")
    match_id = st.text_input("Enter Match ID")
    if not match_id:
        st.info("Type a Match ID from the Live or Fixtures page.")
        return
    try:
        data = api_get("/match_info", {"id": match_id})
        payload = data.get("data", {})
        innings = payload.get("scorecard", []) or payload.get("innings", [])
        if not innings:
            st.warning("No detailed scorecard available for this match (plan/endpoint may limit).")
            return
        for i, inn in enumerate(innings, 1):
            st.markdown(f"### Innings {i}: {inn.get('name','')}")
            if 'batting' in inn:
                st.markdown("**Batting**")
                st.dataframe(pd.DataFrame(inn['batting']), use_container_width=True, hide_index=True)
            if 'bowling' in inn:
                st.markdown("**Bowling**")
                st.dataframe(pd.DataFrame(inn['bowling']), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error fetching scorecard: {e}")
