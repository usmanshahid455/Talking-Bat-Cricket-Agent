import streamlit as st
from utils import set_page, top_nav, footer, get_live_matches, card, empty_state, REFRESH_MS
from streamlit_autorefresh import st_autorefresh

set_page()
st.title("🏏 Live")

# Top navigation (4 emojis) — Live is highlighted under Home, but page exists independently
top_nav(active="home")

# Auto-refresh every 30s
st_autorefresh(interval=REFRESH_MS, key="live_autorefresh")

data = get_live_matches()
if "error" in data:
    empty_state("Could not fetch live matches. Check API key & base URL in utils.py")
else:
    matches = data.get("matches") or data.get("data") or []
    if not matches:
        empty_state("No live matches currently.")
    else:
        for m in matches:
            title = m.get("name") or f"{m.get('team1','?')} vs {m.get('team2','?')}"
            sub = " • ".join([s for s in [m.get("status"), m.get("venue")] if s])
            def body():
                st.write(m)
            card(title, body=body, subtitle=sub)

footer()