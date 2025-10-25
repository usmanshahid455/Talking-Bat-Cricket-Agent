
import streamlit as st
import pandas as pd
from utils import header, api_get_json, table_compact, empty_state

def render():
    header("✅ Recent Results")
    try:
        data = api_get_json("/results")
    except Exception as e:
        empty_state("No results available.", help_text=str(e))
        return

    results = data.get("results", [])
    if not results:
        empty_state("No recent results found.", "Auto-refreshing every 30 seconds…")
        return

    rows = []
    for r in results:
        rows.append({
            "Date": r.get("date_local","-"),
            "Winner": r.get("winner","-"),
            "Margin": r.get("margin","-"),
            "Match": r.get("match_title","-"),
            "Venue": r.get("venue","-"),
        })
    table_compact(rows, index=False)
