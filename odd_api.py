import requests

ODDS_API_KEY = "64b69c0b37dd91cda29c6ec7095b26ee"

def get_mlb_odds():
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
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
        if not game["bookmakers"][0].get("markets"):
            continue

        home = game["home_team"]
        away = game["away_team"]
        ml = {}
        for outcome in game["bookmakers"][0]["markets"][0]["outcomes"]:
            ml[outcome["name"]] = outcome["price"]

        odds[f"{away} vs {home}"] = ml

    return odds
