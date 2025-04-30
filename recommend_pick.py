from consensus_scraper import get_public_betting_consensus
from bullpen_scraper import get_team_bullpen_era
from batting_scraper import get_team_k_bb_rates

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
    bullpen_eras = get_team_bullpen_era()
    team_kbb = get_team_k_bb_rates()

    for game in games:
        home = game["home_team"]
        away = game["away_team"]
        matchup = f"{away} (away) vs {home} (home)"
        odds = odds_data.get(f"{away} vs {home}", {})
        score = 0
        reasons = []

        moneyline = odds.get("moneyline", {})

        home_pitcher = game["home_pitcher"]
        away_pitcher = game["away_pitcher"]

        home_recent = home_pitcher.get("recent")
        away_recent = away_pitcher.get("recent")

        def compare_stat(stat, better_low=True):
            h_val = home_recent.get(stat) if home_recent else None
            a_val = away_recent.get(stat) if away_recent else None
            if h_val is not None and a_val is not None:
                if (h_val < a_val and better_low) or (h_val > a_val and not better_low):
                    return "home"
                else:
                    return "away"
            return None

        try:
            if compare_stat("era", better_low=True) == "home":
                score += 10
                reasons.append("Better home pitcher ERA (recent)")
            elif compare_stat("era", better_low=True) == "away":
                score += 5
                reasons.append("Better away pitcher ERA (recent)")
        except: pass

        try:
            if compare_stat("whip", better_low=True) == "home":
                score += 10
                reasons.append("Better home pitcher WHIP (recent)")
            elif compare_stat("whip", better_low=True) == "away":
                score += 5
                reasons.append("Better away pitcher WHIP (recent)")
        except: pass

        try:
            if compare_stat("k9", better_low=False) == "home":
                score += 5
                reasons.append("Higher strikeouts/9 (home pitcher, recent)")
            elif compare_stat("k9", better_low=False) == "away":
                score += 3
                reasons.append("Higher strikeouts/9 (away pitcher, recent)")
        except: pass

        try:
            if compare_stat("bb9", better_low=True) == "home":
                score += 5
                reasons.append("Lower walks/9 (home pitcher, recent)")
            elif compare_stat("bb9", better_low=True) == "away":
                score += 3
                reasons.append("Lower walks/9 (away pitcher, recent)")
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

        bullpen_home = bullpen_eras.get(home)
        bullpen_away = bullpen_eras.get(away)
        if bullpen_home and bullpen_away:
            if bullpen_home < bullpen_away:
                score += 3
                reasons.append("Stronger bullpen (home)")
            else:
                score += 1
                reasons.append("Stronger bullpen (away)")

        opponent_kbb = team_kbb.get(away)
        if opponent_kbb and home_recent:
            if opponent_kbb["k_pct"] > 24 and home_recent["k9"] > 9:
                score += 3
                reasons.append("High K% opponent favors home pitcher")
            if opponent_kbb["bb_pct"] > 10 and home_recent["bb9"] > 3.5:
                score -= 2
                reasons.append("High BB% opponent vs wild home pitcher")

        winner_pick = home if score >= 40 else away
        winner_confidence = classify_confidence(score)
        winner_confidence_percentage = round((score * 100) / MAX_SCORE)

        recommendations.append({
            "matchup": matchup,
            "winner_pick": winner_pick,
            "winner_confidence": winner_confidence,
            "winner_confidence_percentage": winner_confidence_percentage,
            "reasons": reasons
        })

    recommendations.sort(key=lambda x: x["winner_confidence_percentage"], reverse=True)
    return recommendations
