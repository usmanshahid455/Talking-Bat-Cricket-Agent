import streamlit as st
from datetime import datetime, timedelta
from utils import api_get, GOLD, NAVY

def show_live():
    st.markdown(f"<h3 style='color:{GOLD};'>🔴 Live & Recent Matches</h3>", unsafe_allow_html=True)

    try:
        data = api_get("/matches", {"offset": "0"})
        matches = data.get("data", [])
        if not matches:
            st.info("No match data found from API.")
            return

        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
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

        # ---------- GOLD TICKER BAR ----------
        ticker_text = " | ".join([
            f"{m.get('teams', [''])[0]} vs {m.get('teams', ['',''])[1]} – {m.get('status', '')}"
            for m in filtered
        ])
        st.markdown(f"""
        <div style='background:{GOLD};color:{NAVY};
                    padding:6px 0;border-radius:6px;
                    font-weight:600;white-space:nowrap;
                    overflow:hidden;'>
            <marquee behavior="scroll" direction="left" scrollamount="6">{ticker_text}</marquee>
        </div><br>
        """, unsafe_allow_html=True)
        # -------------------------------------

        # ---------- MATCH CARDS ----------
        for m in filtered:
            st.markdown("---")
            teams = f"{m.get('teamInfo', [{}])[0].get('name', '')} vs {m.get('teamInfo', [{}])[-1].get('name', '')}"
            st.markdown(f"### 🏏 {teams}")

            st.write(f"📍 **Venue:** {m.get('venue', 'N/A')}")
            st.write(f"🕒 **Status:** {m.get('status', 'No update')}")
            st.write(f"📅 **Date:** {m.get('dateTimeGMT', 'N/A')}")
            if m.get("matchType"):
                st.write(f"🏷 **Format:** {m['matchType'].upper()}")

            score_data = m.get("score", [])
            if score_data:
                for s in score_data:
                    team = s.get("inning", "")
                    runs = s.get("r", "")
                    wickets = s.get("w", "")
                    overs = s.get("o", "")
                    st.markdown(f"**{team}:** {runs}/{wickets} ({overs} ov)")
            else:
                st.caption("⏳ Waiting for score updates…")

    except Exception as e:
        st.error(f"⚠️ Unable to fetch live data: {e}")
