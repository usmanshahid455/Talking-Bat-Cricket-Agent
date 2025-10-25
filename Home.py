import streamlit as st
from utils import set_page, top_nav, footer, card, get_live_matches, empty_state

set_page()
st.title("🏏 Talking Bat — Home")

# Top navigation (4 emojis)
top_nav(active="home")

st.caption("Mobile‑friendly dashboard • Auto‑refresh on live pages • Uses your CricketData API key from secrets")

# Home: Quick Live Glance
def live_glance():
    data = get_live_matches()
    if "error" in data:
        empty_state("Could not fetch live matches. Add your API key in `.streamlit/secrets.toml` and check the provider base URL in `utils.py`.")
        return
    matches = data.get("matches") or data.get("data") or []
    if not matches:
        empty_state("No live matches at the moment.")
        return
    for m in matches[:6]:
        title = m.get("name") or f"{m.get('team1','?')} vs {m.get('team2','?')}"
        sub = m.get("status") or m.get("venue") or ""
        card(title, subtitle=sub)

live_glance()

st.divider()
st.subheader("Quick Links")
lcol, fcol, rcol = st.columns(3)
with lcol:
    st.page_link("app/Live.py", label="Go to Live", icon="🏏")
with fcol:
    st.page_link("app/Fixtures.py", label="Upcoming Fixtures", icon="📅")
with rcol:
    st.page_link("app/Results.py", label="Recent Results", icon="✅")

footer()