from datetime import datetime
from mlb_stats import get_games_by_date
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n📅 Fetching MLB games for {today_str}...\n")

    try:
        games = get_games_by_date(today_str)
        odds = get_mlb_odds()
        picks = generate_recommendations(games, odds)

        print("🎯 MLB Picks for Today:\n")
        for rec in picks: 
            print(f"✅ Pick: {rec['winner_pick']}")
            print("-" * 40)

    except Exception as e:
        print(f"❌ Error fetching picks: {e}")

if __name__ == "__main__":
    main()
