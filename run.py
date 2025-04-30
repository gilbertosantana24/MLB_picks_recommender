from datetime import datetime

from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations


def main():
    # Determine today's date
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetching today's games for {today_str}...")
    games = get_games_by_date(today_str)
    print(f"Games found: {len(games)}")

    # Fetch odds
    print("Fetching current odds...")
    odds = get_mlb_odds()

    # Generate and display recommendations
    print("Generating recommendations...\n")
    recs = generate_recommendations(games, odds)

    for rec in recs:
        print(f"🧢 {rec['matchup']}")
        print(f"✅ Recommended Pick: {rec['pick']}")
        print(f"📊 {rec['confidence_percentage']}% confidence")
        print(f"🔰 Confidence Level: {rec['confidence']}")
        print(f"🧠 Reasons: {', '.join(rec['reasons'])}")
        print("-" * 50)


if __name__ == '__main__':
    main()