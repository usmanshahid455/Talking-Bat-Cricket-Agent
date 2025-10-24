# app/Home.py
import streamlit as st

st.set_page_config(page_title="Talking Bat — Cricket AI Agent", page_icon="🏏", layout="wide")

st.title("🏏 Talking Bat — Cricket AI Agent")
st.markdown("""Welcome! This web app shows **all international matches** with live status, fixtures, results, and scorecards.

Use the sidebar to navigate:
- **Live** — ongoing matches (status + quick view)
- **Fixtures** — upcoming matches
- **Results** — recent completed matches
- **Scorecard** — open by Match ID
""")
st.info("Tip: For best results, add your API key in Streamlit **Secrets**. This starter already includes your key in `secrets_template.toml`.")
