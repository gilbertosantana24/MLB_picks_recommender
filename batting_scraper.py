def get_team_k_bb_rates():
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=2024"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    team_rates = {}

    rows = soup.select("table#LeaderBoard1_dg1 tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        team = cols[1].text.strip()
        try:
            k_pct = float(cols[8].text.strip('%'))
            bb_pct = float(cols[9].text.strip('%'))
            team_rates[team] = {"k_pct": k_pct, "bb_pct": bb_pct}
        except:
            continue

    return team_rates
