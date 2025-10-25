import streamlit as st
from utils import auto_refresh, header

st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")
auto_refresh()
header()

# ---- Page logic ----
if "page" not in st.session_state:
    st.session_state.page = "home"

def set_page(p): st.session_state.page = p
page = st.session_state.page

# ---- Navigation ----
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏏 Live"): set_page("live")
with c2:
    if st.button("📅 Fixtures"): set_page("fixtures")
with c3:
    if st.button("✅ Results"): set_page("results")
with c4:
    if st.button("📋 Scorecard"): set_page("scorecard")

# ---- Routing ----
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
    st.markdown(
        """
        <div class='tb-card'>
        <h3>Welcome to <span style='color:#D4AF37;'>Talking Bat Pro Analytics</span></h3>
        <p>This platform combines <b>live cricket data</b> and <b>Talking Bat performance analytics</b> into one professional dashboard.</p>
        <ul>
          <li>🏏 Monitor live scores with real-time updates</li>
          <li>📊 Analyze team & player trends</li>
          <li>🤖 Generate AI insights and scouting summaries</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='tb-footer'>Powered by Talking Bat Analytics © 2025 | All Rights Reserved</div>", unsafe_allow_html=True)
