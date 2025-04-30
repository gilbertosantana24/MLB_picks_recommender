import requests

ODDS_API_KEY = "64b69c0b37dd91cda29c6ec7095b26ee"

def get_mlb_odds():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,totals",
        "oddsFormat": "american"
    }
    res = requests.get(url, params=params)

    try:
        data = res.json()
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}

    if not isinstance(data, list):
        print(f"Expected a list but got: {type(data)}")
        print(data)
        return {}

    odds = {}
    for game in data:
        if not game.get("bookmakers"):
            continue

        home = game["home_team"]
        away = game["away_team"]
        matchup = f"{away} vs {home}"
        market_data = {
            "moneyline": {},
            "total": None
        }

        for market in game["bookmakers"][0].get("markets", []):
            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    market_data["moneyline"][outcome["name"]] = outcome["price"]
            if market["key"] == "totals":
                market_data["total"] = market["outcomes"][0]["point"]

        odds[matchup] = market_data

    return odds
