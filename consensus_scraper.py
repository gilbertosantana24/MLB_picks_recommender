import requests
from bs4 import BeautifulSoup

def get_public_betting_consensus():
    url = "https://www.actionnetwork.com/mlb/public-betting"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    consensus_data = {}

    matchups = soup.select("div[class*='styles__MatchupContent']")  

    for matchup in matchups:
        try:
            teams_text = matchup.select_one("p").text.strip()
            teams = teams_text.replace(" at ", " vs ") 

            percentages = matchup.select("div[class*='styles__Bars'] span")
            bets = int(percentages[0].text.strip('%'))
            money = int(percentages[1].text.strip('%'))

            consensus_data[teams] = {
                "bets": bets,
                "money": money
            }
        except Exception:
            continue

    return consensus_data
