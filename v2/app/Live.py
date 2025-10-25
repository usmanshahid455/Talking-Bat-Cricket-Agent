import streamlit as st
from utils import api_get, GOLD

def show_live():
    st.markdown(f"<h3 style='color:{GOLD};'>🔴 Live Matches</h3>", unsafe_allow_html=True)
    
    try:
        data = api_get("/currentMatches")
        matches = data.get("data", [])

        if not matches:
            st.info("No live matches at the moment.")
            return

        for m in matches:
            st.markdown("---")
            teams = f"{m.get('teamInfo', [{}])[0].get('name', '')} vs {m.get('teamInfo', [{}])[-1].get('name', '')}"
            st.markdown(f"### 🏟 {teams}")

            # Status and Venue
            st.write(f"📍 **Venue:** {m.get('venue', 'N/A')}")
            st.write(f"🕒 **Status:** {m.get('status', 'No update')}")

            # Live Score Details
            score_data = m.get('score', [])
            if score_data:
                for s in score_data:
                    team = s.get("inning", "")
                    runs = s.get("r", "")
                    wickets = s.get("w", "")
                    overs = s.get("o", "")
                    st.markdown(f"**{team}:** {runs}/{wickets} ({overs} ov)")
            else:
                st.warning("No score data available yet.")

            # Additional Info
            if m.get("tossWinner"):
                st.write(f"🪙 **Toss:** {m['tossWinner']} won the toss")
            if m.get("matchType"):
                st.write(f"🏏 **Format:** {m['matchType'].upper()}")

    except Exception as e:
        st.error(f"⚠️ Unable to fetch live matches: {e}")
