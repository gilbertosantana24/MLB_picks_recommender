import json
import os
from datetime import datetime
from mlb_stats import get_games_by_date

def fetch_final_results():
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        with open("picks_today.json", "r") as f:
            picks = json.load(f)
    except FileNotFoundError:
        print("❌ picks_today.json not found.")
        return

    games = get_games_by_date(today_str)
    results = []

    for rec in picks:
        matchup = rec["matchup"]
        picked = rec["winner_pick"]

        # Match the game to get final score
        game = next((g for g in games if f"{g['away_team']} (away) vs {g['home_team']} (home)" == matchup), None)
        if not game or "score" not in game:
            actual = None
        else:
            score = game["score"]
            h_score = score.get("home", 0)
            a_score = score.get("away", 0)
            actual = game["home_team"] if h_score > a_score else game["away_team"]

        results.append({
            "matchup": matchup,
            "picked": picked,
            "actual": actual
        })

    # Save results with timestamp
    month_day = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("results", exist_ok=True)
    with open(f"results/{month_day}.json", "w") as f:
        json.dump({"date": today_str, "results": results}, f, indent=2)

    print(f"✅ Saved results for {today_str}")

if __name__ == "__main__":
    fetch_final_results()
