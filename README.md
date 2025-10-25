# Talking Bat v2

Mobile-friendly Streamlit app with emoji top navigation (🏏 📅 ✅ 📋), 30s auto-refresh on live/feeds,
and a sticky footer: **“Powered by Talking Bat © 2025”**.

## Structure
```text
v2/
├─ app/
│  ├─ Home.py
│  ├─ Live.py
│  ├─ Fixtures.py
│  ├─ Results.py
│  ├─ Scorecard.py
│  └─ utils.py
├─ .streamlit/
│  └─ secrets_template.toml
├─ requirements.txt
└─ README.md
```

## Quick Start

1) **Install**
```bash
pip install -r requirements.txt
```

2) **Secrets**  
   Copy `.streamlit/secrets_template.toml` to `.streamlit/secrets.toml` and keep it private.
   Update with your CricketData API key if needed.

3) **Run**
```bash
streamlit run app/Home.py
```

4) **Endpoints**  
   In `app/utils.py` update `BASE` and the endpoint paths (`/v1/live`, `/v1/fixtures`, `/v1/results`, `/v1/scorecard/{id}`)
   to match your actual CricketData provider. The app is coded to handle common response shapes.

## Notes
- **Mobile-friendly**: CSS tweaks for smaller screens, responsive tables, compact cards.
- **Emoji nav**: Four-pill top navigation (🏏 Home, 📅 Fixtures, ✅ Results, 📋 Scorecard).
- **Auto-refresh**: Live, Fixtures, Results pages refresh every 30 seconds.
- **Footer**: Sticky footer with the required text.
- **Security**: Never commit your real `secrets.toml` to any repo. Keep it local or use Streamlit Cloud secrets.