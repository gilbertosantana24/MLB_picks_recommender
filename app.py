import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

st.set_page_config(page_title="MLB Picks Recommender", page_icon="⚾", layout="wide")


st.title("⚾ MLB Picks Recommender ⚾")
st.caption("Intelligent MLB picks based on real pitcher stats, team performance, and betting odds.")
st.markdown("---")

def get_date_string(days_to_add=0):
    """Devuelve la fecha en formato string para hoy o mañana."""
    target_date = datetime.now(pytz.timezone('America/Los_Angeles')) + timedelta(days=days_to_add)
    return target_date.strftime("%Y-%m-%d"), target_date.strftime("%B %d, %Y")

def prepare_picks(games, picks):
    """Prepara la tabla de picks ordenada por hora de inicio."""
    picks_data = []
    for rec, game in zip(picks, games):
        if rec['confidence_percentage'] >= 55:
            confidence_label = f"{rec['confidence_percentage']}% (High)"
        elif rec['confidence_percentage'] >= 30:
            confidence_label = f"{rec['confidence_percentage']}% (Medium)"
        else:
            confidence_label = f"{rec['confidence_percentage']}% (Low)"

        matchup = rec['matchup']

        picks_data.append({
            "Matchup": matchup,
            "Recommended Pick": rec['pick'],
            "Confidence %": confidence_label,
            "Reasons": ", ".join(rec['reasons']),
            "Start Time": game.get("gameDate")  
        })

    df = pd.DataFrame(picks_data)

    df["Start Time"] = pd.to_datetime(df["Start Time"], errors='coerce')

    df = df.sort_values(by="Start Time")

    df = df.drop(columns=["Start Time"])

    df.index = range(1, len(df) + 1)

    return df

if st.button("-->Fetch Picks<--"):
    with st.spinner('Fetching games and generating picks...'):
        today_str, today_pretty = get_date_string(0)
        tomorrow_str, tomorrow_pretty = get_date_string(1)

        games_today = get_games_by_date(today_str)
        games_tomorrow = get_games_by_date(tomorrow_str)

        odds_today = get_mlb_odds()
        odds_tomorrow = get_mlb_odds()

        picks_today = generate_recommendations(games_today, odds_today)
        picks_tomorrow = generate_recommendations(games_tomorrow, odds_tomorrow)

    st.success("✅ Picks generated!")

    # --- Today's Picks ---
    st.subheader(f"📅 Today's Games ({today_pretty})")
    df_today = prepare_picks(games_today, picks_today)
    st.dataframe(df_today, use_container_width=True)

    # --- Tomorrow's Picks ---
    st.subheader(f"📅 Tomorrow's Games ({tomorrow_pretty})")
    df_tomorrow = prepare_picks(games_tomorrow, picks_tomorrow)
    st.dataframe(df_tomorrow, use_container_width=True)

else:
    st.info("Press the button above to fetch today's and tomorrow's picks.")
