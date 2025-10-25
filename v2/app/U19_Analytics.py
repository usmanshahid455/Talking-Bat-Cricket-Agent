import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def show_u19_analytics():
    # =======================================
    # ⚙️ PAGE CONFIG
    # =======================================
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
        df.columns = [c.strip().lower() for c in df.columns]

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
        wickets = df["player_dismissed"].notnull().sum()
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
        # 🏅 TOP BATTERS & BOWLERS
        # =======================================
        st.markdown("### 🏅 Top Performers")

        if "batsman" in df.columns:
            top_batters = (
                df.groupby("batsman")["total_runs"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )
            st.markdown("#### 🏏 Top 5 Batters")
            cols = st.columns(5)
            for i, row in top_batters.iterrows():
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class='card'>
                            <h4>{row['batsman']}</h4>
                            <p><b>Runs:</b> {int(row['total_runs'])}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        if "bowler" in df.columns:
            top_bowlers = (
                df.groupby("bowler")["player_dismissed"]
                .count()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )
            st.markdown("#### 🎯 Top 5 Bowlers")
            cols = st.columns(5)
            for i, row in top_bowlers.iterrows():
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class='card'>
                            <h4>{row['bowler']}</h4>
                            <p><b>Wickets:</b> {int(row['player_dismissed'])}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # =======================================
        # 🧠 ANALYST INSIGHTS
        # =======================================
        st.markdown("### 🧠 Analyst Insights")

        try:
            pp_sr = phase_summary.loc[phase_summary["phase"] == "Powerplay (0–5)", "Strike Rate"].values[0]
            mid_sr = phase_summary.loc[phase_summary["phase"] == "Middle (6–14)", "Strike Rate"].values[0]
            death_rr = phase_summary.loc[phase_summary["phase"] == "Death (15–19)", "Run Rate"].values[0]
        except IndexError:
            pp_sr = mid_sr = death_rr = 0

        insights = []
        if pp_sr < 100:
            insights.append("🔻 Powerplay scoring rate is below par — strengthen opening combination.")
        else:
            insights.append("✅ Powerplay momentum strong — good boundary conversion.")

        if mid_sr < 85:
            insights.append("⚠️ Middle overs need better rotation & strike control.")
        else:
            insights.append("✅ Middle overs show solid rotation efficiency.")

        if death_rr < 8:
            insights.append("🚨 Death overs run rate low — finishing phase needs improvement.")
        else:
            insights.append("💥 Death overs show aggressive finishing potential.")

        for line in insights:
            st.markdown(line)

        # =======================================
        # 📤 EXPORT SECTION
        # =======================================
        st.markdown("### 📤 Export Data")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Ball-by-Ball")
            phase_summary.to_excel(writer, index=False, sheet_name="Phase Summary")
            top_batters.to_excel(writer, index=False, sheet_name="Top Batters")
            top_bowlers.to_excel(writer, index=False, sheet_name="Top Bowlers")
        excel_data = output.getvalue()
        st.download_button("⬇️ Download Excel Report", data=excel_data,
                           file_name=f"{selected_team}_Analytics_Report.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    else:
        st.info("👆 Please upload an Excel file to begin analysis.")

    # =======================================
    # ⚓ FOOTER
    # =======================================
    st.markdown("""
    <div class='tb-footer'>
      Powered by <b style='color:#D4AF37;'>Talking Bat Analytics</b> © 2025 | All Rights Reserved
    </div>
    """, unsafe_allow_html=True)
