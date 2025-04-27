from mlb_stats import get_today_games
from odd_api import get_mlb_odds
from recommend_pick import generate_recommendations

print("Fetching today's games...")
games = get_today_games()
print(f"Games found: {len(games)}")

print("Fetching current odds...")
odds = get_mlb_odds()

print("Generating recommendations...\n")
recs = generate_recommendations(games, odds)

for rec in recs:
    print(f"🧢 {rec['matchup']}")
    print(f"✅ Recommended Pick: {rec['pick']}")
    print(f"📊 {rec['confidence_percentage']}% confidence")
    print(f"🔰 Confidence Level: {rec['confidence']}")
    print(f"🧠 Reasons: {', '.join(rec['reasons'])}")
    print("-" * 50)
