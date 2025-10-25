import streamlit as st
from utils import auto_refresh, header

st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")
auto_refresh()

# ---- Session-based page navigation ----
if "page" not in st.session_state:
    st.session_state.page = "home"

def set_page(p):
    st.session_state.page = p

# ---- Header ----
st.markdown(f"""
    <div class='tb-header'>
      <img class='tb-logo' src='talkingbat_logo.png' alt='Talking Bat'>
      <div class='tb-title'>Talking Bat</div>
      <div class='tb-nav'>
        <button onclick="window.location.href='/'" style='display:none;'></button>
      </div>
    </div>
""", unsafe_allow_html=True)

# ---- Buttons ----
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏏 Live"): set_page("live")
with c2:
    if st.button("📅 Fixtures"): set_page("fixtures")
with c3:
    if st.button("✅ Results"): set_page("results")
with c4:
    if st.button("📋 Scorecard"): set_page("scorecard")

# ---- Page loader ----
page = st.session_state.page

if page == "live":
    from Live import show_live
    show_live()
elif page == "fixtures":
    from Fixtures import show_fixtures
    show_fixtures()
elif page == "results":
    from Results import show_results
    show_results()
elif page == "scorecard":
    from Scorecard import show_scorecard
    show_scorecard()
else:
    st.subheader("Welcome")
    st.write("This is **Talking Bat Cricket Agent v2 (White & Gold Edition)** — mobile-friendly live cricket app.")
    st.info("Use the buttons above to explore live matches, fixtures, results, and scorecards.")

st.markdown("<div class='tb-footer'>Powered by Talking Bat © 2025 | All Rights Reserved</div>", unsafe_allow_html=True)
