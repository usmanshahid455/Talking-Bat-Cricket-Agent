import os
import time
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone

# -------------------------
# Global Config
# -------------------------
APP_TITLE = "Talking Bat"
APP_FOOTER = "Powered by Talking Bat © 2025"
REFRESH_MS = 30_000  # 30 seconds
TZ = timezone(timedelta(hours=5))  # Asia/Karachi approximate for local rendering

# -------------------------
# Page / Layout helpers
# -------------------------
def set_page(wide: bool = True):
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏏",
        layout="wide" if wide else "centered",
        initial_sidebar_state="collapsed",
    )
    _mobile_first_css()

def _mobile_first_css():
    # Mobile-first responsive tweaks + sticky footer
    st.markdown(
        """
        <style>
        /* Remove extra padding on mobile */
        .block-container {padding-top: 1rem; padding-bottom: 5rem; max-width: 1200px;}
        /* Make tables responsive */
        .dataframe {width: 100% !important; overflow-x: auto;}
        /* Top nav pills */
        .tb-nav {display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; margin-bottom: .75rem;}
        .tb-pill {padding:.4rem .6rem; border-radius: 999px; border:1px solid #e5e7eb; text-decoration:none; color:inherit;}
        .tb-pill.active{background:#0ea5e9; color:white; border-color:#0ea5e9;}
        /* Footer */
        .tb-footer {position: fixed; left: 0; right: 0; bottom: 0; padding: .6rem; text-align:center; 
                    font-size: 0.9rem; background: #f8fafc; border-top: 1px solid #e5e7eb; z-index: 9999;}
        /* Cards */
        .tb-card {border:1px solid #e5e7eb; border-radius: .75rem; padding: .9rem; background:white;}
        .tb-muted {color:#64748b;}
        </style>
        """,
        unsafe_allow_html=True,
    )

def footer():
    st.markdown(f"<div class='tb-footer'>{APP_FOOTER}</div>", unsafe_allow_html=True)

def top_nav(active: str):
    items = [
        ("home", "🏏", "Home"),
        ("fixtures", "📅", "Fixtures"),
        ("results", "✅", "Results"),
        ("scorecard", "📋", "Scorecard"),
    ]
    st.markdown("<div class='tb-nav'>", unsafe_allow_html=True)
    cols = st.columns(len(items))
    for i, (key, icon, label) in enumerate(items):
        is_active = "active" if active == key else ""
        url = _with_query_params({"tab": key})
        html = f"<a class='tb-pill {is_active}' href='{url}'>{icon} {label}</a>"
        with cols[i]:
            st.markdown(html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def _with_query_params(params: dict) -> str:
    # Build a link preserving known params while overriding provided ones
    from urllib.parse import urlencode
    qs = st.query_params.to_dict()
    qs.update(params)
    return "?" + urlencode(qs)

def autorefresh(enabled=True, milliseconds: int = REFRESH_MS, key: str = "auto_refresh"):
    if enabled:
        st.autorefresh = st.experimental_rerun  # backward-friendly alias
        st.session_state.setdefault("_last_refresh_ms", milliseconds)
        st.experimental_set_query_params(**st.query_params)
        st.experimental_rerun  # no-op for older, but ensures state
    # Streamlit provides st_autorefresh; wrap lightly for forward compat
    try:
        from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx  # noqa: F401
        st_autorefresh = getattr(st, "autorefresh", None) or getattr(st, "experimental_rerun", None)
    except Exception:
        st_autorefresh = None
    if hasattr(st, "autorefresh"):
        st.autorefresh(interval=milliseconds, key=key)

# -------------------------
# API helpers
# -------------------------
@st.cache_data(ttl=20)
def _request_json(url: str, params: dict = None, headers: dict = None):
    try:
        r = requests.get(url, params=params or {}, headers=headers or {}, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "url": url, "params": params}

def get_api_key():
    # Expecting .streamlit/secrets.toml with:
    # [cricketdata]
    # api_key="YOUR_KEY"
    try:
        return st.secrets["cricketdata"]["api_key"]
    except Exception:
        return None

def api_headers():
    key = get_api_key()
    if key:
        return {"apikey": key, "Authorization": f"Bearer {key}"}
    return {}

# Example endpoints — adjust to your provider
BASE = "https://api.cricketdata.org"  # placeholder base; update to your provider

@st.cache_data(ttl=15)
def get_live_matches():
    # Replace with your provider's live endpoint
    url = f"{BASE}/v1/live"
    return _request_json(url, headers=api_headers())

@st.cache_data(ttl=60)
def get_fixtures(days_ahead: int = 7):
    url = f"{BASE}/v1/fixtures"
    params = {"days": days_ahead}
    return _request_json(url, params=params, headers=api_headers())

@st.cache_data(ttl=60)
def get_recent_results(days_back: int = 7):
    url = f"{BASE}/v1/results"
    params = {"days": days_back}
    return _request_json(url, params=params, headers=api_headers())

@st.cache_data(ttl=15)
def get_scorecard(match_id: str):
    url = f"{BASE}/v1/scorecard/{match_id}"
    return _request_json(url, headers=api_headers())

# -------------------------
# Small UI helpers
# -------------------------
def card(title: str, body=None, subtitle=None):
    with st.container():
        st.markdown(f"<div class='tb-card'><div><strong>{title}</strong></div>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<div class='tb-muted' style='margin-top:.2rem'>{subtitle}</div>", unsafe_allow_html=True)
        if body:
            body()
        st.markdown("</div>", unsafe_allow_html=True)

def empty_state(message: str):
    st.info(message)