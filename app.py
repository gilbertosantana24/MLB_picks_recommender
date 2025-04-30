import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

st.set_page_config(page_title="Slider picks", page_icon="⚾", layout="wide")

st.title("⚾ MLB Picks Recommender ⚾")
st.caption("MLB picks based on pitcher stats, team performance, and betting odds.")
st.markdown("---")

def get_date_string(days_to_add=0):
    target_date = datetime.now(pytz.timezone('America/Los_Angeles')) + timedelta(days=days_to_add)
    return target_date.strftime("%Y-%m-%d"), target_date.strftime("%B %d, %Y")

def prepare_picks(games, picks):
    picks_data = []
    for rec, game in zip(picks, games):
        picks_data.append({
            "Matchup": rec['matchup'].replace(" vs ", "\nvs\n"),
            "Recommended Winner Pick": rec['winner_pick'],
            #"Over/Under Pick": f"{rec['over_under_pick']} {rec['total_line']}" if rec['over_under_pick'] else "N/A"
        })

    df = pd.DataFrame(picks_data)
    df.index = range(1, len(df) + 1)
    return df

if "picks_fetched" not in st.session_state:
    st.session_state.picks_fetched = False

if st.button("→ Click here to get picks") or st.session_state.picks_fetched:
    if not st.session_state.picks_fetched:
        with st.spinner('Fetching games and generating picks...'):
            today_str, today_pretty = get_date_string(0)
            tomorrow_str, tomorrow_pretty = get_date_string(1)

            st.session_state.today_str = today_str
            st.session_state.tomorrow_str = tomorrow_str
            st.session_state.today_pretty = today_pretty
            st.session_state.tomorrow_pretty = tomorrow_pretty

            st.session_state.games_today = get_games_by_date(today_str)
            st.session_state.games_tomorrow = get_games_by_date(tomorrow_str)

            st.session_state.odds_today = get_mlb_odds()
            st.session_state.odds_tomorrow = get_mlb_odds()

            st.session_state.picks_today = generate_recommendations(st.session_state.games_today, st.session_state.odds_today)
            st.session_state.picks_tomorrow = generate_recommendations(st.session_state.games_tomorrow, st.session_state.odds_tomorrow)

            st.session_state.picks_fetched = True

    st.success("✅ Picks generated!")

    st.subheader(f"📅 Today's Games ({st.session_state.today_pretty})")
    df_today = prepare_picks(st.session_state.games_today, st.session_state.picks_today)

    if not df_today.empty:
        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No picks available for today's games.")

    st.subheader(f"📅 Tomorrow's Games ({st.session_state.tomorrow_pretty})")
    df_tomorrow = prepare_picks(st.session_state.games_tomorrow, st.session_state.picks_tomorrow)

    if not df_tomorrow.empty:
        st.dataframe(df_tomorrow, use_container_width=True)
    else:
        st.info("No picks available for tomorrow's games.")

else:
    st.info("Press the button above to fetch today's and tomorrow's picks.")
