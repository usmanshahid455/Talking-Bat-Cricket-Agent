# /v2/app/U19_Analytics.py

import re
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------
# THEME HELPERS (White & Gold)
# -----------------------------------------------------------
GOLD = "#D4AF37"

def _inject_css():
    st.markdown(
        f"""
        <style>
        .tb-card {{
            border:1px solid {GOLD}55; border-radius:14px; padding:14px 16px; margin:8px 0; background:#fff;
        }}
        .tb-h4 {{ color:{GOLD}; margin:6px 0 10px 0; }}
        .tb-mute {{ color:#666; }}
        .metric-row div[data-testid="stMetricValue"] {{ font-size:22px; }}
        .stTabs [data-baseweb="tab-list"] button {{ font-weight:600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------
# COLUMN NORMALIZATION
# -----------------------------------------------------------
def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize headers so 'Match ID' / 'match-id' / 'match id' => 'match_id'.
    Also removes punctuation and fixes odd unicode spaces/dashes.
    """
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"[\s\-\u2013\u2014]+", "_", regex=True)
        .str.replace(r"[^\w_]", "", regex=True)
        .str.lower()
    )

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

# -----------------------------------------------------------
# UTILS
# -----------------------------------------------------------
LEGAL_EXTRAS = {"wd", "wide", "nb", "noball", "no_ball"}

def is_legal(ball_type: str) -> bool:
    if ball_type is None or (isinstance(ball_type, float) and np.isnan(ball_type)):
        return True
    t = str(ball_type).strip().lower()
    return t not in LEGAL_EXTRAS

def over_from_balls(balls: int) -> float:
    return balls // 6 + (balls % 6) / 6.0

def phase_from_over(over: int) -> str:
    # 0-5, 6-14, 15-19  (you asked for Death 16-19 but T20 overs are 0..19;
    # specifying 15–19 keeps death as last 5 overs; adjust to 16–19 if needed)
    if over <= 5:
        return "Powerplay (0–5)"
    elif over <= 14:
        return "Middle (6–14)"
    else:
        return "Death (15–19)"

PACE_KEYS = [
    "fast", "medium", "rm", "rf", "lm", "lf", "rmf", "lmf", "rmed", "lmed", "pace"
]
SPIN_KEYS = [
    "off break", "offbreak", "ob", "leg break", "legbreak", "lb", "orthodox",
    "sla", "slow left", "chinaman", "left arm unorthodox", "lao", "spin"
]

def coarse_type(action: str, btype: str) -> str:
    txt = f"{str(action).lower()} {str(btype).lower()}"
    if any(k in txt for k in SPIN_KEYS):
        return "Spin"
    if any(k in txt for k in PACE_KEYS):
        return "Pace"
    # Fallback: if only 'break/orthodox' etc → Spin
    if re.search(r"(break|orthodox|chinaman|spin)", txt):
        return "Spin"
    if re.search(r"(fast|medium|rmf|lmf|pace)", txt):
        return "Pace"
    return "Unknown"

