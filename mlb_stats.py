import requests

def get_games_by_date(date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}&hydrate=probablePitcher(stats(type=season,group=pitching)),team(stats,type=season)"
    res = requests.get(url)
    data = res.json()

    games = []

    for date_info in data.get("dates", []):
        for game in date_info.get("games", []):
            home = game["teams"]["home"]
            away = game["teams"]["away"]
            home_pitcher = home.get("probablePitcher", {})
            away_pitcher = away.get("probablePitcher", {})

            home_pitcher_stats = extract_pitcher_stats(home_pitcher)
            away_pitcher_stats = extract_pitcher_stats(away_pitcher)

            home_team_stats = extract_team_stats(home)
            away_team_stats = extract_team_stats(away)

            games.append({
                "home_team": home["team"]["name"],
                "away_team": away["team"]["name"],
                "home_pitcher": home_pitcher_stats,
                "away_pitcher": away_pitcher_stats,
                "home_stats": home_team_stats,
                "away_stats": away_team_stats,
                "gameDate": game.get("gameDate")
            })

    return games

def extract_pitcher_stats(pitcher):
    stats = pitcher.get("stats", [])
    if not stats:
        return {"era": None, "whip": None, "k9": None, "bb9": None}

    pitching_stats = stats[0].get("splits", [{}])[0].get("stat", {})
    return {
        "era": pitching_stats.get("era"),
        "whip": pitching_stats.get("whip"),
        "k9": pitching_stats.get("strikeoutsPer9Inn"),
        "bb9": pitching_stats.get("baseOnBallsPer9Inn")
    }

def extract_team_stats(team):
    stats = team.get("teamStats", [])
    if not stats:
        return {"win_pct": None, "ops": None}

    stat_data = stats[0].get("splits", [{}])[0].get("stat", {})
    return {
        "win_pct": stat_data.get("winPercentage"),
        "ops": stat_data.get("ops")
    }
