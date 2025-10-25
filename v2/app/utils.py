import os, requests, streamlit as st

# ====== Global Settings ======
API_BASE = "https://api.cricapi.com/v1"
API_KEY = st.secrets.get("CRICKETDATA_API_KEY", os.getenv("CRICKETDATA_API_KEY", ""))
REFRESH = int(st.secrets.get("REFRESH_SECONDS", os.getenv("REFRESH_SECONDS", "30")))

# ====== Talking Bat Pro UI Colours ======
NAVY = "#0B3C66"
GOLD = "#D4AF37"
INK = "#0E1525"
GREY = "#6B7280"
BORDER = "#D7DBE2"

# ====== API Call ======
def api_get(path: str, params=None):
    if params is None:
        params = {}
    params["apikey"] = API_KEY
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

# ====== CSS ======
def style_css():
    st.markdown(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

      html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background: #FFFFFF;
        color: {INK};
      }}

      /* Header */
      .tb-header {{
        text-align: center;
        padding: 18px 10px 6px 10px;
        border-bottom: 2px solid {GOLD};
        background: {NAVY};
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      }}

      .tb-logo {{
        width: 48px; height: 48px;
        object-fit: contain;
        display:block;
        margin: 0 auto 8px auto;
      }}

      .tb-title {{
        font-weight: 700;
        font-size: 28px;
        letter-spacing: 0.5px;
        color: {GOLD};
        text-shadow: 0 0 5px rgba(212,175,55,0.3);
      }}

      /* Navigation Buttons */
      .tb-nav {{
        text-align:center;
        margin: 10px 0 4px 0;
      }}
      .tb-nav a button {{
        background: #ffffff;
        border: 2px solid {GOLD};
        color: {INK};
        border-radius: 14px;
        padding: 6px 14px;
        margin: 3px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
      }}
      .tb-nav a button:hover {{
        background: {GOLD};
        color: white;
        box-shadow: 0 0 8px {GOLD}99;
      }}

      /* Card / Box */
      .tb-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
      }}

      /* Footer */
      .tb-footer {{
        text-align:center;
        color:{GREY};
        margin-top: 20px;
        padding: 8px;
        border-top: 1px solid {BORDER};
        font-size: 13px;
      }}

      /* Loading shimmer */
      @keyframes shimmer {{
        0% {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
      }}
      .shimmer {{
        height: 4px;
        background: linear-gradient(90deg, #eee 25%, {GOLD} 50%, #eee 75%);
        background-size: 800px 100%;
        animation: shimmer 2s infinite;
        margin: 10px 0;
      }}
    </style>
    """, unsafe_allow_html=True)

# ====== Auto Refresh ======
def auto_refresh():
    st.markdown(f"<meta http-equiv='refresh' content='{REFRESH}'>", unsafe_allow_html=True)

# ====== Header ======
def header():
    style_css()
    st.markdown(f"""
    <div class='tb-header'>
        <img class='tb-logo' src='talkingbat_logo.png' alt='Talking Bat'>
        <div class='tb-title'>Talking Bat</div>
        <div class='tb-nav'>
            <a href='?page=live'><button>🏏 Live</button></a>
            <a href='?page=fixtures'><button>📅 Fixtures</button></a>
            <a href='?page=results'><button>✅ Results</button></a>
            <a href='?page=scorecard'><button>📋 Scorecard</button></a>
        </div>
        <div class='shimmer'></div>
    </div>
    """, unsafe_allow_html=True)
