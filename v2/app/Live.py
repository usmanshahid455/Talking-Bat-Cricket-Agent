import streamlit as st
from datetime import datetime, timedelta
from utils import api_get, GOLD

def show_live():
    st.markdown(f"<h3 style='color:{GOLD};'>🔴 Live & Recent Matches</h3>", unsafe_allow_html=True)

    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        data = api_get("/matches", {"offset": "0"})
        matches = data.get("data", [])

        if not matches:
            st.info("No matches available from API.")
            return

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
            st.info("No live or recent matches today.")
            return

        for m in filtered:
            st.markdown("---")
            teams = f"{m.get('teamInfo', [{}])[0].get('name', '')} vs {m.get('teamInfo', [{}])[-1].get('name', '')}"
            st.markdown(f"### 🏏 {teams}")

            st.write(f"📍 **Venue:** {m.get('venue', 'N/A')}")
            st.write(f"🕒 **Status:** {m.get('status', 'No update')}")
            st.write(f"📅 **Date:** {m.get('dateTimeGMT', 'N/A')}")
            if m.get("matchType"):
                st.write(f"🏷 **Format:** {m['matchType'].upper()}")

            # Live score summary
            score_data = m.get("score", [])
            if score_data:
                for s in score_data:
                    team = s.get("inning", "")
                    runs = s.get("r", "")
                    wickets = s.get("w", "")
                    overs = s.get("o", "")
                    st.markdown(f"**{team}:** {runs}/{wickets} ({overs} ov)")
            else:
                st.caption("⏳ Waiting for score updates...")

            # Expandable detailed scorecard
            match_id = m.get("id", "")
            if not match_id:
                continue

            with st.expander("📊 View Detailed Scorecard"):
                try:
                    details = api_get("/match_info", {"id": match_id})
                    d = details.get("data", {})

                    if not d:
                        st.warning("No detailed scorecard yet.")
                        continue

                    # Batting summary
                    batting = d.get("batting", [])
                    bowling = d.get("bowling", [])

                    if batting:
                        st.markdown(f"<h5 style='color:{GOLD};margin-top:10px;'>Top Batters</h5>", unsafe_allow_html=True)
                        for b in batting[:3]:
                            name = b.get("batsman", "Unknown")
                            runs = b.get("R", "0")
                            balls = b.get("B", "0")
                            fours = b.get("4s", "0")
                            sixes = b.get("6s", "0")
                            sr = b.get("SR", "0")
                            st.write(f"🏏 **{name}** — {runs} ({balls}) 4s:{fours} 6s:{sixes} SR:{sr}")

                    if bowling:
                        st.markdown(f"<h5 style='color:{GOLD};margin-top:10px;'>Top Bowlers</h5>", unsafe_allow_html=True)
                        for bow in bowling[:3]:
                            name = bow.get("bowler", "Unknown")
                            overs = bow.get("O", "0")
                            maidens = bow.get("M", "0")
                            runs = bow.get("R", "0")
                            wkts = bow.get("W", "0")
                            econ = bow.get("Econ", "0")
                            st.write(f"🎯 **{name}** — {wkts}/{runs} in {overs} overs (Econ {econ})")

                except Exception as e:
                    st.error(f"❌ Unable to load detailed data: {e}")

    except Exception as e:
        st.error(f"⚠️ Error fetching matches: {e}")
