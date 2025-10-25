# Talking Bat v2 — White & Gold Edition

Mobile-friendly Streamlit app for live international cricket data.
- Emoji top navigation (🏏 📅 ✅ 📋)
- Auto-refresh every 30s
- White background with gold accent (#D4AF37)
- Footer: Powered by Talking Bat © 2025

## Deploy
1) Upload this folder to your GitHub repo.
2) In Streamlit Cloud, set:
   - Repository: <your-username>/Talking-Bat-Cricket-Agent
   - Branch: main
   - Main file path: v2/app/Home.py
3) In **App → Settings → Secrets**, paste:
```
CRICKETDATA_API_KEY = "0d0e9880-a9c6-45a2-b622-792d04bf67a5"
REFRESH_SECONDS = "30"
```
4) Deploy.
