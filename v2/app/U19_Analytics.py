import streamlit as st
import pandas as pd
import plotly.express as px

def show_u19_analytics():
    # =======================================
    # ⚙️ PAGE SETTINGS
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

    # =======================================
    # 🏏 HEADER
    # =======================================
    st.markdown("""
    <div class='tb-header'>
      <div class='tb-title'>📊 Talking Bat • U-19 Analytics</div>
      <p style='color:#666; font-size:14px;'>Upload your Women U-19 Ball-by-Ball dataset to view detailed performance insights.</p>
    </div>
    """, unsafe_allow_html=True)

    # =======================================
    # 📁 FILE UPLOAD (Persist Session)
    # =======================================
    if "uploaded_data" not in st.session_state:
        st.session_state.uploaded_data = None

    uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        st.session_state.uploaded_data = uploaded_file
        st.success("✅ File uploaded successfully!")

    # =======================================
    # 📊 ANALYTICS SECTION
    # =======================================
    if st.session_state.uploaded_data is not None:
        df = pd.read_excel(st.session_state.uploaded_data)

        # Clean columns (case-insensitive)
        df.columns = [c.strip().lower() for c in df.columns]

        # Only legal deliveries
        if "ball_type" in df.columns:
            df = df[df["ball_type"].str.lower() == "legal"]

        # Match filter (optional if multiple)
        if "match_id" in df.columns:
            match_ids = df["match_id"].unique().tolist()
            selected_match = st.selectbox("🎯 Select Match", match_ids)
            df = df[df["match_id"] == selected_match]

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
        # 🏏 PHASE ANALYSIS
        # =======================================
        st.markdown("### 📊 Phase Analysis (Powerplay, Middle, Death)")

        df["phase"] = pd.cut(
            df["over"],
            bins=[-1, 5, 14, 19],
            labels=["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"]
        )

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
            "Runs": "{:.0f}",
            "Balls": "{:.0f}",
            "Strike Rate": "{:.2f}",
            "Run Rate": "{:.2f}",
            "Dot %": "{:.2f}",
            "Boundary %": "{:.2f}"
        }).background_gradient(cmap="YlOrBr", axis=None))

        # =======================================
        # 📊 CHARTS
        # =======================================
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(
                phase_summary,
                x="phase",
                y="Runs",
                text="Runs",
                title="Runs by Phase",
                color="phase",
                color_discrete_sequence=["#D4AF37", "#EAD27A", "#F8F1C7"]
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(
                phase_summary,
                x="phase",
                y="Strike Rate",
                markers=True,
                line_shape="spline",
                color_discrete_sequence=["#D4AF37"]
            )
            fig2.update_traces(texttemplate='%{y:.1f}', textposition='top center')
            st.plotly_chart(fig2, use_container_width=True)

        # =======================================
        # 🧠 ANALYST INSIGHTS
        # =======================================
        st.markdown("### 🧠 Analyst Insights")

        pp_sr = phase_summary.loc[phase_summary["phase"] == "Powerplay (0–5)", "Strike Rate"].values[0]
        mid_sr = phase_summary.loc[phase_summary["phase"] == "Middle (6–14)", "Strike Rate"].values[0]
        death_rr = phase_summary.loc[phase_summary["phase"] == "Death (15–19)", "Run Rate"].values[0]

        insights = []
        if pp_sr < 100:
            insights.append("🔻 Powerplay scoring rate is below par — consider stronger openers or boundary options.")
        else:
            insights.append("✅ Powerplay momentum is strong — good strike rate up front.")

        if mid_sr < 85:
            insights.append("⚠️ Middle overs need better rotation and strike rotation strategy.")
        else:
            insights.append("✅ Middle overs show good control and acceleration.")

        if death_rr < 8:
            insights.append("🚨 Death overs run rate is low — finishing phase needs improvement.")
        else:
            insights.append("💥 Death overs show strong finishing power.")

        for line in insights:
            st.markdown(line)

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
