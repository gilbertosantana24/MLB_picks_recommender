import requests
from bs4 import BeautifulSoup

def get_team_bullpen_era():
    url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=8&season=2024&month=0&season1=2024"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    bullpen_eras = {}

    rows = soup.select("table#LeaderBoard1_dg1 tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        team = cols[1].text.strip()
        era = cols[7].text.strip()
        try:
            bullpen_eras[team] = float(era)
        except:
            continue

    return bullpen_eras
