import requests

def get_pitcher_stats(pitcher_id):
    url = f"https://statsapi.mlb.com/api/v1/people/{pitcher_id}?hydrate=stats(type=season)"
    res = requests.get(url).json()
    stats = res["people"][0].get("stats", [])
    if stats:
        era = stats[0]["splits"][0]["stat"].get("era")
        whip = stats[0]["splits"][0]["stat"].get("whip")
        return {"era": float(era) if era else None, "whip": float(whip) if whip else None}
    else:
        return {"era": None, "whip": None}

def get_team_stats(team_id):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/stats?stats=season&group=hitting"
    res = requests.get(url).json()
    stats = res.get("stats", [])
    if stats:
        hitting_stats = stats[0]["splits"][0]["stat"]
        ops = hitting_stats.get("ops")
        win_pct = hitting_stats.get("winPercentage")
        return {
            "ops": float(ops) if ops else None,
            "win_pct": float(win_pct) if win_pct else None,
        }
    else:
        return {"ops": None, "win_pct": None}

def get_final_score(game_id):
    """Consulta el boxscore del juego para obtener el score FINAL real."""
    url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
    res = requests.get(url).json()

    game_status = res.get("teams", {})
    if "home" in game_status and "away" in game_status:
        home_score = res["teams"]["home"].get("runs")
        away_score = res["teams"]["away"].get("runs")
        return home_score, away_score
    return None, None

def get_games_by_date(date_str):
    """Obtiene juegos MLB de una fecha (YYYY-MM-DD)."""
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
    response = requests.get(url)
    data = response.json()

    games = []
    for game in data.get("dates", [])[0].get("games", []):
        home_team_info = game["teams"]["home"]["team"]
        away_team_info = game["teams"]["away"]["team"]

        home_pitcher_info = game["teams"]["home"].get("probablePitcher")
        away_pitcher_info = game["teams"]["away"].get("probablePitcher")

        home_pitcher_stats = get_pitcher_stats(home_pitcher_info["id"]) if home_pitcher_info else {"era": None, "whip": None}
        away_pitcher_stats = get_pitcher_stats(away_pitcher_info["id"]) if away_pitcher_info else {"era": None, "whip": None}

        home_team_stats = get_team_stats(home_team_info["id"])
        away_team_stats = get_team_stats(away_team_info["id"])

        game_pk = game.get("gamePk")
        home_score, away_score = None, None
        status = game.get("status", {}).get("detailedState", "TBD")

        if status == "Final" and game_pk:
            home_score, away_score = get_final_score(game_pk)

        games.append({
            "home_team": home_team_info["name"],
            "away_team": away_team_info["name"],
            "home_pitcher": home_pitcher_stats,
            "away_pitcher": away_pitcher_stats,
            "home_stats": home_team_stats,
            "away_stats": away_team_stats,
            "home_score": home_score,
            "away_score": away_score,
            "gameDate": game.get("gameDate"),
            "status": status
        })

    return games
