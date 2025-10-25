import streamlit as st
from app.utils import auto_refresh, header

st.set_page_config(page_title="Talking Bat", page_icon="🏏", layout="wide")
auto_refresh()
header()

query = st.experimental_get_query_params().get("page", ["home"])[0]

if query == "live":
    from app.Live import show_live
    show_live()
elif query == "fixtures":
    from app.Fixtures import show_fixtures
    show_fixtures()
elif query == "results":
    from app.Results import show_results
    show_results()
elif query == "scorecard":
    from app.Scorecard import show_scorecard
    show_scorecard()
else:
    st.subheader("Welcome")
    st.write("This is **Talking Bat v2 (White & Gold Edition)** — mobile-friendly live cricket app.")
    st.info("Use the buttons above to explore live matches, fixtures, results, and scorecards.")

st.markdown("<div class='tb-footer'>Powered by Talking Bat © 2025 | All Rights Reserved</div>", unsafe_allow_html=True)
