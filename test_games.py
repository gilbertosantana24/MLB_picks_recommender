import json
from mlb_stats import get_games_by_date

games = get_games_by_date("2025-05-12")
print(json.dumps(games, indent=2))