# -----------------------------------------------------------
# CACHING THE UPLOAD (survives page changes)
# -----------------------------------------------------------
@st.cache_data(show_spinner=False)
def _read_and_prepare(file) -> pd.DataFrame:
    df = pd.read_excel(file)
    df = _normalize_cols(df)
    # coerce numeric fields
    for c in ["over", "ball", "batsman_runs", "total_runs"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    # string trims
    for c in ["tournament", "match_id", "batting_team", "bowling_team",
              "batsman", "bowler", "ball_type", "bowling_action", "bowler_type",
              "dismissal_kind", "player_dismissed"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df

# -----------------------------------------------------------
# MAIN ENTRY
# -----------------------------------------------------------
def show_u19_analytics():
    _inject_css()

    st.markdown(
        f"""
        <div class='tb-card'>
          <h3 class='tb-h4'>📊 Talking Bat • U-19 Analytics</h3>
          <div class='tb-mute'>Tournament → Match → Team analysis on Women U-19 ball-by-ball data.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    up = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])
    if not up:
        st.info("👆 Please upload your Women U-19 ball-by-ball Excel.")
        return

    try:
        df = _read_and_prepare(up)
    except Exception as e:
        st.error(f"❌ Failed to read Excel: {e}")
        return

    # sanity check
    required = ["tournament", "match_id", "batting_team", "total_runs", "over", "ball",
                "batsman", "bowler", "bowling_action", "bowler_type", "ball_type"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"❌ Missing columns: {missing}")
        return

    st.success("✅ File uploaded & parsed successfully!")

    # FILTERS
    c1, c2, c3 = st.columns(3)
    with c1:
        t_list = sorted(df["tournament"].dropna().unique().tolist())
        tournament = st.selectbox("🏆 Select Tournament", t_list)
    with c2:
        m_list = sorted(df.loc[df["tournament"] == tournament, "match_id"].dropna().unique().tolist())
        match = st.selectbox("🎯 Select Match ID", m_list)
    with c3:
        team_list = sorted(df.loc[(df["tournament"] == tournament) & (df["match_id"] == match),
                                  "batting_team"].dropna().unique().tolist())
        team = st.selectbox("🏏 Select Batting Team", team_list)

    dsel = df[(df["tournament"] == tournament) & (df["match_id"] == match) & (df["batting_team"] == team)].copy()
    if dsel.empty:
        st.warning("⚠️ No data for this selection.")
        return

    # Precompute legality and phase
    dsel["is_legal"] = dsel["ball_type"].apply(is_legal)
    dsel["phase"] = dsel["over"].apply(phase_from_over)

    # ---------------- KPIs ----------------
    legal = dsel[dsel["is_legal"]]
    balls = int(legal.shape[0])
    overs = over_from_balls(balls)
    runs = int(dsel["total_runs"].sum())
    wkts = int(dsel["player_dismissed"].replace(["", "nan", "None"], np.nan).notna().sum())
    rr = (runs / overs) if overs > 0 else 0.0

    st.markdown(f"<h4 class='tb-h4'>📈 Team Summary KPIs</h4>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Total Runs", runs)
    with k2: st.metric("Wickets", wkts)
    with k3: st.metric("Overs", f"{overs:.1f}")
    with k4: st.metric("Run Rate", f"{rr:.2f}")

    # ---------------- PHASE ANALYSIS ----------------
    phase = (
        dsel.groupby("phase", as_index=False)
            .agg(runs=("total_runs", "sum"),
                 balls=("is_legal", lambda s: int(s.sum())),
                 bat_runs=("batsman_runs", "sum"))
    )
    if not phase.empty:
        phase["SR"] = np.where(phase["balls"] > 0, phase["bat_runs"] * 100 / phase["balls"], 0.0)
        order = ["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"]
        phase["phase"] = pd.Categorical(phase["phase"], order, ordered=True)
        phase = phase.sort_values("phase")

        st.markdown(f"<h4 class='tb-h4'>📊 Phase Analysis</h4>", unsafe_allow_html=True)
        cA, cB = st.columns(2)
        with cA:
            fig1 = px.bar(
                phase, x="phase", y="runs", text_auto=True,
                color="phase", title="Runs by Phase",
                color_discrete_sequence=[GOLD, "#C0C0C0", "#8B8000"],
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        with cB:
            fig2 = px.line(
                phase, x="phase", y="SR", markers=True,
                title="Strike Rate by Phase",
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ---------------- TOP BATTERS & BOWLERS ----------------
    st.markdown(f"<h4 class='tb-h4'>⭐ Top Performers</h4>", unsafe_allow_html=True)
    tb, bw = st.columns(2)

    # Top 5 Batters
    bat = dsel.copy()
    bat["legal_ball"] = bat["is_legal"] & (bat["batsman_runs"] >= 0)
    batters = (
        bat.groupby("batsman", as_index=False)
           .agg(R=("batsman_runs", "sum"),
                B=("legal_ball", "sum"),
                Fours=("batsman_runs", lambda s: int((s == 4).sum())),
                Sixes=("batsman_runs", lambda s: int((s == 6).sum())),
                Dots=("batsman_runs", lambda s: int((s == 0).sum())))
    )
    if not batters.empty:
        batters["SR"] = np.where(batters["B"] > 0, batters["R"] * 100 / batters["B"], 0.0)
        batters["Dot%"] = np.where(batters["B"] > 0, batters["Dots"] * 100 / batters["B"], 0.0)
        batters_top = batters.sort_values(["R", "SR"], ascending=[False, False]).head(5)
        with tb:
            st.markdown("<div class='tb-card'><b>Top 5 Batters</b></div>", unsafe_allow_html=True)
            st.dataframe(
                batters_top[["batsman", "R", "B", "Fours", "Sixes", "SR", "Dot%"]]
                .rename(columns={"batsman": "Batsman"}), use_container_width=True
            )

    # Top 5 Bowlers (against the batting team)
    bowl = dsel.copy()
    # dot ball when total_runs==0 AND legal
    bowl["dot"] = (bowl["total_runs"] == 0) & bowl["is_legal"]
    bowlers = (
        bowl.groupby("bowler", as_index=False)
            .agg(B=("is_legal", "sum"),
                 R=("total_runs", "sum"),
                 W=("player_dismissed", lambda s: int(s.replace(["", "nan", "None"], np.nan).notna().sum())),
                 Dots=("dot", "sum"))
    )
    if not bowlers.empty:
        bowlers["O"] = bowlers["B"].apply(over_from_balls)
        bowlers["Econ"] = np.where(bowlers["O"] > 0, bowlers["R"] / bowlers["O"], 0.0)
        bowlers["SR"] = np.where(bowlers["W"] > 0, bowlers["B"] / bowlers["W"], np.nan)
        bowlers["Dot%"] = np.where(bowlers["B"] > 0, bowlers["Dots"] * 100 / bowlers["B"], 0.0)
        bowlers_top = bowlers.sort_values(["W", "Econ"], ascending=[False, True]).head(5)
        with bw:
            st.markdown("<div class='tb-card'><b>Top 5 Bowlers</b></div>", unsafe_allow_html=True)
            st.dataframe(
                bowlers_top[["bowler", "O", "R", "W", "Econ", "SR", "Dot%"]]
                .rename(columns={"bowler": "Bowler"}), use_container_width=True
            )

    # ---------------- PACE vs SPIN & ACTION BREAKDOWN ----------------
    st.markdown(f"<h4 class='tb-h4'>🎯 Pace vs Spin & Action Breakdown</h4>", unsafe_allow_html=True)
    ab1, ab2 = st.columns(2)

    dsel["coarse"] = dsel.apply(
        lambda r: coarse_type(r.get("bowling_action", ""), r.get("bowler_type", "")), axis=1
    )

    by_coarse = (
        dsel.groupby("coarse", as_index=False)
            .agg(B=("is_legal", "sum"),
                 R=("total_runs", "sum"),
                 bat_runs=("batsman_runs", "sum"),
                 Dots=("total_runs", lambda s: int((s == 0).sum())))
    )
    if not by_coarse.empty:
        by_coarse["SR"] = np.where(by_coarse["B"] > 0, by_coarse["bat_runs"] * 100 / by_coarse["B"], 0.0)
        by_coarse["Dot%"] = np.where(by_coarse["B"] > 0, by_coarse["Dots"] * 100 / by_coarse["B"], 0.0)
        by_coarse = by_coarse.replace({"coarse": {"Unknown": "Other"}})

        with ab1:
            fig3 = px.bar(by_coarse, x="coarse", y="R", text_auto=True,
                          title="Runs vs Pace/Spin", color="coarse",
                          color_discrete_sequence=[GOLD, "#9b59b6", "#95a5a6"])
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
        with ab2:
            fig4 = px.bar(by_coarse, x="coarse", y="Dot%", text_auto=".1f",
                          title="Dot% vs Pace/Spin", color="coarse",
                          color_discrete_sequence=[GOLD, "#9b59b6", "#95a5a6"])
            fig4.update_layout(showlegend=False, yaxis_ticksuffix="%")
            st.plotly_chart(fig4, use_container_width=True)

    # Fine-grained action table
    actions = (
        dsel.groupby("bowling_action", as_index=False)
            .agg(B=("is_legal", "sum"),
                 R=("total_runs", "sum"),
                 bat_runs=("batsman_runs", "sum"),
                 Dots=("total_runs", lambda s: int((s == 0).sum())))
            .sort_values("R", ascending=False)
            .head(10)
    )
    if not actions.empty:
        actions["SR"] = np.where(actions["B"] > 0, actions["bat_runs"] * 100 / actions["B"], 0.0)
        actions["Dot%"] = np.where(actions["B"] > 0, actions["Dots"] * 100 / actions["B"], 0.0)
        st.markdown("<div class='tb-card'><b>Bowling Action Breakdown (Top 10)</b></div>", unsafe_allow_html=True)
        st.dataframe(
            actions.rename(columns={"bowling_action": "Action"})[["Action", "B", "R", "SR", "Dot%"]],
            use_container_width=True
        )

    # ---------------- ANALYST INSIGHTS ----------------
    insight_points = []
    try:
        pp = phase.loc[phase["phase"] == "Powerplay (0–5)", "SR"].values
        md = phase.loc[phase["phase"] == "Middle (6–14)", "SR"].values
        dt = phase.loc[phase["phase"] == "Death (15–19)", "SR"].values
        if len(pp): insight_points.append(f"Powerplay SR: <b>{pp[0]:.1f}</b>")
        if len(md): insight_points.append(f"Middle SR: <b>{md[0]:.1f}</b>")
        if len(dt): insight_points.append(f"Death SR: <b>{dt[0]:.1f}</b>")
    except Exception:
        pass

    if not by_coarse.empty:
        best = by_coarse.sort_values("R", ascending=False).iloc[0]
        insight_points.append(f"Most productive style: <b>{best['coarse']}</b> (Runs: <b>{int(best['R'])}</b>)")

    st.markdown(
        f"""
        <div class='tb-card'>
          <h4 class='tb-h4'>🧠 Analyst Insights</h4>
          <ul class='tb-mute' style='line-height:1.7'>
            <li>Maintain dots below <b>35%</b> in the middle overs to lift innings RR.</li>
            <li>Target weaker bowling actions from the breakdown table for matchups.</li>
            <li>{' • '.join(insight_points) if insight_points else 'Phase & style signals will appear after selections.'}</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Footer
    st.markdown(
        f"<div class='tb-mute' style='text-align:center; margin-top:12px;'>"
        f"Powered by <span style='color:{GOLD}; font-weight:600;'>Talking Bat Analytics</span> © 2025</div>",
        unsafe_allow_html=True,
    )
