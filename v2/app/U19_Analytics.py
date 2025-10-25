import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# Optional PDF export (enabled automatically if reportlab is installed)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    PDF_OK = True
except Exception:
    PDF_OK = False


def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a copy with a robust, standard set of internal column names by
    auto-mapping typical headers used in your U-19 xlsx file.
    Works even if the source columns are Title Case or have spaces.
    """
    df = df.copy()
    original = list(df.columns)
    # Build a map like "match_id" -> "Match ID"
    colmap = {c.lower().strip().replace(" ", "_"): c for c in original}

    def pick(*cands):
        for c in cands:
            if c in colmap:
                return colmap[c]
        return None

    rename_map = {}
    # Core identifiers / filters
    t_col = pick("tournament")
    m_col = pick("match_id", "matchid")
    bt_col = pick("batting_team", "battingteam")
    bw_col = pick("bowling_team", "bowlingteam")

    # Ball/over structure
    over_col = pick("over")
    ball_col = pick("ball")

    # Scoring
    total_runs_col = pick("total_runs", "runs_total", "runs")
    batsman_runs_col = pick("batsman_runs")
    extra_runs_col = pick("extra_runs")

    # Participants
    batsman_col = pick("batsman", "striker")
    bowler_col = pick("bowler")

    # Dismissal / wickets
    dismissed_col = pick("player_dismissed", "dismissed_player")
    dismissal_kind_col = pick("dismissal_kind", "dismissal")

    # Delivery type
    ball_type_col = pick("ball_type", "delivery_type")
    bowler_type_col = pick("bowler_type")
    bowling_action_col = pick("bowling_action")

    # Friendly fallbacks (not all are required)
    mapping_candidates = {
        "tournament": t_col,
        "match_id": m_col,
        "batting_team": bt_col,
        "bowling_team": bw_col,
        "over": over_col,
        "ball": ball_col,
        "total_runs": total_runs_col,
        "batsman_runs": batsman_runs_col,
        "extra_runs": extra_runs_col,
        "batsman": batsman_col,
        "bowler": bowler_col,
        "player_dismissed": dismissed_col,
        "dismissal_kind": dismissal_kind_col,
        "ball_type": ball_type_col,
        "bowler_type": bowler_type_col,
        "bowling_action": bowling_action_col,
    }

    for std, real in mapping_candidates.items():
        if real:
            rename_map[real] = std

    df = df.rename(columns=rename_map)
    return df


def _legal_only(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to legal deliveries if 'ball_type' exists; otherwise pass through."""
    if "ball_type" in df.columns:
        return df[df["ball_type"].astype(str).str.lower() == "legal"].copy()
    return df.copy()


def _overs_string_from_balls(total_balls: int) -> str:
    ov = total_balls // 6
    balls = total_balls % 6
    return f"{ov}.{balls}"


