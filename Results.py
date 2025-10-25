import streamlit as st
from utils import set_page, top_nav, footer, get_recent_results, card, empty_state, REFRESH_MS
from streamlit_autorefresh import st_autorefresh

set_page()
st.title("✅ Results")
top_nav(active="results")

st_autorefresh(interval=REFRESH_MS, key="results_autorefresh")

col_days, = st.columns(1)
with col_days:
    days = st.slider("Show results from last N days", 1, 30, 7)

data = get_recent_results(days_back=days)
if "error" in data:
    empty_state("Could not fetch results. Check API key & base URL in utils.py")
else:
    items = data.get("results") or data.get("data") or []
    if not items:
        empty_state("No results in the selected window.")
    else:
        for r in items:
            title = r.get("name") or f"{r.get('team1','?')} vs {r.get('team2','?')}"
            sub = " • ".join([s for s in [r.get("status"), r.get("venue")] if s])
            def body():
                st.write(r)
            card(title, body=body, subtitle=sub)

footer()