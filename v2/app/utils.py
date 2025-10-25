import os, requests, streamlit as st

API_BASE = "https://api.cricapi.com/v1"
API_KEY = st.secrets.get("CRICKETDATA_API_KEY", os.getenv("CRICKETDATA_API_KEY", ""))
REFRESH = int(st.secrets.get("REFRESH_SECONDS", os.getenv("REFRESH_SECONDS", "30")))
GOLD = "#D4AF37"

def api_get(path: str, params=None):
    if params is None: params = {}
    params["apikey"] = API_KEY
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def style_css():
    st.markdown(f"""<style>
      @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
      html, body, [class*="css"]  {{
        font-family: 'Poppins', sans-serif;
        background: #ffffff;
      }}
      .tb-header {{
        text-align:center;
        padding: 18px 10px 8px 10px;
        border-bottom: 2px solid {GOLD}33;
        margin-bottom: 10px;
      }}
      .tb-title {{
        font-weight: 700;
        font-size: 28px;
        color: {GOLD};
        letter-spacing: .5px;
      }}
      .tb-nav {{
        text-align:center;
        margin: 6px 0;
      }}
      .tb-nav a button {{
        background: white;
        border: 2px solid {GOLD};
        color: #333;
        border-radius: 14px;
        padding: 6px 10px;
        margin: 4px;
        cursor: pointer;
      }}
      .tb-nav a button:hover {{
        background: {GOLD}11;
      }}
      .tb-footer {{
        text-align:center;
        color:#777;
        margin-top: 20px;
        padding-top: 6px;
        border-top: 1px solid #eee;
        font-size: 13px;
      }}
      .tb-logo {{
        width: 44px; height: 44px; object-fit: contain; display:block; margin: 0 auto 6px auto;
      }}
    </style>""", unsafe_allow_html=True)

def auto_refresh():
    st.markdown(f"<meta http-equiv='refresh' content='{REFRESH}'>", unsafe_allow_html=True)

def header():
    style_css()
    st.markdown("""<div class='tb-header'>
      <img class='tb-logo' src='talkingbat_logo.png' alt='Talking Bat'>
      <div class='tb-title'>Talking Bat</div>
      <div class='tb-nav'>
        <a href='?page=live'><button>🏏 Live</button></a>
        <a href='?page=fixtures'><button>📅 Fixtures</button></a>
        <a href='?page=results'><button>✅ Results</button></a>
        <a href='?page=scorecard'><button>📋 Scorecard</button></a>
      </div>
    </div>""", unsafe_allow_html=True)