def _phase_binning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'phase' using your definition:
      Powerplay 0–5, Middle 6–14, Death 15–19
    Assumes 'over' is 0-based in the data (typical ball-by-ball).
    """
    out = df.copy()
    if "over" not in out.columns:
        out["phase"] = "Unknown"
        return out

    out["phase"] = pd.cut(
        out["over"],
        bins=[-1, 5, 14, 19],
        labels=["Powerplay (0–5)", "Middle (6–14)", "Death (15–19)"]
    ).astype(str)  # avoid category fillna issues
    return out


def _batting_table(df: pd.DataFrame) -> pd.DataFrame:
    """Batting table: Runs, Balls, SR, Dot%, 4s, 6s for each batter."""
    if "batsman" not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    # Prefer batsman_runs if present; otherwise fall back to total_runs
    runs_src = "batsman_runs" if "batsman_runs" in tmp.columns else "total_runs"
    g = tmp.groupby("batsman").agg(
        Runs=(runs_src, "sum"),
        Balls=("ball", "count"),
        Dots=(runs_src, lambda x: (x == 0).sum()),
        Fours=(runs_src, lambda x: (x == 4).sum()),
        Sixes=(runs_src, lambda x: (x == 6).sum()),
    ).reset_index()
    g["SR"] = (g["Runs"] / g["Balls"] * 100).round(2).fillna(0)
    g["Dot%"] = (g["Dots"] / g["Balls"] * 100).round(2).fillna(0)
    return g.sort_values(["Runs", "SR"], ascending=[False, False])


def _bowling_table(df: pd.DataFrame) -> pd.DataFrame:
    """Bowling table: Balls, Runs, Wickets, Eco, Dot%."""
    if "bowler" not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    g = tmp.groupby("bowler").agg(
        Balls=("ball", "count"),
        Runs=("total_runs", "sum"),
        Wickets=("player_dismissed", lambda x: x.notna().sum() if pd.api.types.is_object_dtype(x) or pd.api.types.is_string_dtype(x) else int(x.sum()) ),
        Dots=("total_runs", lambda x: (x == 0).sum()),
    ).reset_index()
    g["Overs"] = (g["Balls"] / 6).round(1)
    g["Eco"] = (g["Runs"] / (g["Balls"] / 6).replace(0, 1)).round(2)
    g["Dot%"] = (g["Dots"] / g["Balls"] * 100).round(2)
    return g.sort_values(["Wickets", "Eco"], ascending=[False, True])


def _pace_spin_table(df: pd.DataFrame) -> pd.DataFrame:
    """Pace vs Spin summary if 'bowler_type' exists."""
    if "bowler_type" not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    g = tmp.groupby("bowler_type").agg(
        Balls=("ball", "count"),
        Runs=("total_runs", "sum"),
        Wkts=("player_dismissed", lambda x: x.notna().sum() if pd.api.types.is_object_dtype(x) or pd.api.types.is_string_dtype(x) else int(x.sum()) ),
        Dots=("total_runs", lambda x: (x == 0).sum()),
    ).reset_index()
    g["Eco"] = (g["Runs"] / (g["Balls"] / 6).replace(0, 1)).round(2)
    g["Dot%"] = (g["Dots"] / g["Balls"] * 100).round(2)
    return g.sort_values(["Eco"], ascending=True)


def _export_excel(ball_df, phase_df, bat_df, bowl_df, pace_spin_df) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        ball_df.to_excel(writer, index=False, sheet_name="Ball-by-Ball")
        phase_df.to_excel(writer, index=False, sheet_name="Phase Summary")
        if not bat_df.empty:
            bat_df.to_excel(writer, index=False, sheet_name="Batting")
        if not bowl_df.empty:
            bowl_df.to_excel(writer, index=False, sheet_name="Bowling")
        if not pace_spin_df.empty:
            pace_spin_df.to_excel(writer, index=False, sheet_name="Pace_vs_Spin")
    return output.getvalue()


def _export_pdf_simple(team_name: str, kpis: dict, phase_df: pd.DataFrame) -> bytes:
    """
    Minimal, compatible PDF (no external services). Creates a single-page summary
    with KPIs and phase table. Requires reportlab.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, f"Talking Bat – U-19 Report")
    y -= 0.8 * cm
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Team: {team_name}    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 0.6 * cm

    # KPIs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "KPIs")
    y -= 0.5 * cm
    c.setFont("Helvetica", 11)
    for k, v in kpis.items():
        c.drawString(2.4 * cm, y, f"- {k}: {v}")
        y -= 0.45 * cm

    # Phase table
    y -= 0.3 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Phase Summary")
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)

    cols = ["phase", "Balls", "Runs", "Strike Rate", "Run Rate", "Dot %", "Boundary %"]
    col_x = [2.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0]  # in cm
    # headers
    for cx, col in zip(col_x, cols):
        c.drawString(cx * cm, y, col)
    y -= 0.4 * cm

    for _, row in phase_df[cols].iterrows():
        if y < 2.0 * cm:
            c.showPage()
            y = height - 2 * cm
        for cx, col in zip(col_x, cols):
            c.drawString(cx * cm, y, str(row[col]))
        y -= 0.35 * cm

    c.showPage()
    c.save()
    return buf.getvalue()


