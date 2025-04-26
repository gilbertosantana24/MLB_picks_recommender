# mlb_stats.py
import requests
from datetime import datetime

def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')

def get_pitcher_stats(pitcher_id):
    url = f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}/stats?stats=season&group=pitching"
    res = requests.get(url).json()
    try:
        stat = res["stats"][0]["splits"][0]["stat"]
        return {
            "era": stat.get("era"),
            "whip": stat.get("whip")
        }
    except:
        return {"era": None, "whip": None}

def get_last_10_record(team_id):
    """Calculate real last 10 games win percentage and format as 'wins/10'."""
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate=2024-01-01&endDate={datetime.now().strftime('%Y-%m-%d')}&gameType=R"
    res = requests.get(url).json()
    games = []
    for date in res.get("dates", []):
        for game in date.get("games", []):
            if game.get("status", {}).get("abstractGameState") == "Final":
                home_team = game["teams"]["home"]["team"]["id"]
                away_team = game["teams"]["away"]["team"]["id"]
                home_score = game["teams"]["home"].get("score")
                away_score = game["teams"]["away"].get("score")
                if home_score is not None and away_score is not None:
                    games.append({
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_score": home_score,
                        "away_score": away_score,
                    })
    last_10_games = games[-10:]
    wins = 0
    for g in last_10_games:
        if team_id == g["home_team"] and g["home_score"] > g["away_score"]:
            wins += 1
        elif team_id == g["away_team"] and g["away_score"] > g["home_score"]:
            wins += 1
    total_games = len(last_10_games)
    if total_games == 0:
        return "0/0", 0.5
    else:
        return f"{wins}/{total_games}", wins / total_games

def get_team_stats(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/stats?stats=season&group=hitting"
    res = requests.get(url).json()
    team_stats = {"ops": None, "lastTenWinPct": None, "lastTenRecord": None}
    try:
        for group in res["stats"]:
            if group["group"]["displayName"] == "hitting":
                team_stats["ops"] = group["splits"][0]["stat"].get("ops")
    except:
        pass

    record_str, record_pct = get_last_10_record(team_id)
    team_stats["lastTenWinPct"] = record_pct
    team_stats["lastTenRecord"] = record_str
    return team_stats

def get_today_games():
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={get_today_date()}&hydrate=probablePitcher"
    res = requests.get(url).json()
    games = []
    for game in res.get("dates", [])[0].get("games", []):
        home_team = game["teams"]["home"]["team"]
        away_team = game["teams"]["away"]["team"]

        home_pitcher_data = game["teams"]["home"].get("probablePitcher")
        away_pitcher_data = game["teams"]["away"].get("probablePitcher")

        home_pitcher = get_pitcher_stats(home_pitcher_data["id"]) if home_pitcher_data else {"era": None, "whip": None}
        away_pitcher = get_pitcher_stats(away_pitcher_data["id"]) if away_pitcher_data else {"era": None, "whip": None}

        home_stats = get_team_stats(home_team["id"])
        away_stats = get_team_stats(away_team["id"])

        games.append({
            "home_team": home_team["name"],
            "away_team": away_team["name"],
            "home_pitcher": home_pitcher,
            "away_pitcher": away_pitcher,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "gameDate": game.get("gameDate")  # 👈 Add this!
        })
    return games

