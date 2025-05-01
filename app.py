import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Slider picks", page_icon="⚾", layout="wide")
st.title("⚾ MLB Picks Recommender ⚾")
st.caption("Picks generated automatically every day at 12:01 AM.")
st.markdown("---")

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

def get_date_strings():
    now = datetime.now(pytz.timezone('America/Los_Angeles'))
    return now.strftime("%Y-%m-%d"), now.strftime("%B %d, %Y")

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

# === Load today's picks ===
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
    st.warning("Picks have not been generated yet. Please run the daily fetch script.")

# === Show Monthly Accuracy ===
st.markdown("---")
st.markdown("### 📊 Monthly Pick Accuracy")
correct, total = get_monthly_performance()
st.write(f"🎯 {correct} right picks / {total} total games")
if total > 0:
    display_pie_chart(correct, total)
else:
    st.info("No pick results available yet for this month.")
