import streamlit as st
from utils import auto_refresh, header

# =======================================
# ⚙️ PAGE CONFIGURATION
# =======================================
st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")

# =======================================
# 🧭 SESSION STATE SETUP
# =======================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "auto_refresh_on" not in st.session_state:
    st.session_state.auto_refresh_on = True  # default ON

def set_page(p):
    st.session_state.page = p

page = st.session_state.page

# =======================================
# 🎛️ AUTO-REFRESH TOGGLE (top-right)
# =======================================
col1, col2 = st.columns([0.8, 0.2])
with col1:
    header()
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.session_state.auto_refresh_on = st.toggle("🔁 Auto-Refresh", value=st.session_state.auto_refresh_on)

# Enable auto-refresh only on Live/Fixtures pages and only if toggle is ON
if st.session_state.auto_refresh_on and page in ["live", "fixtures"]:
    auto_refresh()

# =======================================
# 🏠 MAIN NAVIGATION BUTTONS
# =======================================
st.markdown("<br>", unsafe_allow_html=True)
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

# =======================================
# 📄 PAGE ROUTING
# =======================================
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
        <div style='text-align:center; padding:25px;'>
          <h2 style='color:#D4AF37;'>🏏 Welcome to Talking Bat Pro Analytics</h2>
          <p style='font-size:16px; color:#444;'>
            This platform unifies <b>Live Cricket Data</b> and <b>Performance Analytics</b> 
            into one professional dashboard built for analysts, coaches, and scouts.
          </p>
          <div style='text-align:left; display:inline-block; margin-top:20px;'>
            <ul style='line-height:1.8; font-size:15px; color:#555;'>
              <li>📡 Track live international & domestic matches</li>
              <li>📊 Upload U-19 datasets to view KPIs & trends</li>
              <li>🤖 Generate AI-powered insights for match strategy</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =======================================
# ⚓ FOOTER
# =======================================
st.markdown(
    """
    <div class='tb-footer' style='text-align:center; color:#777; margin-top:40px;
         border-top:1px solid #eee; padding-top:10px; font-size:13px;'>
         Powered by <span style='color:#D4AF37; font-weight:600;'>Talking Bat Analytics</span> © 2025 | All Rights Reserved
    </div>
    """,
    unsafe_allow_html=True,
)
