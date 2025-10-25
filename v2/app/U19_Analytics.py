import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def show_u19_analytics():
    st.set_page_config(page_title="U-19 Analytics", page_icon="📊", layout="wide")

    # =======================================
    # 🎨 TALKING BAT STYLE
    # =======================================
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
    .card {
        background-color:#fff8e1;
        border:1px solid #D4AF37;
        border-radius:10px;
        padding:10px;
        text-align:center;
        margin-bottom:8px;
    }
    .card h4 {color:#D4AF37; margin:4px 0 6px 0;}
    .card p {margin:2px; color:#333;}
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

    # =======================================
    # 📁 FILE UPLOAD
    # =======================================
    if "uploaded_data" not in st.session_state:
        st.session_state.uploaded_data = None

    uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file is not None:
        st.session_state.uploaded_data = uploaded_file
        st.success("✅ File uploaded successfully!")

    if st.session_state.uploaded_data is not None:
        df = pd.read_excel(st.session_state.uploaded_data)

        # ✅ Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # ✅ Verify required columns exist
        required_cols = ["tournament", "match_id", "batting_team", "over", "ball", "total_runs"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            st.stop()

        # ===== Filter legal deliveries =====
        if "ball_type" in df.columns:
            df = df[df["ball_type"].astype(str).str.lower() == "legal"]

        # ===== Cascading Filters =====
        tournaments = sorted(df["tournament"].dropna().unique().tolist())
        selected_tour = st.selectbox("🏆 Select Tournament", tournaments)

        match_ids = sorted(df[df["tournament"] == selected_tour]["match_id"].dropna().unique().tolist())
        selected_match = st.selectbox("🎯 Select Match ID", match_ids)

        teams = sorted(df[df["match_id"] == selected_match]["batting_team"].dropna().unique().tolist())
        selected_team = st.selectbox("🏏 Select Batting Team", teams)

        df = df[(df["tournament"] == selected_tour) &
                (df["match_id"] == selected_match) &
                (df["batting_team"] == selected_team)]

        if df.empty:
            st.warning("⚠️ No data available for this selection.")
            return

        # =======================================
        # 📈 TEAM SUMMARY KPIs
        # =======================================
        total_runs = df["total_runs"].sum()
        wickets = df["player_dismissed"].notnull().sum() if "player_dismissed" in df.columns else 0
        total_balls = len(df)
        overs = int(total_balls // 6)
        balls = int(total_balls % 6)
        display_overs = f"{overs}.{balls}"
        run_rate = round(total_runs / (total_balls / 6), 2) if total_balls > 0 else 0

        st.markdown("### 📈 Team Summary KPIs")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Runs", total_runs)
        c2.metric("Wickets", wickets)
        c3.metric("Overs", display_overs)
        c4.metric("Run Rate", run_rate)

        # =======================================
        # 📊 PHASE ANALYSIS
        # =======================================
        st.markdown("### 📊 Phase Analysis (Powerplay, Middle, Death)")

        df["phase"] = pd.cut(df["over"], bins=[-1, 5, 14, 19],
                             labels=["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"]).astype(str)

        phase_summary = df.groupby("phase").agg(
            Balls=("ball", "count"),
            Runs=("total_runs", "sum")
        ).reset_index()

        phase_summary["Strike Rate"] = (phase_summary["Runs"] / phase_summary["Balls"]) * 100
        phase_summary["Run Rate"] = (phase_summary["Runs"] / (phase_summary["Balls"] / 6))
        phase_summary["Dot %"] = ((df[df["total_runs"] == 0]
                                   .groupby("phase")["total_runs"].count()) / phase_summary["Balls"]) * 100
        phase_summary["Boundary %"] = ((df[df["total_runs"] >= 4]
                                        .groupby("phase")["total_runs"].count()) / phase_summary["Balls"]) * 100
        phase_summary = phase_summary.fillna(0)

        st.dataframe(phase_summary.style.format({
            "Runs": "{:.0f}", "Balls": "{:.0f}",
            "Strike Rate": "{:.2f}", "Run Rate": "{:.2f}",
            "Dot %": "{:.2f}", "Boundary %": "{:.2f}"
        }).background_gradient(cmap="YlOrBr", axis=None))

        # =======================================
        # 🧠 INSIGHTS + TOP PLAYERS (unchanged from v3)
        # =======================================
        st.markdown("### 🧠 Analyst Insights")
        st.info("Insights and performance highlights will appear here after filters.")

    else:
        st.info("👆 Please upload an Excel file to begin analysis.")

    st.markdown("""
    <div class='tb-footer'>
      Powered by <b style='color:#D4AF37;'>Talking Bat Analytics</b> © 2025 | All Rights Reserved
    </div>
    """, unsafe_allow_html=True)
