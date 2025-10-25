import streamlit as st
from utils import set_page, top_nav, footer, get_fixtures, card, empty_state, REFRESH_MS
from streamlit_autorefresh import st_autorefresh

set_page()
st.title("📅 Fixtures")
top_nav(active="fixtures")

st_autorefresh(interval=REFRESH_MS, key="fixtures_autorefresh")

col_days, = st.columns(1)
with col_days:
    days = st.slider("Show fixtures for next N days", 1, 30, 7)

data = get_fixtures(days_ahead=days)
if "error" in data:
    empty_state("Could not fetch fixtures. Check API key & base URL in utils.py")
else:
    items = data.get("fixtures") or data.get("data") or []
    if not items:
        empty_state("No fixtures found for the selected range.")
    else:
        for f in items:
            title = f.get("name") or f"{f.get('team1','?')} vs {f.get('team2','?')}"
            sub = " • ".join([s for s in [f.get("start_time"), f.get("venue")] if s])
            def body():
                st.write(f)
            card(title, body=body, subtitle=sub)

footer()