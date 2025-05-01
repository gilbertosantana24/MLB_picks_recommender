import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
import matplotlib.pyplot as plt

from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

st.set_page_config(page_title="Slider picks", page_icon="⚾", layout="wide")
st.title("⚾ MLB Picks Recommender ⚾")
st.caption("Click below to fetch today's picks and track yesterday's results.")
st.markdown("---")

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

def get_monthly_performance():
    correct = 0
    total = 0
    month = datetime.now().strftime("%Y-%m")
    folder = "results"
    if not os.path.exists(folder):
        return 0, 0

    for file in os.listdir(folder):
        if file.endswith(".json") and file.startswith(month):
            with open(os.path.join(folder, file)) as f:
                data = json.load(f)
                for game in data["results"]:
                    if game.get("picked") and game.get("actual"):
                        total += 1
                        if game["picked"] == game["actual"]:
                            correct += 1
    return correct, total

def display_pie_chart(correct, total):
    wrong = total - correct
    labels = ["✅ Correct", "❌ Wrong"]
    sizes = [correct, wrong]
    colors = ["#4CAF50", "#F44336"]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
    ax.axis("equal")
    st.pyplot(fig)

def evaluate_yesterday_results():
    yesterday = (datetime.now(pytz.timezone('America/Los_Angeles')) - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        with open("picks_today.json", "r") as f:
            all_picks = json.load(f)
    except:
        return None, None

    games = get_games_by_date(yesterday)
    result_map = {}
    for g in games:
        if "score" in g:
            h = g["home_team"]
            a = g["away_team"]
            h_score = g["score"]["home"]
            a_score = g["score"]["away"]
            winner = h if h_score > a_score else a
            matchup = f"{a} (away) vs {h} (home)"
            result_map[matchup] = winner

    correct = 0
    total = 0
    results = []
    for rec in all_picks:
        matchup = rec["matchup"]
        picked = rec["winner_pick"]
        actual = result_map.get(matchup)
        if picked and actual:
            total += 1
            if picked == actual:
                correct += 1
        results.append({
            "matchup": matchup,
            "picked": picked,
            "actual": actual
        })

    os.makedirs("results", exist_ok=True)
    with open(f"results/{yesterday}.json", "w") as f:
        json.dump({"date": yesterday, "results": results}, f, indent=2)

    return correct, total

if "picks_fetched" not in st.session_state:
    st.session_state.picks_fetched = False

if st.button("🎯 Click to Fetch Today's Picks") or st.session_state.picks_fetched:
    with st.spinner("Fetching and generating picks..."):
        correct, total = evaluate_yesterday_results()
        if correct is not None:
            percent = round((correct / total) * 100, 1) if total else 0
            st.success(f"✅ Yesterday’s record: {correct} right / {total} total ({percent}%)")

        today_str, today_pretty = get_date_strings()
        games = get_games_by_date(today_str)
        odds = get_mlb_odds()
        picks = generate_recommendations(games, odds)

        with open("picks_today.json", "w") as f:
            json.dump(picks, f, indent=2)

        st.session_state.picks_fetched = True

    st.subheader(f"📅 Today's Picks ({today_pretty})")
    df_today = prepare_picks(picks)
    if not df_today.empty:
        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No picks available.")
else:
    today_str, today_pretty = get_date_strings()
    picks_file = "picks_today.json"
    if os.path.exists(picks_file):
        with open(picks_file, "r") as f:
            picks = json.load(f)
        st.subheader(f"📅 Today's Picks ({today_pretty})")
        df_today = prepare_picks(picks)
        if not df_today.empty:
            st.dataframe(df_today, use_container_width=True)
        else:
            st.info("No picks available.")
    else:
        st.warning("Picks not generated yet. Click the button above to fetch.")

st.markdown("---")
st.markdown("### 📊 Monthly Pick Accuracy")
correct, total = get_monthly_performance()
st.write(f"🎯 {correct} right picks / {total} total games")
if total > 0:
    display_pie_chart(correct, total)
else:
    st.info("No pick results available yet for this month.")
