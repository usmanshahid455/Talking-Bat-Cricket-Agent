import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# 🧠 HEADER SECTION
# ==========================================================
st.set_page_config(page_title="Talking Bat U-19 Analytics", layout="wide")

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize all headers automatically so variations like 'Match ID',
    'match id', or 'match-id' all become 'match_id'. Handles spaces, case,
    dashes, invisible chars, and punctuation.
    """
    df = df.copy()
    
    # Normalize columns: lowercase, replace spaces/dashes with underscores
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"[\s\-\u2013\u2014]+", "_", regex=True)
        .str.replace(r"[^\w_]", "", regex=True)
        .str.lower()
    )
    
    # Apply consistent naming dictionary
    rename_map = {
        "matchid": "match_id",
        "match_id": "match_id",
        "innings": "innings",
        "over": "over",
        "ball": "ball",
        "battingstyle": "batting_style",
        "batsman": "batsman",
        "nonstriker": "non_striker",
        "bowler": "bowler",
        "bowlingaction": "bowling_action",
        "bowlertype": "bowler_type",
        "batsmanruns": "batsman_runs",
        "dismissalkind": "dismissal_kind",
        "balltype": "ball_type",
        "extraruns": "extra_runs",
        "feetname": "feet_name",
        "shotname": "shot_name",
        "deliveryname": "delivery_name",
        "connectionname": "connection_name",
        "totalruns": "total_runs",
        "battingteam": "batting_team",
        "bowlingteam": "bowling_team",
        "playerdismissed": "player_dismissed",
        "year": "year",
        "tournament": "tournament",
        "venue": "venue",
        "date": "date",
    }

    df = df.rename(columns=rename_map)
    return df

# ==========================================================
# 🏏 MAIN ANALYTICS FUNCTION
# ==========================================================
def show_u19_analytics():
    st.markdown(
        "<h3 style='color:#D4AF37;'>📊 Talking Bat • U-19 Analytics</h3>"
        "<p style='color:#777;'>Tournament → Match → Team analysis on Women U-19 ball-by-ball data. "
        "White & Gold Pro theme.</p>",
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])
    if not uploaded:
        st.info("👆 Please upload an Excel file to begin analysis.")
        return

    # Read Excel and normalize
    try:
        df = pd.read_excel(uploaded)
        df = _normalize_cols(df)
    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
        return

    if df.empty:
        st.warning("⚠️ Uploaded file is empty.")
        return

    # Ensure required columns exist
    required_cols = ["tournament", "match_id", "batting_team", "total_runs", "bowler", "batsman_runs", "over"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        return

    st.success("✅ File uploaded successfully!")

    # ==========================================================
    # 🎯 DROPDOWNS — FILTER CONTROLS
    # ==========================================================
    col1, col2, col3 = st.columns(3)

    with col1:
        tournaments = sorted(df["tournament"].dropna().unique())
        tournament = st.selectbox("🏆 Select Tournament", tournaments)

    with col2:
        matches = sorted(df.loc[df["tournament"] == tournament, "match_id"].dropna().unique())
        match = st.selectbox("🎯 Select Match ID", matches)

    with col3:
        teams = sorted(df.loc[df["match_id"] == match, "batting_team"].dropna().unique())
        team = st.selectbox("🏏 Select Batting Team", teams)

    if not all([tournament, match, team]):
        st.warning("⚠️ Please select all filters above.")
        return

    # Filtered data
    data = df[(df["tournament"] == tournament) & (df["match_id"] == match) & (df["batting_team"] == team)]
    if data.empty:
        st.warning("⚠️ No data available for this selection.")
        return

    # ==========================================================
    # 📈 KPIs SECTION
    # ==========================================================
    total_runs = data["total_runs"].sum()
    wickets = data["player_dismissed"].notna().sum()
    overs = data["over"].max() + (data["ball"].max() / 6)
    run_rate = total_runs / overs if overs > 0 else 0

    st.markdown("<h4 style='color:#D4AF37;'>📈 Team Summary KPIs</h4>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Runs", f"{total_runs}")
    k2.metric("Wickets", f"{wickets}")
    k3.metric("Overs", f"{overs:.1f}")
    k4.metric("Run Rate", f"{run_rate:.2f}")

    # ==========================================================
    # 📊 PHASE-WISE ANALYSIS (Powerplay, Middle, Death)
    # ==========================================================
    def get_phase(over):
        if over <= 5:
            return "Powerplay (0–5)"
        elif over <= 14:
            return "Middle (6–14)"
        else:
            return "Death (15–19)"

    data["phase"] = data["over"].apply(get_phase)

    phase_summary = (
        data.groupby("phase")[["total_runs", "batsman_runs"]]
        .sum()
        .assign(balls=data.groupby("phase")["ball"].count())
    )
    phase_summary["Strike Rate"] = (phase_summary["batsman_runs"] / phase_summary["balls"]) * 100
    phase_summary = phase_summary.reset_index()

    st.markdown("<h4 style='color:#D4AF37;'>📊 Phase Analysis (Powerplay, Middle, Death)</h4>", unsafe_allow_html=True)
    fig = px.bar(
        phase_summary,
        x="phase",
        y="Strike Rate",
        color="phase",
        text_auto=".1f",
        color_discrete_sequence=["#D4AF37", "#C0C0C0", "#8B8000"],
        title="Strike Rate by Phase",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # 🎯 ANALYST INSIGHTS
    # ==========================================================
    st.markdown(
        """
        <div style='padding:10px 15px; border:1px solid #D4AF37; border-radius:10px; margin-top:10px;'>
        <h4 style='color:#D4AF37;'>🧠 Analyst Insights</h4>
        <ul style='color:#666; line-height:1.7;'>
        <li>Powerplay control and middle-over strike rate are crucial for batting momentum.</li>
        <li>Death overs consistency in dot reduction increases total run potential.</li>
        <li>Use phase data to plan bowler matchups and batting tempo per game segment.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='tb-footer' style='text-align:center; color:#777; margin-top:30px; "
        "border-top:1px solid #eee; padding-top:8px; font-size:13px;'>"
        "Powered by <span style='color:#D4AF37; font-weight:600;'>Talking Bat Analytics</span> © 2025 | All Rights Reserved</div>",
        unsafe_allow_html=True,
    )
