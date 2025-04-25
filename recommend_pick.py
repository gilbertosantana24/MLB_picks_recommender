# recommender.py

MAX_SCORE = 70  # Max possible score to normalize percentage

def classify_confidence(score):
    if score >= 55:
        return "🔥 High Confidence"
    elif score >= 30:
        return "👍 Medium Confidence"
    else:
        return "🤔 Low Confidence"

def generate_recommendations(games, odds_data):
    recommendations = []

    for game in games:
        home = game["home_team"]
        away = game["away_team"]
        matchup = f"{away} (away) vs {home} (home)"
        odds = odds_data.get(f"{away} vs {home}", {})
        score = 0
        reasons = []

        try:
            if float(game["home_pitcher"]["era"]) < float(game["away_pitcher"]["era"]):
                score += 20
                reasons.append("Better home pitcher ERA")
            else:
                score += 10
                reasons.append("Better away pitcher ERA")
        except:
            reasons.append("ERA data not available")

        try:
            if float(game["home_pitcher"]["whip"]) < float(game["away_pitcher"]["whip"]):
                score += 15
                reasons.append("Better home pitcher WHIP")
            else:
                score += 5
                reasons.append("Better away pitcher WHIP")
        except:
            reasons.append("WHIP data not available")

        try:
            home_record = game["home_stats"]["lastTenRecord"]
            away_record = game["away_stats"]["lastTenRecord"]
            if float(game["home_stats"]["lastTenWinPct"]) > float(game["away_stats"]["lastTenWinPct"]):
                score += 10
                reasons.append(f"Better last 10 games record (home) [{home_record}]")
            else:
                reasons.append(f"Better last 10 games record (away) [{away_record}]")
        except:
            reasons.append("Last 10 games record not available")

        try:
            if float(game["home_stats"]["ops"]) > float(game["away_stats"]["ops"]):
                score += 5
                reasons.append("Better OPS (home)")
            else:
                reasons.append("Better OPS (away)")
        except:
            reasons.append("OPS data not available")

        h_odds = odds.get(home)
        a_odds = odds.get(away)
        if h_odds and h_odds < 0:
            score += 10
            reasons.append("Favorite in moneyline (home)")
        elif a_odds and a_odds < 0:
            score += 5
            reasons.append("Favorite in moneyline (away)")

        pick = home if score >= 40 else away
        confidence = classify_confidence(score)
        confidence_percentage = round((score * 100) / MAX_SCORE)

        recommendations.append({
            "matchup": matchup,
            "pick": pick,
            "confidence": confidence,
            "confidence_percentage": confidence_percentage,
            "reasons": reasons
        })

    recommendations.sort(key=lambda x: x["confidence_percentage"], reverse=True)
    return recommendations
