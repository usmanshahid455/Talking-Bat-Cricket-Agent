
import streamlit as st
import pandas as pd
from utils import header, api_get_json, card, empty_state

def render():
    header("🏏 Live Matches")
    try:
        data = api_get_json("/live")
    except Exception as e:
        empty_state("No live feed yet.", help_text=str(e))
        return

    if not data or ("matches" not in data) or (len(data["matches"]) == 0):
        empty_state("No live matches right now.", "Auto-refreshing every 30 seconds…")
        return

    for m in data["matches"]:
        with card():
            st.subheader(f'{m.get("series","")} — {m.get("match_title","")}')
            st.write(f'**Status:** {m.get("status","-")}')
            if "score" in m:
                st.write(m["score"])
            st.write(f'**Venue:** {m.get("venue","-")}')
            st.caption(f'{m.get("start_time_local","")} — {m.get("format","")}')
