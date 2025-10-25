import streamlit as st
import pandas as pd
from utils import set_page, top_nav, footer, get_scorecard, empty_state, card

set_page()
st.title("📋 Scorecard")
top_nav(active="scorecard")

match_id = st.text_input("Enter Match ID (from your provider):", value="")
go = st.button("Fetch Scorecard", use_container_width=True)
if go and match_id.strip():
    data = get_scorecard(match_id.strip())
    if "error" in data:
        empty_state("Could not fetch scorecard. Check the Match ID, API key & base URL in utils.py")
    else:
        innings = data.get("innings") or data.get("scorecard") or []
        if not innings:
            empty_state("No scorecard data returned.")
        else:
            for inn in innings:
                title = inn.get("name") or inn.get("team") or "Innings"
                def body():
                    # Try to render batting/bowling tables if present
                    bat = inn.get("batting") or []
                    bowl = inn.get("bowling") or []
                    if bat:
                        st.markdown("**Batting**")
                        st.dataframe(pd.DataFrame(bat))
                    if bowl:
                        st.markdown("**Bowling**")
                        st.dataframe(pd.DataFrame(bowl))
                    # Raw pane
                    with st.expander("Raw innings JSON"):
                        st.json(inn)
                card(title, body=body, subtitle=inn.get("status",""))
else:
    st.caption("Provide a valid Match ID, then click **Fetch Scorecard**.")

footer()