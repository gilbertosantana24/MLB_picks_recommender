from consensus_scraper import get_public_betting_consensus

MAX_SCORE = 85

def classify_confidence(score):
    if score >= 70:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

def generate_recommendations(games, odds_data):
    recommendations = []
    consensus_data = get_public_betting_consensus()

    for game in games:
        home = game["home_team"]
        away = game["away_team"]
        matchup = f"{away} (away) vs {home} (home)"
        odds = odds_data.get(f"{away} vs {home}", {})
        score = 0
        reasons = []

        moneyline = odds.get("moneyline", {})
        total_line = odds.get("total")

        try:
            if game["home_pitcher"]["era"] and game["away_pitcher"]["era"]:
                if float(game["home_pitcher"]["era"]) < float(game["away_pitcher"]["era"]):
                    score += 10
                    reasons.append("Better home pitcher ERA")
                else:
                    score += 5
                    reasons.append("Better away pitcher ERA")
        except: pass

        try:
            if game["home_pitcher"]["whip"] and game["away_pitcher"]["whip"]:
                if float(game["home_pitcher"]["whip"]) < float(game["away_pitcher"]["whip"]):
                    score += 10
                    reasons.append("Better home pitcher WHIP")
                else:
                    score += 5
                    reasons.append("Better away pitcher WHIP")
        except: pass

        try:
            if game["home_pitcher"].get("k9") and game["away_pitcher"].get("k9"):
                if float(game["home_pitcher"]["k9"]) > float(game["away_pitcher"]["k9"]):
                    score += 5
                    reasons.append("Higher strikeouts/9 (home pitcher)")
                else:
                    score += 3
                    reasons.append("Higher strikeouts/9 (away pitcher)")
        except: pass

        try:
            if game["home_pitcher"].get("bb9") and game["away_pitcher"].get("bb9"):
                if float(game["home_pitcher"]["bb9"]) < float(game["away_pitcher"]["bb9"]):
                    score += 5
                    reasons.append("Lower walks/9 (home pitcher)")
                else:
                    score += 3
                    reasons.append("Lower walks/9 (away pitcher)")
        except: pass

        try:
            hw = game["home_stats"].get("win_pct")
            aw = game["away_stats"].get("win_pct")
            if hw and aw:
                if float(hw) > float(aw):
                    score += 8
                    reasons.append("Better win % (home)")
                else:
                    score += 4
                    reasons.append("Better win % (away)")
        except: pass

        try:
            ho = game["home_stats"].get("ops")
            ao = game["away_stats"].get("ops")
            if ho and ao:
                if float(ho) > float(ao):
                    score += 5
                    reasons.append("Better team OPS (home)")
                else:
                    score += 3
                    reasons.append("Better team OPS (away)")
        except: pass

        h_odds = moneyline.get(home)
        a_odds = moneyline.get(away)
        if isinstance(h_odds, (int, float)) and h_odds < 0:
            score += 10
            reasons.append("Home is moneyline favorite")
        elif isinstance(a_odds, (int, float)) and a_odds < 0:
            score += 5
            reasons.append("Away is moneyline favorite")

        # Add public consensus logic
        consensus = consensus_data.get(f"{away} vs {home}")
        if consensus:
            bets = consensus["bets"]
            money = consensus["money"]
            if money > bets and money >= 60:
                score += 5
                reasons.append("Sharp money backing this side")
            elif bets >= 70 and money <= 50:
                score -= 3
                reasons.append("Public heavily on this side")

        winner_pick = home if score >= 40 else away
        winner_confidence = classify_confidence(score)
        winner_confidence_percentage = round((score * 100) / MAX_SCORE)

        ou_pick = None
        if total_line is not None:
            if game.get("home_score") and game.get("away_score"):
                total_runs = game["home_score"] + game["away_score"]
                ou_pick = "Over" if total_runs > total_line else "Under"
            else:
                ou_pick = "Over" if score < 35 else "Under"

        recommendations.append({
            "matchup": matchup,
            "winner_pick": winner_pick,
            "winner_confidence": winner_confidence,
            "winner_confidence_percentage": winner_confidence_percentage,
            "over_under_pick": ou_pick,
            "total_line": total_line,
            "reasons": reasons
        })

    recommendations.sort(key=lambda x: x["winner_confidence_percentage"], reverse=True)
    return recommendations
