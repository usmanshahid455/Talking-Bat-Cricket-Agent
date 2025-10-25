import streamlit as st
import pandas as pd
import plotly.express as px


def show_u19_analytics():
    st.set_page_config(page_title="U-19 Analytics", page_icon="📊", layout="wide")

    st.title("📊 U-19 Analytics Dashboard")
    st.markdown("Upload your **Women U-19 ball-by-ball dataset (.xlsx)** to view player and team analytics.")

    uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Data uploaded successfully!")

        # Preview data
        with st.expander("🔍 Preview Dataset"):
            st.dataframe(df.head())

        # ========================
        # 🏏 KPIs Section
        # ========================
        st.markdown("### 📈 Team Summary KPIs")
        total_runs = df["total_runs"].sum()
        wickets = df["player_dismissed"].count()
        overs = df["over"].max()
        run_rate = round(total_runs / overs, 2) if overs else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Runs", total_runs)
        c2.metric("Wickets", wickets)
        c3.metric("Overs", overs)
        c4.metric("Run Rate", run_rate)

        # ========================
        # 📊 Charts
        # ========================
        st.markdown("### 📊 Phase Analysis (Powerplay, Middle, Death)")
        df["phase"] = pd.cut(df["over"], bins=[0, 6, 15, 20], labels=["Powerplay", "Middle", "Death"])
        phase_stats = df.groupby("phase")["total_runs"].sum().reset_index()

        fig = px.bar(
            phase_stats,
            x="phase",
            y="total_runs",
            text="total_runs",
            title="Runs by Phase",
            color="phase",
            color_discrete_sequence=["#D4AF37", "#EAD27A", "#F8F1C7"],
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### ⚡ Strike Rate by Phase")
        df["balls_faced"] = 1
        sr_phase = df.groupby("phase").agg({"total_runs": "sum", "balls_faced": "count"})
        sr_phase["Strike Rate"] = (sr_phase["total_runs"] / sr_phase["balls_faced"]) * 100
        fig2 = px.line(
            sr_phase,
            x=sr_phase.index,
            y="Strike Rate",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#D4AF37"],
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ========================
        # 🔍 Insights
        # ========================
        st.markdown("### 🧠 Analyst Insights")
        st.write("- Powerplay control and middle-over strike rate are crucial for batting momentum.")
        st.write("- Death overs consistency in dot reduction increases total run potential.")
        st.write("- Use phase data to plan bowler matchups and batting tempo per game segment.")

    else:
        st.info("👆 Please upload an Excel file to begin analysis.")
