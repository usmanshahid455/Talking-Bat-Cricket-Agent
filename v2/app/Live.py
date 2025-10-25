import streamlit as st
from datetime import datetime, timedelta
from utils import api_get, GOLD

def show_live():
    st.markdown(f"<h3 style='color:{GOLD};'>🔴 Live & Recent Matches</h3>", unsafe_allow_html=True)

    try:
        # Get matches from today and yesterday
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        params = {"offset": "0"}
        data = api_get("/matches", params)
        matches = data.get("data", [])

        if not matches:
            st.info("No match data found from API.")
            return

        # Filter only live or very recent ones
        filtered = []
        for m in matches:
            try:
                date_str = m.get("dateTimeGMT", "")
                if not date_str:
                    continue
                match_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                if match_date >= yesterday and m.get("status"):
                    filtered.append(m)
            except Exception:
                continue

        if not filtered:
            st.info("No live or recent matches available today.")
            return

        # Display the filtered matches
        for m in filtered:
            st.markdown("---")
            teams = f"{m.get('teamInfo', [{}])[0].get('name', '')} vs {m.get('teamInfo', [{}])[-1].get('name', '')}"
            st.markdown(f"### 🏏 {teams}")

            # Show match type and venue
            if m.get("matchType"):
                st.write(f"**Format:** {m['matchType'].upper()}")
            if m.get("venue"):
                st.write(f"📍 {m['venue']}")

            # Show status and date
            st.write(f"🕒 **Status:** {m.get('status', 'N/A')}")
            st.write(f"📅 **Date:** {m.get('dateTimeGMT', 'N/A')}")

            # Show score info if available
            score_data = m.get("score", [])
            if score_data:
                for s in score_data:
                    team = s.get("inning", "")
                    runs = s.get("r", "")
                    wickets = s.get("w", "")
                    overs = s.get("o", "")
                    st.markdown(f"**{team}:** {runs}/{wickets} ({overs} ov)")
            else:
                st.caption("⏳ Waiting for live score update...")

    except Exception as e:
        st.error(f"⚠️ Unable to fetch live data: {e}")
