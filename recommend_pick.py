from consensus_scraper import get_public_betting_consensus
from bullpen_scraper import get_team_bullpen_era
from weather_fetcher import get_weather
import random

PARK_FACTORS = {
    "Angel Stadium": 1.02, "Busch Stadium": 0.95, "Chase Field": 1.04, "Citizens Bank Park": 1.06, "Citi Field": 0.97,
    "Comerica Park": 0.98, "Coors Field": 1.35, "Dodger Stadium": 1.00, "Fenway Park": 1.08, "Globe Life Field": 1.01,
    "Great American Ball Park": 1.12, "Guaranteed Rate Field": 1.04, "Kauffman Stadium": 0.96, "loanDepot park": 0.94,
    "Minute Maid Park": 1.01, "Nationals Park": 1.01, "Oakland Coliseum": 0.92, "Oracle Park": 0.90, "Petco Park": 0.85,
    "PNC Park": 0.98, "Progressive Field": 1.00, "Rogers Centre": 1.09, "T-Mobile Park": 0.94, "Target Field": 0.99,
    "Tropicana Field": 0.93, "Truist Park": 1.05, "Wrigley Field": 1.07, "Yankee Stadium": 1.12,
    "American Family Field": 1.03, "Oriole Park at Camden Yards": 1.00
}

BALLPARK_CITIES = {
    "Angel Stadium": "Anaheim", "Busch Stadium": "St. Louis", "Chase Field": "Phoenix", "Citizens Bank Park": "Philadelphia",
    "Citi Field": "New York", "Comerica Park": "Detroit", "Coors Field": "Denver", "Dodger Stadium": "Los Angeles",
    "Fenway Park": "Boston", "Globe Life Field": "Arlington", "Great American Ball Park": "Cincinnati",
    "Guaranteed Rate Field": "Chicago", "Kauffman Stadium": "Kansas City", "loanDepot park": "Miami",
    "Minute Maid Park": "Houston", "Nationals Park": "Washington", "Oakland Coliseum": "Oakland",
    "Oracle Park": "San Francisco", "Petco Park": "San Diego", "PNC Park": "Pittsburgh", "Progressive Field": "Cleveland",
    "Rogers Centre": "Toronto", "T-Mobile Park": "Seattle", "Target Field": "Minneapolis",
    "Tropicana Field": "St. Petersburg", "Truist Park": "Atlanta", "Wrigley Field": "Chicago",
    "Yankee Stadium": "New York", "American Family Field": "Milwaukee", "Oriole Park at Camden Yards": "Baltimore"
}

WEIGHTS = {
    "pitching": 1.5,
    "ops": 1.2,
    "bullpen": 1.0,
    "win_pct": 1.0,
    "park_factor": 0.5,
    "weather": 0.5,
    "betting_sharp": 1.0,
    "betting_fade": 0.5,
    "odds": 1.0
}

def normalize(value, min_val, max_val):
    try:
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
    except:
        return 0.0

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
        moneyline = odds.get("moneyline", {})
        h_odds = moneyline.get(home)
        a_odds = moneyline.get(away)
        score_home = 0
        score_away = 0

        home_pitcher = game["home_pitcher"].get("recent", {})
        away_pitcher = game["away_pitcher"].get("recent", {})
        for metric, min_val, max_val in [("era", 1.5, 6.0), ("whip", 0.8, 2.0), ("k9", 5.0, 13.0), ("bb9", 1.0, 5.0)]:
            h = home_pitcher.get(metric)
            a = away_pitcher.get(metric)
            if h is not None and a is not None:
                if metric == "era" and abs(h - a) < 0.2:
                    continue
                if metric in ["era", "whip", "bb9"]:
                    h_val = 1 - normalize(h, min_val, max_val)
                    a_val = 1 - normalize(a, min_val, max_val)
                else:
                    h_val = normalize(h, min_val, max_val)
                    a_val = normalize(a, min_val, max_val)
                delta = h_val - a_val
                score_home += max(0, delta) * WEIGHTS["pitching"]
                score_away += max(0, -delta) * WEIGHTS["pitching"]

        try:
            home_ops = float(game["home_stats"].get("ops"))
            away_ops = float(game["away_stats"].get("ops"))
            if abs(home_ops - away_ops) >= 0.010:
                home_val = normalize(home_ops, 0.600, 0.900)
                away_val = normalize(away_ops, 0.600, 0.900)
                delta = home_val - away_val
                score_home += max(0, delta) * WEIGHTS["ops"]
                score_away += max(0, -delta) * WEIGHTS["ops"]
            else:
                home_ops = away_ops = 0.0
        except:
            home_ops = away_ops = 0.0

        try:
            home_bp = bullpen_eras.get(home)
            away_bp = bullpen_eras.get(away)
            home_val = 1 - normalize(home_bp, 2.5, 5.5)
            away_val = 1 - normalize(away_bp, 2.5, 5.5)
            delta = home_val - away_val
            score_home += max(0, delta) * WEIGHTS["bullpen"]
            score_away += max(0, -delta) * WEIGHTS["bullpen"]
        except:
            pass

        try:
            home_win = float(game["home_stats"].get("win_pct"))
            away_win = float(game["away_stats"].get("win_pct"))
            home_val = normalize(home_win, 0.3, 0.7)
            away_val = normalize(away_win, 0.3, 0.7)
            delta = home_val - away_val
            score_home += max(0, delta) * WEIGHTS["win_pct"]
            score_away += max(0, -delta) * WEIGHTS["win_pct"]
        except:
            pass

        park_factor = PARK_FACTORS.get(venue, 1.00)
        if park_factor > 1.1:
            score_home += (home_ops > away_ops) * WEIGHTS["park_factor"]
            score_away += (away_ops > home_ops) * WEIGHTS["park_factor"]
        elif park_factor < 0.9:
            try:
                if home_pitcher.get("era") < away_pitcher.get("era"):
                    score_home += WEIGHTS["park_factor"]
                else:
                    score_away += WEIGHTS["park_factor"]
            except:
                pass

        weather = get_weather(BALLPARK_CITIES.get(venue, ""))
        if weather.get("wind_mph", 0) > 15:
            score_home += WEIGHTS["weather"] / 2
        elif weather.get("temp", 0) > 85:
            score_home += (home_ops > away_ops) * (WEIGHTS["weather"] / 2)
            score_away += (away_ops > home_ops) * (WEIGHTS["weather"] / 2)

        consensus = consensus_data.get(f"{away} vs {home}")
        if consensus:
            bets = consensus.get("bets")
            money = consensus.get("money")

            if money > bets and money >= 60:
                score_away += WEIGHTS["betting_sharp"]

            if bets >= 70 and money <= 50:
                score_home += WEIGHTS["betting_fade"]

            if isinstance(a_odds, (int, float)) and a_odds > 0 and money > bets and money >= 60:
                score_away += 0.5

        if isinstance(h_odds, (int, float)) and h_odds < 0:
            score_away += WEIGHTS["odds"]

        if abs(score_home - score_away) < 0.25:
            continue
        winner_pick = home if score_home > score_away else away

        recommendations.append({
            "matchup": matchup,
            "winner_pick": winner_pick
        })

    return recommendations
