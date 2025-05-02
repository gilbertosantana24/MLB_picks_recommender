import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
import os

from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

st.set_page_config(page_title="Slider picks", page_icon="⚾", layout="wide")
st.title("⚾ MLB Picks Recommender ⚾")

def get_date_strings():
    now = datetime.now(pytz.timezone('America/Los_Angeles'))
    return now.strftime("%Y-%m-%d"), now.strftime("%B %d, %Y")

def prepare_picks(picks):
    picks_data = []
    for rec in picks:
        picks_data.append({
            "Matchup": rec['matchup'].replace(" vs ", "\nvs\n"),
            "Recommended Winner Pick": rec['winner_pick'],
        })
    df = pd.DataFrame(picks_data)
    df.index = range(1, len(df) + 1)
    return df

if "picks_fetched" not in st.session_state:
    st.session_state.picks_fetched = False

if not st.session_state.picks_fetched:
    st.caption("Click below to fetch today's picks and see the recommendations.")
    if st.button("🎯 Click to Fetch Today's Picks"):
        with st.spinner("Fetching and generating picks..."):
            today_str, today_pretty = get_date_strings()
            games = get_games_by_date(today_str)
            odds = get_mlb_odds()
            picks = generate_recommendations(games, odds)

            with open("picks_today.json", "w") as f:
                json.dump(picks, f, indent=2)

            st.session_state.picks = picks
            st.session_state.picks_fetched = True

if st.session_state.get("picks_fetched", False):
    today_str, today_pretty = get_date_strings()
    st.subheader(f"📅 Today's Picks ({today_pretty})")
    df_today = prepare_picks(st.session_state.picks)
    if not df_today.empty:
        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No picks available.")
