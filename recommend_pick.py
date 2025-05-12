from consensus_scraper import get_public_betting_consensus
from bullpen_scraper import get_team_bullpen_era
from weather_fetcher import get_weather
from mlb_stats import get_run_diff_last_10
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
    "pitching": 1.0,
    "ops": 1.2,
    "bullpen": 1.0,
    "win_pct": 1.2,
    "run_diff": 1.5,
    "park_factor": 0.5,
    "weather": 0.5,
    "betting_sharp": 1.0,
    "betting_fade": 0.5,
    "odds": 1.5
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
        home_id = game.get("home_team_id")
        away_id = game.get("away_team_id")
        matchup = f"{away} (away) vs {home} (home)"
        odds = odds_data.get(f"{away} vs {home}", {})
        moneyline = odds.get("moneyline", {})
        h_odds = moneyline.get(home)
        a_odds = moneyline.get(away)
        score_home = 0
        score_away = 0

        debug = []

        # Penalización para equipos muy débiles
        try:
            home_win = float(game["home_stats"].get("win_pct", 0))
            away_win = float(game["away_stats"].get("win_pct", 0))
            if home_win < 0.4:
                score_home -= 1.0
                debug.append(("Low Win% Penalty", -1.0, 0))
            if away_win < 0.4:
                score_away -= 1.0
                debug.append(("Low Win% Penalty", 0, -1.0))
        except:
            pass

        try:
            home_diff = get_run_diff_last_10(home_id)
            away_diff = get_run_diff_last_10(away_id)
            if home_diff <= -15:
                score_home -= 1.0
                debug.append(("RunDiff Penalty", -1.0, 0))
            if away_diff <= -15:
                score_away -= 1.0
                debug.append(("RunDiff Penalty", 0, -1.0))
        except:
            pass

        home_pitcher = game["home_pitcher"]
        away_pitcher = game["away_pitcher"]
        pitch_score_home = 0
        pitch_score_away = 0

        for metric, min_val, max_val in [("era", 1.5, 6.0), ("whip", 0.8, 2.0), ("k9", 5.0, 13.0), ("bb9", 1.0, 5.0)]:
            h_recent = home_pitcher.get("recent", {}).get(metric)
            a_recent = away_pitcher.get("recent", {}).get(metric)
            h_season = home_pitcher.get(metric)
            a_season = away_pitcher.get(metric)

            if h_recent and h_season:
                h_combined = (h_recent + h_season) / 2
            else:
                h_combined = h_recent or h_season

            if a_recent and a_season:
                a_combined = (a_recent + a_season) / 2
            else:
                a_combined = a_recent or a_season

            if h_combined is not None and a_combined is not None:
                if metric == "era" and abs(h_combined - a_combined) < 0.2:
                    continue
                if metric in ["era", "whip", "bb9"]:
                    h_val = 1 - normalize(h_combined, min_val, max_val)
                    a_val = 1 - normalize(a_combined, min_val, max_val)
                else:
                    h_val = normalize(h_combined, min_val, max_val)
                    a_val = normalize(a_combined, min_val, max_val)
                delta = h_val - a_val
                pitch_score_home += max(0, delta) * WEIGHTS["pitching"]
                pitch_score_away += max(0, -delta) * WEIGHTS["pitching"]

        score_home += pitch_score_home
        score_away += pitch_score_away
        debug.append(("Pitching", round(pitch_score_home, 2), round(pitch_score_away, 2)))

        try:
            home_ops = float(game["home_stats"].get("ops"))
            away_ops = float(game["away_stats"].get("ops"))
            home_val = normalize(home_ops, 0.600, 0.900)
            away_val = normalize(away_ops, 0.600, 0.900)
            delta = home_val - away_val
            ops_home = max(0, delta) * WEIGHTS["ops"]
            ops_away = max(0, -delta) * WEIGHTS["ops"]
            score_home += ops_home
            score_away += ops_away
            debug.append(("OPS", round(ops_home, 2), round(ops_away, 2)))
        except:
            pass

        try:
            home_bp = bullpen_eras.get(home)
            away_bp = bullpen_eras.get(away)
            home_val = 1 - normalize(home_bp, 2.5, 5.5)
            away_val = 1 - normalize(away_bp, 2.5, 5.5)
            delta = home_val - away_val
            bp_home = max(0, delta) * WEIGHTS["bullpen"]
            bp_away = max(0, -delta) * WEIGHTS["bullpen"]
            score_home += bp_home
            score_away += bp_away
            debug.append(("Bullpen", round(bp_home, 2), round(bp_away, 2)))
        except:
            pass

        try:
            home_val = normalize(home_win, 0.3, 0.7)
            away_val = normalize(away_win, 0.3, 0.7)
            delta = home_val - away_val
            wp_home = max(0, delta) * WEIGHTS["win_pct"]
            wp_away = max(0, -delta) * WEIGHTS["win_pct"]
            score_home += wp_home
            score_away += wp_away
            debug.append(("Win %", round(wp_home, 2), round(wp_away, 2)))
        except:
            pass

        try:
            diff_delta = normalize(home_diff, -20, 20) - normalize(away_diff, -20, 20)
            rd_home = max(0, diff_delta) * WEIGHTS["run_diff"]
            rd_away = max(0, -diff_delta) * WEIGHTS["run_diff"]
            score_home += rd_home
            score_away += rd_away
            debug.append(("Run Diff", round(rd_home, 2), round(rd_away, 2)))
        except:
            pass

        if isinstance(h_odds, (int, float)) and h_odds < 0:
            score_away += WEIGHTS["odds"]
            debug.append(("Odds", 0, WEIGHTS["odds"]))

        if abs(score_home - score_away) < 0.25:
            continue

        winner_pick = home if score_home > score_away else away

        print(f"🧢 {matchup}")
        for factor, h_score, a_score in debug:
            print(f"  {factor:<15}: {home} +{h_score} | {away} +{a_score}")
        print(f"  TOTAL           : {home} {round(score_home,2)} | {away} {round(score_away,2)}")
        print(f"  ✅ Winner: {winner_pick}")
        print("-" * 40)

        recommendations.append({
            "matchup": matchup,
            "winner_pick": winner_pick
        })

    return recommendations
