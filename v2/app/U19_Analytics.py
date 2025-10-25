# /v2/app/U19_Analytics.py

import re
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ======================= THEME =======================
PRIMARY = "#002B5B"   # Deep navy
ACCENT  = "#3A506B"   # Muted blue
LTGRAY  = "#EAEAEA"   # Light gray
WHITE   = "#FFFFFF"

def _inject_css():
    st.markdown(
        f"""
        <style>
        /* Page base */
        .main, .block-container {{
          padding-top: 0.6rem;
          padding-bottom: 0.6rem;
        }}

        /* Cards & headers */
        .tb-card {{
          background: {WHITE};
          border: 1px solid {LTGRAY};
          border-radius: 12px;
          padding: 10px 14px;
          margin: 8px 0;
          box-shadow: 0 1px 2px rgba(0,0,0,.04);
        }}
        .tb-title {{
          color: {PRIMARY};
          font-weight: 700;
          margin: 0;
        }}
        .tb-sub {{
          color: #5a6b7b;
          margin: 2px 0 0 0;
          font-size: 14px;
        }}
        .tb-h4 {{ color: {PRIMARY}; margin: 6px 0 8px; }}
        .tb-mute {{ color: #708090; }}

        /* Compact metrics */
        div[data-testid="stMetric"] {{
          background: {WHITE};
          border: 1px solid {LTGRAY};
          border-radius: 10px;
          padding: 6px 8px;
          text-align: center;
        }}
        div[data-testid="stMetric"] label p {{
          margin-bottom: 2px !important;
          color: {ACCENT} !important;
          font-weight: 600;
          text-align: center !important;
        }}
        div[data-testid="stMetricValue"] {{
          font-size: 22px !important;
          text-align: center !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] button {{
          font-weight: 600;
          color: {PRIMARY};
        }}

        /* Center table headers & cells */
        .tb-table table {{
          width: 100%;
          border-collapse: collapse;
        }}
        .tb-table th, .tb-table td {{
          border: 1px solid {LTGRAY};
          padding: 6px 8px;
          text-align: center;      /* center cells */
          vertical-align: middle;
          font-size: 13px;
        }}
        .tb-table th {{
          background: #f7f9fc;
          color: {PRIMARY};
          font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Helper: center-aligned HTML table (so Streamlit keeps alignment)
def _html_table(df: pd.DataFrame, index=False) -> str:
    return (
        "<div class='tb-table'>"
        + df.to_html(index=index, escape=False)
        + "</div>"
    )

# ===================== COLUMN NORMALIZATION =====================
def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
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
    return df.rename(columns=rename_map)

# =========================== UTILS ==============================
LEGAL_EXTRAS = {"wd", "wide", "nb", "noball", "no_ball"}

def is_legal(ball_type: str) -> bool:
    if ball_type is None or (isinstance(ball_type, float) and np.isnan(ball_type)):
        return True
    t = str(ball_type).strip().lower()
    return t not in LEGAL_EXTRAS

def over_from_balls(balls: int) -> float:
    return balls // 6 + (balls % 6) / 6.0

def phase_from_over(over: int) -> str:
    if over <= 5:
        return "Powerplay (0–5)"
    elif over <= 14:
        return "Middle (6–14)"
    else:
        return "Death (15–19)"

PACE_KEYS = ["fast", "medium", "rm", "rf", "lm", "lf", "rmf", "lmf", "rmed", "lmed", "pace"]
SPIN_KEYS = ["off break", "offbreak", "ob", "leg break", "legbreak", "lb", "orthodox",
             "sla", "slow left", "chinaman", "left arm unorthodox", "lao", "spin"]

def coarse_type(action: str, btype: str) -> str:
    txt = f"{str(action).lower()} {str(btype).lower()}"
    if any(k in txt for k in SPIN_KEYS): return "Spin"
    if any(k in txt for k in PACE_KEYS): return "Pace"
    if re.search(r"(break|orthodox|chinaman|spin)", txt): return "Spin"
    if re.search(r"(fast|medium|rmf|lmf|pace)", txt): return "Pace"
    return "Other"

# ===================== CACHED READER ============================
@st.cache_data(show_spinner=False)
def _read_and_prepare(file) -> pd.DataFrame:
    df = pd.read_excel(file)
    df = _normalize_cols(df)

    # Numeric coercions
    for c in ["over", "ball", "batsman_runs", "total_runs"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # String trims
    for c in ["tournament","match_id","batting_team","bowling_team","batsman","bowler",
              "ball_type","bowling_action","bowler_type","dismissal_kind","player_dismissed","batting_style"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df

# =========================== MAIN ===============================
def show_u19_analytics():
    st.set_page_config(page_title="U-19 Analytics", page_icon="📊", layout="wide")
    _inject_css()

    st.markdown(
        f"""
        <div class="tb-card">
          <h3 class="tb-title">📊 Talking Bat • U-19 Analytics</h3>
          <p class="tb-sub">Tournament → Match → Team analysis • Compact blue theme • Center-aligned tables</p>
        </div>
        """, unsafe_allow_html=True
    )

    uploaded = st.file_uploader("📂 Upload Excel File", type=["xlsx","xls"])
    if not uploaded:
        st.info("👆 Please upload your Women U-19 ball-by-ball Excel.")
        return

    try:
        df = _read_and_prepare(uploaded)
    except Exception as e:
        st.error(f"❌ Failed to read Excel: {e}")
        return

    # Checks
    required = ["tournament","match_id","batting_team","total_runs","over","ball","batsman","bowler","ball_type"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"❌ Missing columns: {missing}")
        return

    st.success("✅ File uploaded & parsed successfully!")

    # Filters
    c1, c2, c3 = st.columns(3)
    with c1:
        tours = sorted(df["tournament"].dropna().unique().tolist())
        selected_tour = st.selectbox("🏆 Select Tournament", tours)
    with c2:
        mids = sorted(df.loc[df["tournament"] == selected_tour, "match_id"].dropna().unique().tolist())
        selected_match = st.selectbox("🎯 Select Match ID", mids)
    with c3:
        teams = sorted(df.loc[(df["tournament"] == selected_tour) & (df["match_id"] == selected_match),
                              "batting_team"].dropna().unique().tolist())
        selected_team = st.selectbox("🏏 Select Batting Team", teams)

    dsel = df[(df["tournament"] == selected_tour) &
              (df["match_id"] == selected_match) &
              (df["batting_team"] == selected_team)].copy()

    if dsel.empty:
        st.warning("⚠️ No data for this selection.")
        return

    # Legal + Phase
    dsel["is_legal"] = dsel["ball_type"].apply(is_legal)
    dsel["phase"] = dsel["over"].apply(phase_from_over)

    # ================= KPIs =================
    legal = dsel[dsel["is_legal"]]
    balls = int(legal.shape[0])
    overs_val = over_from_balls(balls)
    runs = int(dsel["total_runs"].sum())
    wkts = int(dsel["player_dismissed"].replace(["", "nan", "None"], np.nan).notna().sum())
    rr = (runs / overs_val) if overs_val > 0 else 0.0

    st.markdown(f"<h4 class='tb-h4'>📈 Team Summary KPIs</h4>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns([1,1,1,1])
    k1.metric("Total Runs", runs)
    k2.metric("Wickets", wkts)
    k3.metric("Overs", f"{overs_val:.1f}")
    k4.metric("Run Rate", f"{rr:.2f}")

    # =============== Phase Analysis ===============
    phase = (
        dsel.groupby("phase", as_index=False)
            .agg(runs=("total_runs","sum"),
                 balls=("is_legal", lambda s: int(s.sum())),
                 bat_runs=("batsman_runs","sum"))
    )
    if not phase.empty:
        phase["SR"] = np.where(phase["balls"]>0, phase["bat_runs"]*100/phase["balls"], 0.0)
        order = ["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"]
        phase["phase"] = pd.Categorical(phase["phase"], order, ordered=True)
        phase = phase.sort_values("phase")

        st.markdown(f"<h4 class='tb-h4'>📊 Phase Analysis</h4>", unsafe_allow_html=True)
        cA, cB, cC = st.columns(3)

        with cA:
            fig1 = px.bar(
                phase, x="phase", y="runs", text_auto=True,
                title="Runs by Phase",
                color="phase",
                color_discrete_sequence=[PRIMARY, ACCENT, "#5C7A99"]
            )
            fig1.update_layout(showlegend=False, margin=dict(l=10,r=10,t=40,b=10))
            fig1.update_traces(hovertemplate="Phase: %{x}<br>Runs: %{y}")
            st.plotly_chart(fig1, use_container_width=True)

        with cB:
            fig2 = px.line(
                phase, x="phase", y="SR", markers=True,
                title="Strike Rate by Phase",
                color_discrete_sequence=[PRIMARY]
            )
            fig2.update_layout(margin=dict(l=10,r=10,t=40,b=10), hovermode="x unified")
            fig2.update_traces(hovertemplate="Phase: %{x}<br>SR: %{y:.1f}")
            st.plotly_chart(fig2, use_container_width=True)

        with cC:
            # RR by over
            og = dsel[dsel["is_legal"]].groupby("over", as_index=False)\
                    .agg(B=("is_legal","sum"), R=("total_runs","sum"))
            if not og.empty:
                og["RR"] = np.where(og["B"]>0, og["R"]/(og["B"]/6), 0.0)
                fig3 = px.line(
                    og, x="over", y="RR", markers=True,
                    title="Run Rate by Over",
                    color_discrete_sequence=[ACCENT]
                )
                fig3.update_layout(margin=dict(l=10,r=10,t=40,b=10), hovermode="x unified")
                fig3.update_traces(hovertemplate="Over: %{x}<br>RR: %{y:.2f}")
                st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ================= TABS =================
    tab_bat, tab_bowl, tab_matchups = st.tabs(["🏏 Batting", "🎯 Bowling", "🔄 Match-ups"])

    # -------- Batting --------
    with tab_bat:
        bat = dsel.copy()
        bat["legal_ball"] = bat["is_legal"] & (bat["batsman_runs"] >= 0)
        batters = (
            bat.groupby("batsman", as_index=False)
               .agg(R=("batsman_runs","sum"),
                    B=("legal_ball","sum"),
                    Fours=("batsman_runs", lambda s: int((s==4).sum())),
                    Sixes=("batsman_runs", lambda s: int((s==6).sum())),
                    Dots=("batsman_runs", lambda s: int((s==0).sum())))
        )
        if batters.empty:
            st.info("No batting records.")
        else:
            batters["SR"] = np.where(batters["B"]>0, batters["R"]*100/batters["B"], 0.0)
            batters["Dot%"] = np.where(batters["B"]>0, batters["Dots"]*100/batters["B"], 0.0)
            bat_top = batters.sort_values(["R","SR"], ascending=[False, False]).head(5)
            st.markdown("<div class='tb-card'><b>Top 5 Batters</b></div>", unsafe_allow_html=True)

            table = bat_top.rename(columns={"batsman":"Batsman"})[["Batsman","R","B","Fours","Sixes","SR","Dot%"]]
            st.markdown(_html_table(table), unsafe_allow_html=True)

    # -------- Bowling --------
    with tab_bowl:
        bwl = dsel.copy()
        bwl["dot"] = (bwl["total_runs"]==0) & bwl["is_legal"]
        bowlers = (
            bwl.groupby("bowler", as_index=False)
               .agg(B=("is_legal","sum"),
                    R=("total_runs","sum"),
                    W=("player_dismissed", lambda s: int(s.replace(["","nan","None"], np.nan).notna().sum())),
                    Dots=("dot","sum"))
        )
        if bowlers.empty:
            st.info("No bowling records.")
        else:
            bowlers["O"] = bowlers["B"].apply(over_from_balls)
            bowlers["Econ"] = np.where(bowlers["O"]>0, bowlers["R"]/bowlers["O"], 0.0)
            bowlers["SR"] = np.where(bowlers["W"]>0, bowlers["B"]/bowlers["W"], np.nan)
            bowlers["Dot%"] = np.where(bowlers["B"]>0, bowlers["Dots"]*100/bowlers["B"], 0.0)
            bowl_top = bowlers.sort_values(["W","Econ"], ascending=[False, True]).head(5)
            st.markdown("<div class='tb-card'><b>Top 5 Bowlers</b></div>", unsafe_allow_html=True)

            table = bowl_top.rename(columns={"bowler":"Bowler"})[["Bowler","O","R","W","Econ","SR","Dot%"]]
            st.markdown(_html_table(table), unsafe_allow_html=True)

            # Pace vs Spin
            dsel["coarse"] = dsel.apply(
                lambda r: coarse_type(r.get("bowling_action",""), r.get("bowler_type","")), axis=1
            )
            by_coarse = (
                dsel.groupby("coarse", as_index=False)
                    .agg(B=("is_legal","sum"),
                         R=("total_runs","sum"),
                         bat_runs=("batsman_runs","sum"),
                         Dots=("total_runs", lambda s: int((s==0).sum())))
            )
            if not by_coarse.empty:
                by_coarse["SR"] = np.where(by_coarse["B"]>0, by_coarse["bat_runs"]*100/by_coarse["B"], 0.0)
                by_coarse["Dot%"] = np.where(by_coarse["B"]>0, by_coarse["Dots"]*100/by_coarse["B"], 0.0)
                st.markdown("<div class='tb-card'><b>Pace vs Spin</b></div>", unsafe_allow_html=True)
                cPS1, cPS2 = st.columns(2)
                with cPS1:
                    fig_ps1 = px.bar(
                        by_coarse, x="coarse", y="R", text_auto=True,
                        title="Runs vs Pace/Spin",
                        color="coarse",
                        color_discrete_sequence=[PRIMARY, ACCENT, "#5C7A99"]
                    )
                    fig_ps1.update_layout(showlegend=False, margin=dict(l=10,r=10,t=40,b=10))
                    fig_ps1.update_traces(hovertemplate="Type: %{x}<br>Runs: %{y}")
                    st.plotly_chart(fig_ps1, use_container_width=True)
                with cPS2:
                    fig_ps2 = px.bar(
                        by_coarse, x="coarse", y="Dot%", text_auto=".1f",
                        title="Dot% vs Pace/Spin",
                        color="coarse",
                        color_discrete_sequence=[PRIMARY, ACCENT, "#5C7A99"]
                    )
                    fig_ps2.update_layout(showlegend=False, margin=dict(l=10,r=10,t=40,b=10))
                    fig_ps2.update_traces(hovertemplate="Type: %{x}<br>Dot%: %{y:.1f}%")
                    st.plotly_chart(fig_ps2, use_container_width=True)

            # Bowling Action (top 10)
            actions = (
                dsel.groupby("bowling_action", as_index=False)
                    .agg(B=("is_legal","sum"),
                         R=("total_runs","sum"),
                         bat_runs=("batsman_runs","sum"),
                         Dots=("total_runs", lambda s: int((s==0).sum())))
                    .sort_values("R", ascending=False)
                    .head(10)
            )
            if not actions.empty:
                actions["SR"]  = np.where(actions["B"]>0, actions["bat_runs"]*100/actions["B"], 0.0)
                actions["Dot%"] = np.where(actions["B"]>0, actions["Dots"]*100/actions["B"], 0.0)
                st.markdown("<div class='tb-card'><b>Bowling Action Breakdown (Top 10)</b></div>", unsafe_allow_html=True)
                table = actions.rename(columns={"bowling_action":"Action"})[["Action","B","R","SR","Dot%"]]
                st.markdown(_html_table(table), unsafe_allow_html=True)

    # -------- Match-ups --------
    with tab_matchups:
        st.markdown("<div class='tb-card'><b>Match-ups Dashboard</b></div>", unsafe_allow_html=True)
        mu_tabs = st.tabs(["👥 Batter vs Bowler", "🧩 Batter vs Bowling Action", "🫲 Bowler vs Batting Style (RHB/LHB)"])

        # Batter vs Bowler
        with mu_tabs[0]:
            g = dsel.copy()
            g["legal_ball"] = g["is_legal"]
            pair = (g.groupby(["batsman","bowler"], as_index=False)
                      .agg(R=("batsman_runs","sum"),
                           B=("legal_ball","sum"),
                           Dots=("batsman_runs", lambda s: int((s==0).sum()))))
            g["dismiss_flag"] = (g["player_dismissed"].replace(["","nan","None"], np.nan).fillna("") == g["batsman"])
            dism = g.groupby(["batsman","bowler"], as_index=False)["dismiss_flag"].sum().rename(columns={"dismiss_flag":"Wkts"})
            pair = pair.merge(dism, on=["batsman","bowler"], how="left").fillna({"Wkts":0})
            if pair.empty:
                st.info("No pair data.")
            else:
                pair["SR"] = np.where(pair["B"]>0, pair["R"]*100/pair["B"], 0.0)
                pair["Dot%"] = np.where(pair["B"]>0, pair["Dots"]*100/pair["B"], 0.0)
                show = pair.sort_values(["R","SR"], ascending=[False, False]).head(30)
                show = show.rename(columns={"batsman":"Batsman","bowler":"Bowler"})
                st.markdown(_html_table(show), unsafe_allow_html=True)

        # Batter vs Bowling Action
        with mu_tabs[1]:
            if "bowling_action" not in dsel.columns:
                st.info("No bowling_action column found.")
            else:
                a = dsel.copy()
                a["legal_ball"] = a["is_legal"]
                act = (a.groupby(["batsman","bowling_action"], as_index=False)
                         .agg(R=("batsman_runs","sum"),
                              B=("legal_ball","sum"),
                              Dots=("batsman_runs", lambda s: int((s==0).sum()))))
                a["dismiss_flag"] = a["player_dismissed"].replace(["","nan","None"], np.nan).notna()
                dism2 = a.groupby(["batsman","bowling_action"], as_index=False)["dismiss_flag"].sum().rename(columns={"dismiss_flag":"Wkts"})
                act = act.merge(dism2, on=["batsman","bowling_action"], how="left").fillna({"Wkts":0})
                if act.empty:
                    st.info("No action data.")
                else:
                    act["SR"] = np.where(act["B"]>0, act["R"]*100/act["B"], 0.0)
                    act["Dot%"] = np.where(act["B"]>0, act["Dots"]*100/act["B"], 0.0)
                    show = act.sort_values(["R","SR"], ascending=[False, False]).head(30)
                    show = show.rename(columns={"batsman":"Batsman","bowling_action":"Action"})
                    st.markdown(_html_table(show), unsafe_allow_html=True)

        # Bowler vs Batting Style (RHB/LHB)
        with mu_tabs[2]:
            if "batting_style" not in dsel.columns:
                st.info("No batting_style column found.")
            else:
                b = dsel.copy()
                b["legal_ball"] = b["is_legal"]
                b["bat_style"] = b["batting_style"].str.upper().str.extract(r"(RHB|LHB)")[0].fillna("UNK")
                vs_style = (b.groupby(["bowler","bat_style"], as_index=False)
                              .agg(B=("legal_ball","sum"),
                                   R=("total_runs","sum"),
                                   W=("player_dismissed", lambda s: int(s.replace(['','nan','None'], np.nan).notna().sum())),
                                   Dots=("total_runs", lambda s: int((s==0).sum()))))
                if vs_style.empty:
                    st.info("No style data.")
                else:
                    vs_style["O"] = vs_style["B"].apply(over_from_balls)
                    vs_style["Econ"] = np.where(vs_style["O"]>0, vs_style["R"]/vs_style["O"], 0.0)
                    vs_style["Dot%"] = np.where(vs_style["B"]>0, vs_style["Dots"]*100/vs_style["B"], 0.0)
                    vs_style["SR(balls/w)"] = np.where(vs_style["W"]>0, vs_style["B"]/vs_style["W"], np.nan)
                    show = vs_style.rename(columns={"bowler":"Bowler","bat_style":"Vs Style"})
                    st.markdown(_html_table(show), unsafe_allow_html=True)

    # ============== Analyst Insights ==============
    st.markdown("<h4 class='tb-h4'>🧠 Analyst Insights</h4>", unsafe_allow_html=True)
    bullets = []
    try:
        pp_sr = float(phase.loc[phase["phase"]=="Powerplay (0–5)","SR"].values[0]); bullets.append(f"Powerplay SR: <b>{pp_sr:.1f}</b>")
    except Exception: pass
    try:
        mid_sr = float(phase.loc[phase["phase"]=="Middle (6–14)","SR"].values[0]); bullets.append(f"Middle SR: <b>{mid_sr:.1f}</b>")
    except Exception: pass
    try:
        death_sr = float(phase.loc[phase["phase"]=="Death (15–19)","SR"].values[0]); bullets.append(f"Death SR: <b>{death_sr:.1f}</b>")
    except Exception: pass

    items = (
        ['Keep middle-overs Dot% under <b>35%</b> to sustain RR.',
         'Use action match-ups to unlock boundary options.',
         'Exploit highest-run bowler type from Pace/Spin summary.']
        + ([' • '.join(bullets)] if bullets else [])
    )
    st.markdown(
        "<div class='tb-card tb-mute' style='line-height:1.7'><ul><li>" +
        "</li><li>".join(items) + "</li></ul></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div class='tb-mute' style='text-align:center; margin-top:8px;'>"
        f"Powered by <b style='color:{PRIMARY};'>Talking Bat Analytics</b> © 2025</div>",
        unsafe_allow_html=True
    )
