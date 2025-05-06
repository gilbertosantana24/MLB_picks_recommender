from consensus_scraper import get_public_betting_consensus
from bullpen_scraper import get_team_bullpen_era
from weather_fetcher import get_weather
import random

PARK_FACTORS = {
    "Angel Stadium": 1.02,
    "Busch Stadium": 0.95,
    "Chase Field": 1.04,
    "Citizens Bank Park": 1.06,
    "Citi Field": 0.97,
    "Comerica Park": 0.98,
    "Coors Field": 1.35,
    "Dodger Stadium": 1.00,
    "Fenway Park": 1.08,
    "Globe Life Field": 1.01,
    "Great American Ball Park": 1.12,
    "Guaranteed Rate Field": 1.04,
    "Kauffman Stadium": 0.96,
    "loanDepot park": 0.94,
    "Minute Maid Park": 1.01,
    "Nationals Park": 1.01,
    "Oakland Coliseum": 0.92,
    "Oracle Park": 0.90,
    "Petco Park": 0.85,
    "PNC Park": 0.98,
    "Progressive Field": 1.00,
    "Rogers Centre": 1.09,
    "T-Mobile Park": 0.94,
    "Target Field": 0.99,
    "Tropicana Field": 0.93,
    "Truist Park": 1.05,
    "Wrigley Field": 1.07,
    "Yankee Stadium": 1.12,
    "American Family Field": 1.03,
    "Oriole Park at Camden Yards": 1.00
}

BALLPARK_CITIES = {
    "Angel Stadium": "Anaheim",
    "Busch Stadium": "St. Louis",
    "Chase Field": "Phoenix",
    "Citizens Bank Park": "Philadelphia",
    "Citi Field": "New York",
    "Comerica Park": "Detroit",
    "Coors Field": "Denver",
    "Dodger Stadium": "Los Angeles",
    "Fenway Park": "Boston",
    "Globe Life Field": "Arlington",
    "Great American Ball Park": "Cincinnati",
    "Guaranteed Rate Field": "Chicago",
    "Kauffman Stadium": "Kansas City",
    "loanDepot park": "Miami",
    "Minute Maid Park": "Houston",
    "Nationals Park": "Washington",
    "Oakland Coliseum": "Oakland",
    "Oracle Park": "San Francisco",
    "Petco Park": "San Diego",
    "PNC Park": "Pittsburgh",
    "Progressive Field": "Cleveland",
    "Rogers Centre": "Toronto",
    "T-Mobile Park": "Seattle",
    "Target Field": "Minneapolis",
    "Tropicana Field": "St. Petersburg",
    "Truist Park": "Atlanta",
    "Wrigley Field": "Chicago",
    "Yankee Stadium": "New York",
    "American Family Field": "Milwaukee",
    "Oriole Park at Camden Yards": "Baltimore"
}

def generate_recommendations(games, odds_data):
    recommendations = []
    bullpen_eras = get_team_bullpen_era()
    consensus_data = get_public_betting_consensus()

    for game in games:
        home = game["home_team"]
        away = game["away_team"]
        venue = game.get("venue")
        matchup = f"{away} (away) vs {home} (home)"
        odds = odds_data.get(f"{away} vs {home}", {})
        score_home = 0
        score_away = 0

        # Pitcher Stats
        home_pitcher = game["home_pitcher"].get("recent", {})
        away_pitcher = game["away_pitcher"].get("recent", {})
        for metric in ["era", "whip", "k9", "bb9"]:
            if home_pitcher.get(metric) is not None and away_pitcher.get(metric) is not None:
                if home_pitcher[metric] < away_pitcher[metric]:
                    score_home += 1
                else:
                    score_away += 1

        # Team OPS
        home_ops = game["home_stats"].get("ops")
        away_ops = game["away_stats"].get("ops")
        if home_ops and away_ops:
            if float(home_ops) > float(away_ops):
                score_home += 2
            else:
                score_away += 2

        # Bullpen ERA
        home_bp = bullpen_eras.get(home)
        away_bp = bullpen_eras.get(away)
        if home_bp and away_bp:
            if home_bp < away_bp:
                score_home += 1
            else:
                score_away += 1

        # Team Win %
        home_win_pct = game["home_stats"].get("win_pct")
        away_win_pct = game["away_stats"].get("win_pct")
        if home_win_pct and away_win_pct:
            if float(home_win_pct) > float(away_win_pct):
                score_home += 2
            else:
                score_away += 2

        # Park Factor
        park_factor = PARK_FACTORS.get(venue, 1.00)
        if park_factor > 1.1:
            if home_ops and away_ops:
                if float(home_ops) > float(away_ops):
                    score_home += 0.5
                else:
                    score_away += 0.5
        elif park_factor < 0.9:
            if home_pitcher.get("era") and away_pitcher.get("era"):
                if home_pitcher["era"] < away_pitcher["era"]:
                    score_home += 0.5
                else:
                    score_away += 0.5

        # Weather Effects
        weather = get_weather(BALLPARK_CITIES.get(venue, ""))
        if weather.get("wind_mph", 0) > 15:
            score_home += 0.5
        elif weather.get("temp", 0) > 85:
            if home_ops and away_ops:
                if float(home_ops) > float(away_ops):
                    score_home += 0.5
                else:
                    score_away += 0.5

        # Betting Consensus
        consensus = consensus_data.get(f"{away} vs {home}")
        if consensus:
            bets = consensus.get("bets")
            money = consensus.get("money")
            if money > bets and money >= 60:
                score_away += 1.5
            elif bets >= 70 and money <= 50:
                score_home += 1

        # Moneyline Odds
        moneyline = odds.get("moneyline", {})
        h_odds = moneyline.get(home)
        a_odds = moneyline.get(away)
        if isinstance(h_odds, (int, float)) and h_odds < 0:
            score_home += 1
        elif isinstance(a_odds, (int, float)) and a_odds < 0:
            score_away += 1

        # Final Pick
        if score_home > score_away:
            winner_pick = home
        elif score_away > score_home:
            winner_pick = away
        else:
            winner_pick = random.choice([home, away])

        recommendations.append({
            "matchup": matchup,
            "winner_pick": winner_pick
        })

    return recommendations
