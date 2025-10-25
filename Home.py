
import streamlit as st
from utils import set_page_config, nav_bar, footer, autorefresh_30s
import Live, Fixtures, Results, Scorecard

set_page_config()
page = nav_bar()
autorefresh_30s()

if page == "🏏 Live":
    Live.render()
elif page == "📅 Fixtures":
    Fixtures.render()
elif page == "✅ Results":
    Results.render()
elif page == "📋 Scorecard":
    Scorecard.render()
else:
    st.title("Talking Bat — Cricket Hub")
    st.caption("Welcome! Use the emoji tabs above to navigate.")

footer()
