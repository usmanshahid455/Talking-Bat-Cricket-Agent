# Talking Bat — Cricket AI Agent (Web App)

A ready-to-launch Streamlit app that shows **all international matches**:
- 🔴 Live matches (status, quick score, open scorecard)
- 📅 Fixtures (upcoming)
- ✅ Results (recent completed)
- 📋 Scorecards by match ID

Auto-refresh supported; data comes live from **CricketData**.

---

## 1) One-time Setup (Streamlit Cloud — easiest)

1. Go to https://share.streamlit.io/ and sign in.
2. Create a new app from this folder (upload to a GitHub repo or directly via "Deploy from a GitHub repo").
3. In Streamlit Cloud, open **App → Settings → Secrets**, and paste the contents of `secrets_template.toml` into the secrets editor.
   - It already contains your API key.

4. Press **Deploy**. Your app will be live at a URL like:
   `https://talkingbat-cricket-ai-agent.streamlit.app`

---

## 2) Local Run (optional)

```bash
pip install -r requirements.txt
streamlit run app/Home.py
```

If running locally, you can set the API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:CRICKETDATA_API_KEY="0d0e9880-a9c6-45a2-b622-792d04bf67a5"
```

**macOS/Linux:**
```bash
export CRICKETDATA_API_KEY="0d0e9880-a9c6-45a2-b622-792d04bf67a5"
```

Or use Streamlit secrets locally by creating a file `.streamlit/secrets.toml` and pasting the template.

---

## 3) Notes & Next Steps

- This MVP calls public endpoints directly from the browser session.
- For subscriptions/payments and historical storage, we’ll add a backend & database later.
- You can change branding in `app/Home.py` (title, logo, colors).

Need help deploying? Ping me and I’ll walk you through it.
