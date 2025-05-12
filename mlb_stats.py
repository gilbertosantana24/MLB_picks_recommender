import requests


def extract_pitcher_stats(pitcher_id):
    try:
        url = f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}/stats?stats=season&group=pitching&season=2024"
        res = requests.get(url)
        stats = res.json().get("stats", [])[0].get("splits", [])
        if not stats:
            return {"era": None, "whip": None, "k9": None, "bb9": None}

        stat = stats[0].get("stat", {})
        return {
            "era": float(stat.get("era", 0)),
            "whip": float(stat.get("whip", 0)),
            "k9": float(stat.get("strikeoutsPer9Inn", 0)),
            "bb9": float(stat.get("baseOnBallsPer9Inn", 0))
        }
    except:
        return {"era": None, "whip": None, "k9": None, "bb9": None}


def get_team_ops(team_id):
    try:
        url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/stats?stats=season&group=hitting"
        res = requests.get(url)
        splits = res.json().get("stats", [])[0].get("splits", [])
        stat = splits[0].get("stat", {}) if splits else {}
        ops = float(stat.get("ops")) if stat.get("ops") else None
        return ops
    except:
        return None


def get_team_win_pct(team_id):
    try:
        url = f"https://statsapi.mlb.com/api/v1/standings?season=2024&leagueId=103,104"
        res = requests.get(url)
        for record in res.json().get("records", []):
            for team in record.get("teamRecords", []):
                if team.get("team", {}).get("id") == team_id:
                    return float(team.get("winningPercentage", 0))
        return None
    except:
        return None


def extract_team_stats(team_id):
    return {
        "ops": get_team_ops(team_id),
        "win_pct": get_team_win_pct(team_id)
    }


def get_run_diff_last_10(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/stats?stats=lastTen&group=team"
    res = requests.get(url)
    splits = res.json().get("stats", [])[0].get("splits", [])
    if not splits:
        return 0
    runs_scored = splits[0]["stat"].get("runs", 0)
    runs_allowed = splits[0]["stat"].get("runsAllowed", 0)
    return runs_scored - runs_allowed


def get_games_by_date(date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}&hydrate=probablePitcher,team,venue"
    res = requests.get(url)
    data = res.json()
    games = []

    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            home_team = game["teams"]["home"]["team"]
            away_team = game["teams"]["away"]["team"]

            home_team_id = home_team["id"]
            away_team_id = away_team["id"]

            home_pitcher = game["teams"]["home"].get("probablePitcher")
            away_pitcher = game["teams"]["away"].get("probablePitcher")

            home_pitcher_stats = extract_pitcher_stats(home_pitcher["id"]) if home_pitcher else {"era": None, "whip": None, "k9": None, "bb9": None}
            away_pitcher_stats = extract_pitcher_stats(away_pitcher["id"]) if away_pitcher else {"era": None, "whip": None, "k9": None, "bb9": None}

            home_stats = extract_team_stats(home_team_id)
            away_stats = extract_team_stats(away_team_id)

            games.append({
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "home_team_id": home_team_id,
                "away_team_id": away_team_id,
                "home_pitcher": home_pitcher_stats,
                "away_pitcher": away_pitcher_stats,
                "home_stats": home_stats,
                "away_stats": away_stats,
                "gameDate": game.get("gameDate"),
                "venue": game.get("venue", {}).get("name")
            })

    return games
