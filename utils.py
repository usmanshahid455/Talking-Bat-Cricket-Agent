# app/utils.py
import os, time
import requests
import streamlit as st

API_BASE = "https://api.cricapi.com/v1"
API_KEY = st.secrets.get("CRICKETDATA_API_KEY", os.getenv("CRICKETDATA_API_KEY", ""))
REFRESH = int(st.secrets.get("REFRESH_SECONDS", os.getenv("REFRESH_SECONDS", "30")))

def api_get(path: str, params=None):
    if params is None: params = {}
    if API_KEY:
        params["apikey"] = API_KEY
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def auto_refresh():
    # Adds a simple auto-refresh using Streamlit's rerun mechanics
    st.caption(f"Auto-refresh every {REFRESH} seconds")
    st.experimental_singleton.clear() if hasattr(st, "experimental_singleton") else None
    st.markdown(
        f"<meta http-equiv='refresh' content='{REFRESH}'>",
        unsafe_allow_html=True
    )
