from datetime import datetime
import json
from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetching MLB games for {today_str}...")

    games = get_games_by_date(today_str)
    odds = get_mlb_odds()
    recs = generate_recommendations(games, odds)

    with open("games_today.json", "w") as f:
        json.dump(games, f)

    with open("picks_today.json", "w") as f:
        json.dump(recs, f)

    print(f"Picks saved for {today_str}")

if __name__ == "__main__":
    main()
