import streamlit as st
import pandas as pd
from utils import GOLD, NAVY, INK

def show_u19_analytics():
    st.markdown(f"<h3 style='color:{GOLD};'>📊 Women U-19 Analytics</h3>", unsafe_allow_html=True)
    st.caption("Upload your ball-by-ball Excel file to view player & team insights.")

    file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])

    if not file:
        st.info("Please upload your Excel file first.")
        return

    try:
        df = pd.read_excel(file)
        st.success("✅ File loaded successfully!")

        # ---------- BASIC CLEANUP ----------
        df.columns = [c.strip().lower() for c in df.columns]

        # Expected columns
        expected_cols = ["batsman", "bowler", "innings", "over", "ball",
                         "batsman_runs", "dismissal_kind", "bowling_team",
                         "batting_team", "ball_type", "extra_runs"]
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            st.warning(f"⚠️ Missing columns: {missing}")

        # ---------- KPIs ----------
        st.markdown(f"<h4 style='color:{NAVY};margin-top:10px;'>🏏 Batting KPIs</h4>", unsafe_allow_html=True)
        bat = (
            df.groupby("batsman")
            .agg(
                Runs=("batsman_runs", "sum"),
                Balls=("ball", "count"),
                Dots=("batsman_runs", lambda x: (x == 0).sum()),
                Fours=("batsman_runs", lambda x: (x == 4).sum()),
                Sixes=("batsman_runs", lambda x: (x == 6).sum()),
            )
            .reset_index()
        )
        bat["SR"] = (bat["Runs"] / bat["Balls"] * 100).round(1)
        bat["Dot%"] = (bat["Dots"] / bat["Balls"] * 100).round(1)
        bat["Bnd%"] = ((bat["Fours"] + bat["Sixes"]) / bat["Balls"] * 100).round(1)
        bat["BPB"] = (bat["Balls"] / (bat["Fours"] + bat["Sixes"]).replace(0, 1)).round(1)

        st.dataframe(
            bat.sort_values("Runs", ascending=False).style
            .highlight_max(subset=["Runs"], color="#fdf5e6")
            .set_table_styles(
                [{"selector": "th", "props": [("background-color", GOLD), ("color", NAVY)]}]
            ),
            use_container_width=True,
        )

        # ---------- BOWLING ----------
        st.markdown(f"<h4 style='color:{NAVY};margin-top:20px;'>🎯 Bowling KPIs</h4>", unsafe_allow_html=True)
        bowl = (
            df.groupby("bowler")
            .agg(
                Runs=("batsman_runs", "sum"),
                Balls=("ball", "count"),
                Wickets=("dismissal_kind", lambda x: (x != "none").sum()),
                Dots=("batsman_runs", lambda x: (x == 0).sum()),
            )
            .reset_index()
        )
        bowl["Overs"] = (bowl["Balls"] / 6).round(1)
        bowl["Eco"] = (bowl["Runs"] / bowl["Overs"]).round(2)
        bowl["Dot%"] = (bowl["Dots"] / bowl["Balls"] * 100).round(1)
        bowl["BPD"] = (bowl["Balls"] / bowl["Wickets"].replace(0, 1)).round(1)

        st.dataframe(
            bowl.sort_values("Wickets", ascending=False).style
            .highlight_max(subset=["Wickets"], color="#fdf5e6")
            .set_table_styles(
                [{"selector": "th", "props": [("background-color", GOLD), ("color", NAVY)]}]
            ),
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
