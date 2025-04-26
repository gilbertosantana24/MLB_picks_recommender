# ⚾ MLB Picks Recommender

This project builds an intelligent recommendation system for MLB games based on real data — including pitcher stats, team performance, and betting odds.

It automatically analyzes each matchup and suggests the team most likely to win, along with a confidence percentage.

---

## 📈 Features

- ✅ Real pitcher ERA and WHIP from the MLB Stats API
- ✅ Real team record from the last 10 games
- ✅ Offensive stats (OPS) for better team performance comparison
- ✅ Current moneyline odds from The Odds API
- ✅ Score-based confidence percentage
- ✅ Auto-sorted picks (highest confidence first)
- ✅ Clear recommendation reasons

---

## 🚀 How to Run

1. **Clone this repository**

bash
git clone https://github.com/gilbertosantana24/MLB_picks_recommender.git
cd MLB_picks_recommender

install dependencies:
pip install requests
python run.py

/mlb_recommender/
├── mlb_stats.py       # 📊 Pulls MLB pitchers and team stats
├── odds_api.py        # 💰 Pulls current betting odds
├── recommender.py     # 🧠 Calculates picks and confidence
└── run.py             # 🚀 Main runner script

🧢 Chicago Cubs (away) vs New York Yankees (home)
✅ Recommended Pick: New York Yankees
📊 92% confidence
🔰 Confidence Level: 🔥 High Confidence
🧠 Reasons: Better home pitcher ERA, Better home pitcher WHIP, Better last 10 games record (home) [7/10], Better OPS (home), Favorite in moneyline (home)
--------------------------------------------------

