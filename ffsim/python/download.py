import urllib.request
from bs4 import BeautifulSoup


def data(url):
    # Returns a BeautifulSoup object for the given URL
    r = urllib.request.urlopen(url).read()
    return BeautifulSoup(r, "html.parser")


def league_schedule_data(league_id, season):
    # Imports the schedule and scores
    url = "http://games.espn.go.com/ffl/schedule?leagueId=" + str(league_id) + "&seasonId=" + str(season)
    soup = data(url)
    schedule_dict = {}
    week = 0
    table = soup.find("table", {"class": "tableBody"})
    rows = table.findAll("tr")
    for row in rows:
        if row.attrs.get("class") == ['tableHead']:
            weekStr = row.text.strip().replace("WEEK ", " ").strip()
            if weekStr.isnumeric():
                week = int(weekStr)
                schedule_dict[week] = []
        if row.attrs.get("bgcolor") == "#f2f2e8" or row.attrs.get("bgcolor") == "#f8f8f2":
            matchup = row.findAll("a")
            away = matchup[0].text
            home = matchup[1].text
            score = matchup[2].text
            awayScore = 0.0
            homeScore = 0.0
            if score.find("-") != -1:
                scores = score.split("-")
                awayScore = float(scores[0])
                homeScore = float(scores[1])
            schedule_dict.get(week).append({"home" : home, "away" : away, "homeScore": homeScore, "awayScore" : awayScore})
    return schedule_dict


def league_division_data(league_id, season):
    # Gets the all the teams in the league organized by division
    url = "http://games.espn.go.com/ffl/standings?leagueId=" + str(league_id) + "&seasonId=" + str(season)
    soup = data(url)
    table = soup.find("table", {"cellpadding" : "0", "cellspacing" : "0", "width" : "100%"})
    divisions = table.findAll("table")
    div_dict = {}
    for div in divisions:
        divName = div.find("tr").find("td").text
        div_dict[divName] = []
        divRows = div.findAll("tr", {"class":"tableBody"})
        for row in divRows:
            team = row.find("a").text
            div_dict[divName].append(team)
    return div_dict
