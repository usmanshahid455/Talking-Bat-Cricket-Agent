
import streamlit as st
from utils import header, api_get_json, card, empty_state, pill

def render():
    header("📋 Scorecard")
    match_id = st.text_input("Enter Match ID", placeholder="e.g., 12345")
    if not match_id:
        empty_state("Enter a match ID to view the scorecard.")
        return

    try:
        data = api_get_json(f"/scorecard/{match_id}")
    except Exception as e:
        empty_state("Could not load scorecard.", help_text=str(e))
        return

    if not data:
        empty_state("No scorecard found for this match.")
        return

    with card():
        st.subheader(data.get("match_title", "Match"))
        st.caption(data.get("venue", "-"))
        st.write(data.get("status",""))

    innings = data.get("innings", [])
    if not innings:
        empty_state("No innings data available.")
        return

    for inn in innings:
        with card():
            st.markdown(f"### {inn.get('team','Team')} — {inn.get('runs','-')}/{inn.get('wkts','-')} ({inn.get('overs','-')} ov)")
            if "batting" in inn:
                st.markdown("**Batting**")
                st.dataframe(inn["batting"], use_container_width=True, hide_index=True)
            if "bowling" in inn:
                st.markdown("**Bowling**")
                st.dataframe(inn["bowling"], use_container_width=True, hide_index=True)

    if "player_of_the_match" in data:
        pill("POTM", data["player_of_the_match"])
