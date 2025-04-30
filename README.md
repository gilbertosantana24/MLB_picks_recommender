# ⚾ MLB Picks Recommender

This app recommends MLB game picks using real-time statistics and betting odds.

---

## 📈 Features

- ✅ Pulls pitcher stats (ERA, WHIP, K/9, BB/9) from MLB Stats API  
- ✅ Pulls team stats (OPS, Win%) from MLB Stats API  
- ✅ Integrates betting odds (moneyline, totals) from The Odds API  
- ✅ Includes public betting consensus data (% bets, % money) from Action Network  
- ✅ Scores matchups and picks winners based on a custom rule-based algorithm  
- ✅ Suggests Over/Under picks based on prediction score and total line  
- ✅ Simple, clean frontend: only shows matchup, winner pick, and OU pick  

---

## 🖥️ UI Output Example

| Matchup                  | Recommended Winner Pick | Over/Under Pick |
|--------------------------|--------------------------|------------------|
| Yankees vs Red Sox       | Yankees                  | Under 8.5        |
| Dodgers vs Padres        | Dodgers                  | Over 9.0         |

*Confidence and reasons are used internally to determine picks but are not displayed.*

---

mlb_picks_recommender/
├── app.py                 # 📊 Streamlit frontend
├── mlb_stats.py           # 🧠 Pulls MLB team and pitcher stats
├── odd_api.py             # 💰 Pulls moneyline and totals odds
├── recommend_pick.py      # 🧮 Calculates picks and scores
├── consensus_scraper.py   # 🧠 Gets % bets and % money from Action Network
├── run.py                 # 🖥️ Optional CLI runner
└── README.md

Consensus data is scraped from Action Network — structure may break over time.

This is a deterministic rule-based model (not ML-based, but extendable).

Use for entertainment and analysis. Bet responsibly.

## 🚀 How to Run Locally

```bash
# Clone the repo
git clone https://github.com/your-username/MLB_picks_recommender.git
cd MLB_picks_recommender

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
