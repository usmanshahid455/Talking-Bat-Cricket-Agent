import streamlit as st
from utils import auto_refresh, header

st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")
auto_refresh()
header()

# ✅ Correct query handling (fixed your line)
params = st.query_params
query = params.get("page", ["home"])[0]

if query == "live":
    from Live import show_live
    show_live()
elif query == "fixtures":
    from Fixtures import show_fixtures
    show_fixtures()
elif query == "results":
    from Results import show_results
    show_results()
elif query == "scorecard":
    from Scorecard import show_scorecard
    show_scorecard()
else:
    st.subheader("Welcome")
    st.write("This is **Talking Bat Cricket Agent v2 (White & Gold Edition)** — mobile-friendly live cricket app.")
    st.info("Use the buttons above to explore live matches, fixtures, results, and scorecards.")

st.markdown("<div class='tb-footer'>Powered by Talking Bat © 2025 | All Rights Reserved</div>", unsafe_allow_html=True)
