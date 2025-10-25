import streamlit as st
from utils import auto_refresh, header

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")
auto_refresh()
header()

# ====== SESSION NAVIGATION ======
if "page" not in st.session_state:
    st.session_state.page = "home"

def set_page(p):
    st.session_state.page = p

page = st.session_state.page

# ====== MAIN NAV BUTTONS ======
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("🏏 Live"):
        set_page("live")
with c2:
    if st.button("📅 Fixtures"):
        set_page("fixtures")
with c3:
    if st.button("✅ Results"):
        set_page("results")
with c4:
    if st.button("📋 Scorecard"):
        set_page("scorecard")
with c5:
    if st.button("📊 U-19 Analytics"):
        set_page("u19")

# ====== PAGE ROUTING ======
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

elif page == "u19":
    from U19_Analytics import show_u19_analytics
    show_u19_analytics()

else:
    st.markdown(
        """
        <div class='tb-card'>
          <h3>Welcome to <span style='color:#D4AF37;'>Talking Bat Pro Analytics</span></h3>
          <p>This platform combines <b>Live Cricket Data</b> and <b>Talking Bat Performance Analytics</b>
             into one professional dashboard.</p>
          <ul>
            <li>🏏 Track live international and domestic matches</li>
            <li>📊 Upload U-19 data and view team & player KPIs</li>
            <li>🤖 Generate AI Insights for scouting and coaching</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ====== FOOTER ======
st.markdown(
    "<div class='tb-footer'>Powered by Talking Bat Analytics © 2025 | All Rights Reserved</div>",
    unsafe_allow_html=True,
)
