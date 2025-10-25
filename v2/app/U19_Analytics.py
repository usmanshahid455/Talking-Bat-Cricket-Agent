import streamlit as st
import pandas as pd
from io import BytesIO

def show_u19_analytics():
    st.set_page_config(page_title="U-19 Analytics", page_icon="📊", layout="wide")

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #ffffff;
    }
    .tb-header {
        text-align:center;
        padding: 15px 10px;
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 15px;
    }
    .tb-title {
        font-weight:700;
        font-size:28px;
        color:#D4AF37;
        letter-spacing:1px;
    }
    .tb-footer {
        text-align:center;
        color:#777;
        margin-top:40px;
        padding-top:10px;
        border-top:1px solid #eee;
        font-size:13px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='tb-header'>
      <div class='tb-title'>📊 Talking Bat • U-19 Analytics (v3 Pro)</div>
      <p style='color:#666; font-size:14px;'>Tournament, Match & Team level analytics for Women U-19 ball-by-ball data.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df.columns = [c.strip() for c in df.columns]

        # ✅ Auto-map column names (case-insensitive)
        colmap = {c.lower().replace(" ", "_"): c for c in df.columns}
        get = lambda x: colmap.get(x, None)

        # Ensure required columns exist
        required = ["tournament", "match_id", "batting_team", "over", "ball", "total_runs"]
        missing = [x for x in required if get(x) is None]
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            st.stop()

        df = df.rename(columns={get("tournament"): "tournament",
                                get("match_id"): "match_id",
                                get("batting_team"): "batting_team",
                                get("over"): "over",
                                get("ball"): "ball",
                                get("total_runs"): "total_runs"})

        # 🎯 Filters
        tournaments = sorted(df["tournament"].dropna().unique().tolist())
        selected_tour = st.selectbox("🏆 Select Tournament", tournaments)

        match_ids = sorted(df[df["tournament"] == selected_tour]["match_id"].dropna().unique().tolist())
        selected_match = st.selectbox("🎯 Select Match ID", match_ids)

        teams = sorted(df[df["match_id"] == selected_match]["batting_team"].dropna().unique().tolist())
        selected_team = st.selectbox("🏏 Select Batting Team", teams)

        filtered = df[(df["tournament"] == selected_tour) &
                      (df["match_id"] == selected_match) &
                      (df["batting_team"] == selected_team)]

        if filtered.empty:
            st.warning("⚠️ No data available for this selection.")
            return

        # ✅ Stats Summary
        st.markdown("### 📈 Team Summary KPIs")
        total_runs = filtered["total_runs"].sum()
        total_balls = len(filtered)
        overs = int(total_balls // 6)
        balls = int(total_balls % 6)
        run_rate = round(total_runs / (total_balls / 6), 2)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Runs", total_runs)
        c2.metric("Balls", total_balls)
        c3.metric("Overs", f"{overs}.{balls}")
        c4.metric("Run Rate", run_rate)

    else:
        st.info("👆 Please upload your Women U-19 Excel file to start analysis.")

    st.markdown("""
    <div class='tb-footer'>
      Powered by <b style='color:#D4AF37;'>Talking Bat Analytics</b> © 2025 | All Rights Reserved
    </div>
    """, unsafe_allow_html=True)
