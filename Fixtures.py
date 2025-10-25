
import streamlit as st
import pandas as pd
from utils import header, api_get_json, table_compact, empty_state, card

def render():
    header("📅 Upcoming Fixtures")
    try:
        data = api_get_json("/fixtures")
    except Exception as e:
        empty_state("No fixtures available.", help_text=str(e))
        return

    fixtures = data.get("fixtures", [])
    if not fixtures:
        empty_state("No upcoming fixtures found.", "Auto-refreshing every 30 seconds…")
        return

    rows = []
    for f in fixtures:
        rows.append({
            "Date": f.get("date_local","-"),
            "Match": f.get("match_title","-"),
            "Venue": f.get("venue","-"),
            "Series": f.get("series","-"),
            "Format": f.get("format","-"),
        })
    table_compact(rows, index=False)
