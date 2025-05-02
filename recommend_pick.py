from consensus_scraper import get_public_betting_consensus
from bullpen_scraper import get_team_bullpen_era

def generate_recommendations(games, odds_data):
    recommendations = []
    bullpen_eras = get_team_bullpen_era()
    consensus_data = get_public_betting_consensus()

    for game in games:
        home = game["home_team"]
        away = game["away_team"]
        matchup = f"{away} (away) vs {home} (home)"
        odds = odds_data.get(f"{away} vs {home}", {})
        score_home = 0
        score_away = 0

        # ----------------- Pitcher ERA (recent)
        home_pitcher = game["home_pitcher"].get("recent", {})
        away_pitcher = game["away_pitcher"].get("recent", {})
        if home_pitcher.get("era") is not None and away_pitcher.get("era") is not None:
            if home_pitcher["era"] < away_pitcher["era"]:
                score_home += 10
            else:
                score_away += 10

        # ----------------- Team OPS
        home_ops = game["home_stats"].get("ops")
        away_ops = game["away_stats"].get("ops")
        if home_ops and away_ops:
            if float(home_ops) > float(away_ops):
                score_home += 6
            else:
                score_away += 6

        # ----------------- Bullpen ERA
        home_bp = bullpen_eras.get(home)
        away_bp = bullpen_eras.get(away)
        if home_bp and away_bp:
            if home_bp < away_bp:
                score_home += 4
            else:
                score_away += 4

        # ----------------- Win % (proxy for last 10 games performance)
        home_win_pct = game["home_stats"].get("win_pct")
        away_win_pct = game["away_stats"].get("win_pct")
        if home_win_pct and away_win_pct:
            if float(home_win_pct) > float(away_win_pct):
                score_home += 6
            else:
                score_away += 6

        # ----------------- Betting Consensus
        consensus = consensus_data.get(f"{away} vs {home}")
        if consensus:
            bets = consensus.get("bets")
            money = consensus.get("money")
            if money > bets and money >= 60:
                score_away += 3  # Sharp money
            elif bets >= 70 and money <= 50:
                score_home += 2  # Fade public

        # ----------------- Moneyline Odds (tie breaker)
        moneyline = odds.get("moneyline", {})
        h_odds = moneyline.get(home)
        a_odds = moneyline.get(away)
        if isinstance(h_odds, (int, float)) and h_odds < 0:
            score_home += 2
        elif isinstance(a_odds, (int, float)) and a_odds < 0:
            score_away += 2

        # ----------------- Final Decision
        winner_pick = home if score_home >= score_away else away

        recommendations.append({
            "matchup": matchup,
            "winner_pick": winner_pick
        })

    return recommendations
