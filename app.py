import streamlit as st
from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations
from datetime import datetime

st.set_page_config(page_title="MLB Daily Picks", layout="wide")

st.title("⚾️ MLB Picks of the Day")

if st.button("Fetch Recommendations"):
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        games = get_games_by_date(today)
        odds_data = get_mlb_odds()
        picks = generate_recommendations(games, odds_data)

        if picks:
            st.success("Picks loaded successfully!")
            st.json(picks)
        else:
            st.warning("No picks available.")
    except Exception as e:
        st.error(f"Error fetching picks: {e}")
