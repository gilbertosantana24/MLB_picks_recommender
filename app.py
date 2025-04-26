# app.py
import streamlit as st
import pandas as pd
from mlb_stats import get_today_games
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations
from datetime import datetime
import pytz

# --- CONFIG ---
st.set_page_config(page_title="MLB Picks Recommender", page_icon="⚾", layout="wide")

# --- HEADER ---
st.title("⚾ MLB Picks Recommender")
st.caption("Intelligent MLB picks based on real pitcher stats, team performance, and betting odds.")

st.markdown("---")

# --- Helper: Convert UTC to PST time ---
def convert_utc_to_pst(utc_datetime_str):
    utc_time = datetime.strptime(utc_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    pst_timezone = pytz.timezone('America/Los_Angeles')
    pst_time = utc_time.astimezone(pst_timezone)
    return pst_time.strftime("%I:%M %p")  # e.g., "04:10 PM"

# --- FETCH BUTTON ---
if st.button("🚀 Fetch Today's Picks"):
    with st.spinner('Fetching games and calculating picks...'):
        games = get_today_games()
        odds = get_mlb_odds()
        picks = generate_recommendations(games, odds)

    st.success(f"✅ {len(picks)} picks found!")

    # --- Prepare Picks Data ---
    picks_data = []
    for rec, game in zip(picks, games):
        # --- Get start time in PST ---
        game_time_utc = game.get("gameDate")
        if game_time_utc:
            game_time_pst = convert_utc_to_pst(game_time_utc)
        else:
            game_time_pst = "N/A"

        # --- Determine High/Medium/Low Confidence ---
        if rec['confidence_percentage'] >= 55:
            confidence_label = f"{rec['confidence_percentage']}% (High)"
        elif rec['confidence_percentage'] >= 30:
            confidence_label = f"{rec['confidence_percentage']}% (Medium)"
        else:
            confidence_label = f"{rec['confidence_percentage']}% (Low)"

        # --- Create Matchup with Time
        matchup_with_time = f"{rec['matchup']} - {game_time_pst} PST"

        picks_data.append({
            "Matchup": matchup_with_time,
            "Recommended Pick": rec['pick'],
            "Confidence %": confidence_label,
            "Reasons": ", ".join(rec['reasons']),
        })

    df = pd.DataFrame(picks_data)

    # --- Reset index starting at 1 ---
    df.index = df.index + 1

    # --- Picks Table Title ---
    st.subheader("📊 Picks Table (Games & Start Time in PST)")

    # --- Show Table ---
    st.dataframe(df, use_container_width=True)

else:
    st.info("Press the button above to fetch today's recommended picks.")
