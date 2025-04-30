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

def get_recent_pitcher_stats(pitcher_id, num_games=3):
    url = f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}/stats?stats=gameLog&group=pitching&season=2024"
    res = requests.get(url)
    logs = res.json().get("stats", [])[0].get("splits", [])

    recent_logs = logs[:num_games]
    if not recent_logs:
        return None

    innings = 0
    earned_runs = 0
    walks = 0
    strikeouts = 0
    hits = 0

    for game in recent_logs:
        stat = game["stat"]
        innings += float(stat.get("inningsPitched", 0))
        earned_runs += stat.get("earnedRuns", 0)
        walks += stat.get("baseOnBalls", 0)
        strikeouts += stat.get("strikeOuts", 0)
        hits += stat.get("hits", 0)

    era = (earned_runs * 9 / innings) if innings else None
    whip = ((walks + hits) / innings) if innings else None
    k9 = (strikeouts * 9 / innings) if innings else None
    bb9 = (walks * 9 / innings) if innings else None

    return {"era": era, "whip": whip, "k9": k9, "bb9": bb9}

def extract_pitcher_stats(pitcher):
    stats = pitcher.get("stats", [])
    if not stats:
        return {"era": None, "whip": None, "k9": None, "bb9": None}

    pitching_stats = stats[0].get("splits", [{}])[0].get("stat", {})
    return {
        "era": pitching_stats.get("era"),
        "whip": pitching_stats.get("whip"),
        "k9": pitching_stats.get("strikeoutsPer9Inn"),
        "bb9": pitching_stats.get("baseOnBallsPer9Inn"),
        "recent": get_recent_pitcher_stats(pitcher.get("id"))
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
