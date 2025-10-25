
import streamlit as st
import requests
import contextlib
import pandas as pd

def set_page_config():
    st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")
    # Mobile-friendly styles
    st.markdown(r'''
        <style>
        @media (max-width: 768px) {
            .block-container {padding: 1rem !important;}
            .stButton>button, .stRadio [role="radiogroup"] label {font-size: 1.05rem !important;}
        }
        /* Sticky top nav */
        .tb-nav {position: sticky; top: 0; z-index: 100; background: var(--background-color); padding: 0.25rem 0; border-bottom: 1px solid rgba(0,0,0,0.05);}
        /* Footer */
        .tb-footer {text-align:center; margin-top: 2rem; opacity: 0.7;}
        /* Pills */
        .tb-pill {display:inline-block; padding: .25rem .5rem; border-radius: 999px; border:1px solid rgba(0,0,0,.1); margin-right:.5rem;}
        /* Cards */
        .tb-card {padding: 1rem; border-radius: 1rem; border: 1px solid rgba(0,0,0,0.08); background: rgba(0,0,0,0.02); margin-bottom: 0.75rem;}
        </style>
    ''', unsafe_allow_html=True)

def nav_bar():
    st.markdown('<div class="tb-nav"></div>', unsafe_allow_html=True)
    tabs = ["🏏 Live", "📅 Fixtures", "✅ Results", "📋 Scorecard"]
    return st.radio("Navigate", tabs, key="tb_nav", horizontal=True, label_visibility="collapsed")

def autorefresh_30s():
    # Simple meta refresh for reliability across Streamlit versions
    st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

def header(title:str):
    st.title(title)

@contextlib.contextmanager
def card():
    st.markdown('<div class="tb-card">', unsafe_allow_html=True)
    yield
    st.markdown('</div>', unsafe_allow_html=True)

def table_compact(rows, index=False):
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=not index)

def pill(label, value):
    st.markdown(f'<span class="tb-pill"><strong>{label}:</strong> {value}</span>', unsafe_allow_html=True)

def empty_state(title, help_text=""):
    st.info(f"{title}\n\n{help_text}" if help_text else title)

def api_get_json(path:str):
    base_url = st.secrets.get("CRICKETDATA_BASE_URL", "https://api.cricketdata.example.com")
    key = st.secrets.get("CRICKETDATA_API_KEY")
    if not key:
        raise RuntimeError("Missing CRICKETDATA_API_KEY in Streamlit secrets.")
    url = f"{base_url.rstrip('/')}{path}"
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=20)
    r.raise_for_status()
    return r.json()

def footer():
    st.markdown('<div class="tb-footer">Powered by Talking Bat © 2025</div>', unsafe_allow_html=True)