def show_u19_analytics():
    # ============ PAGE CONFIG ============
    st.set_page_config(page_title="U-19 Analytics", page_icon="📊", layout="wide")

    # ============ THEME ============
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background:#ffffff; }
        .tb-header { text-align:center; padding:15px 10px; border-bottom:2px solid #D4AF37; margin-bottom:10px; }
        .tb-title { font-weight:700; font-size:28px; color:#D4AF37; letter-spacing:1px; }
        .hint { color:#666; font-size:14px; }
        .card { background:#fff8e1; border:1px solid #D4AF37; border-radius:12px; padding:10px; text-align:center; }
        .card h4 { color:#D4AF37; margin:0 0 6px 0; font-size:14px; }
        .card p { margin:2px; color:#333; font-size:13px; }
        .tb-footer { text-align:center; color:#777; margin-top:25px; padding-top:8px; border-top:1px solid #eee; font-size:13px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='tb-header'>
      <div class='tb-title'>📊 Talking Bat • U-19 Analytics</div>
      <p class='hint'>Tournament → Match → Team analysis on Women U-19 ball-by-ball data. White & Gold Pro theme.</p>
    </div>
    """, unsafe_allow_html=True)

    # ============ FILE UPLOAD & SESSION ============
    if "uploaded_data" not in st.session_state:
        st.session_state.uploaded_data = None

    uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file is not None:
        st.session_state.uploaded_data = uploaded_file
        st.success("✅ File uploaded successfully!")

    if st.session_state.uploaded_data is None:
        st.info("👆 Please upload your Women U-19 Excel file to start analysis.")
        st.markdown("<div class='tb-footer'>Powered by <b style='color:#D4AF37;'>Talking Bat Analytics</b> © 2025</div>", unsafe_allow_html=True)
        return

    # ============ LOAD & NORMALIZE ============
    raw = pd.read_excel(st.session_state.uploaded_data)
    df = _normalize_cols(raw)
    if "match_id" not in df.columns or "batting_team" not in df.columns:
        st.error("This file is missing required fields like Match ID or Batting Team.")
        return

    df = _legal_only(df)

    # ============ FILTERS (Tournament → Match → Team) ============
    # If tournament missing, create a default bucket
    if "tournament" not in df.columns:
        df["tournament"] = "All"

    tournaments = sorted(df["tournament"].dropna().unique().tolist())
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_tour = st.selectbox("🏆 Select Tournament", tournaments)
    with c2:
        match_ids = sorted(df[df["tournament"] == selected_tour]["match_id"].dropna().unique().tolist())
        selected_match = st.selectbox("🎯 Select Match ID", match_ids)
    with c3:
        teams = sorted(df[df["match_id"] == selected_match]["batting_team"].dropna().unique().tolist())
        selected_team = st.selectbox("🏏 Select Batting Team", teams)

    filt = df[(df["tournament"] == selected_tour) &
              (df["match_id"] == selected_match) &
              (df["batting_team"] == selected_team)].copy()

    if filt.empty:
        st.warning("⚠️ No data available for this selection.")
        return

    # ============ KPIs ============
    total_runs = filt["total_runs"].sum() if "total_runs" in filt.columns else 0
    total_balls = len(filt)
    overs_str = _overs_string_from_balls(total_balls)
    run_rate = round(total_runs / (total_balls / 6), 2) if total_balls else 0
    wickets = 0
    if "player_dismissed" in filt.columns:
        wickets = filt["player_dismissed"].notna().sum()

    st.markdown("### 📈 Team Summary KPIs")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Runs", total_runs)
    k2.metric("Wickets", int(wickets))
    k3.metric("Overs", overs_str)
    k4.metric("Run Rate", run_rate)

    # ============ PHASE ANALYSIS ============
    st.markdown("### 📊 Phase Analysis (Powerplay 0–5, Middle 6–14, Death 15–19)")
    phase_df = _phase_binning(filt)

    # preferred dot/4s/6s logic
    run_src = "batsman_runs" if "batsman_runs" in phase_df.columns else "total_runs"

    phase_summary = phase_df.groupby("phase").agg(
        Balls=("ball", "count"),
        Runs=("total_runs", "sum")
    ).reset_index()

    # Add dot and boundary counts
    dots = (phase_df[phase_df[run_src] == 0].groupby("phase")[run_src].count()).reindex(phase_summary["phase"]).fillna(0)
    bounds = (phase_df[phase_df[run_src] >= 4].groupby("phase")[run_src].count()).reindex(phase_summary["phase"]).fillna(0)

    phase_summary["Strike Rate"] = (phase_summary["Runs"] / phase_summary["Balls"] * 100).round(2).fillna(0)
    phase_summary["Run Rate"] = (phase_summary["Runs"] / (phase_summary["Balls"] / 6).replace(0, 1)).round(2)
    phase_summary["Dot %"] = (dots.values / phase_summary["Balls"] * 100).round(2)
    phase_summary["Boundary %"] = (bounds.values / phase_summary["Balls"] * 100).round(2)

    st.dataframe(
        phase_summary.style.format({
            "Runs": "{:.0f}", "Balls": "{:.0f}",
            "Strike Rate": "{:.2f}", "Run Rate": "{:.2f}",
            "Dot %": "{:.2f}", "Boundary %": "{:.2f}"
        }).background_gradient(cmap="YlOrBr", axis=None),
        use_container_width=True
    )

    # Charts row
    ch1, ch2, ch3 = st.columns(3)
    with ch1:
        fig1 = px.bar(
            phase_summary, x="phase", y="Runs", text="Runs",
            title="Runs by Phase", color="phase",
            color_discrete_sequence=["#D4AF37", "#EAD27A", "#F8F1C7"]
        )
        st.plotly_chart(fig1, use_container_width=True)
    with ch2:
        fig2 = px.line(
            phase_summary, x="phase", y="Strike Rate",
            markers=True, line_shape="spline",
            color_discrete_sequence=["#D4AF37"]
        )
        st.plotly_chart(fig2, use_container_width=True)
    with ch3:
        # Run Rate by over
        over_grp = filt.groupby("over").agg(Balls=("ball", "count"), Runs=("total_runs", "sum")).reset_index()
        over_grp["Run Rate"] = (over_grp["Runs"] / (over_grp["Balls"] / 6).replace(0, 1)).round(2)
        fig3 = px.line(
            over_grp, x="over", y="Run Rate", markers=True, line_shape="spline",
            title="Run Rate by Over", color_discrete_sequence=["#C89B3C"]
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ============ TABS: Batting / Bowling / Export ============
    tab_bat, tab_bowl, tab_export = st.tabs(["🏏 Batting", "🎯 Bowling", "📤 Export"])

    # ----- Batting tab -----
    with tab_bat:
        bat_df = _batting_table(filt)
        if bat_df.empty:
            st.info("No batting records found.")
        else:
            # Top 5 cards
            st.markdown("#### 🏅 Top 5 Batters (by Runs)")
            top5 = bat_df.head(5).reset_index(drop=True)
            cols = st.columns(len(top5))
            for i, row in top5.iterrows():
                fours = int(row.get("Fours", 0))
                sixes = int(row.get("Sixes", 0))
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class='card'>
                            <h4>{row['batsman']}</h4>
                            <p><b>Runs:</b> {int(row['Runs'])}</p>
                            <p><b>SR:</b> {row['SR']}</p>
                            <p><b>Dot%:</b> {row['Dot%']}</p>
                            <p><b>4s/6s:</b> {fours}/{sixes}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("#### 📋 Batting Table")
            st.dataframe(bat_df, use_container_width=True)

    # ----- Bowling tab -----
    with tab_bowl:
        bowl_df = _bowling_table(filt)
        if bowl_df.empty:
            st.info("No bowling records found.")
        else:
            st.markdown("#### 🏅 Top 5 Bowlers (by Wickets)")
            top5b = bowl_df.head(5).reset_index(drop=True)
            cols = st.columns(len(top5b))
            for i, row in top5b.iterrows():
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class='card'>
                            <h4>{row['bowler']}</h4>
                            <p><b>Wkts:</b> {int(row['Wickets'])}</p>
                            <p><b>Eco:</b> {row['Eco']}</p>
                            <p><b>Dot%:</b> {row['Dot%']}</p>
                            <p><b>Balls:</b> {int(row['Balls'])}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("#### 📋 Bowling Table")
            st.dataframe(bowl_df, use_container_width=True)

            # Pace vs Spin
            pace_spin_df = _pace_spin_table(filt)
            if not pace_spin_df.empty:
                st.markdown("#### 🌀 Pace vs Spin")
                st.dataframe(pace_spin_df, use_container_width=True)
                fig_ps = px.bar(
                    pace_spin_df, x="bowler_type", y="Eco",
                    title="Economy by Bowler Type", text="Eco",
                    color="bowler_type", color_discrete_sequence=["#D4AF37", "#EAD27A", "#F8F1C7", "#C89B3C"]
                )
                st.plotly_chart(fig_ps, use_container_width=True)

    # ----- Export tab -----
    with tab_export:
        st.markdown("#### 📦 Download Reports")
        # For export, also keep the pace/spin table we just computed (recompute safely if needed).
        pace_spin_df = _pace_spin_table(filt)

        excel_bytes = _export_excel(
            ball_df=filt,
            phase_df=phase_summary,
            bat_df=_batting_table(filt),
            bowl_df=_bowling_table(filt),
            pace_spin_df=pace_spin_df
        )
        st.download_button(
            "⬇️ Download Excel (Multi-sheet)",
            data=excel_bytes,
            file_name=f"{selected_team}_{selected_tour}_{selected_match}_Analytics.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if PDF_OK:
            kpis = {
                "Runs": total_runs,
                "Wickets": int(wickets),
                "Overs": overs_str,
                "Run Rate": run_rate
            }
            pdf_bytes = _export_pdf_simple(selected_team, kpis, phase_summary)
            st.download_button(
                "⬇️ Download PDF Summary",
                data=pdf_bytes,
                file_name=f"{selected_team}_{selected_tour}_{selected_match}_Summary.pdf",
                mime="application/pdf"
            )
        else:
            st.info("To enable PDF export, add `reportlab` to v2/requirements.txt and redeploy.")

    # ============ INSIGHTS ============
    st.markdown("### 🧠 Analyst Insights (auto)")
    try:
        pp_sr = float(phase_summary.loc[phase_summary["phase"] == "Powerplay (0–5)", "Strike Rate"].values[0])
    except Exception:
        pp_sr = 0.0
    try:
        mid_sr = float(phase_summary.loc[phase_summary["phase"] == "Middle (6–14)", "Strike Rate"].values[0])
    except Exception:
        mid_sr = 0.0
    try:
        death_rr = float(phase_summary.loc[phase_summary["phase"] == "Death (15–19)", "Run Rate"].values[0])
    except Exception:
        death_rr = 0.0

    bullets = []
    bullets.append("✅ Powerplay momentum is healthy." if pp_sr >= 100 else "🔻 Powerplay SR below par — consider boundary intent/strike rotation.")
    bullets.append("✅ Middle overs rotation is stable." if mid_sr >= 85 else "⚠️ Middle overs SR low — improve singles-to-dots ratio.")
    bullets.append("💥 Death overs finishing is strong." if death_rr >= 8 else "🚨 Death overs run rate low — review finishing plans.")

    for b in bullets:
        st.markdown(f"- {b}")

    # Footer
    st.markdown("<div class='tb-footer'>Powered by <b style='color:#D4AF37;'>Talking Bat Analytics</b> © 2025</div>", unsafe_allow_html=True)
