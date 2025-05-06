# ⚾ Slider MLB Picks Recommender (CLI Version)

This project provides daily MLB betting pick recommendations directly in your terminal.  
It uses live data such as team stats, pitcher metrics, weather, betting odds, bullpen stats, and public betting consensus to make an informed pick for each game.

---

## 🔧 How it Works

The app assigns scores to each team based on:
- **Pitcher recent form** (ERA, WHIP, K/9, BB/9)
- **Team OPS**
- **Bullpen ERA** (from Fangraphs)
- **Win percentage**
- **Ballpark factor**
- **Weather** (temperature and wind, via OpenWeather)
- **Betting consensus** (sharp/public splits)
- **Moneyline odds**

The team with the highest score is picked as the winner.

You will see something like this:
📅 Fetching MLB games for 2025-05-06...
🎯 MLB Picks for Today:
🧢 Yankees (away) vs Red Sox (home)
✅ Pick: Red Sox
----------------------------------------

## 🚀 How to Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt

2. python run.py

