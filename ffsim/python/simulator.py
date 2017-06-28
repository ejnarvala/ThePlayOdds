import copy
import math
import random

from . import download


def initialize_team_stats(team_name, schedule):
    scores = []
    sum = 0.0
    count = 0
    wins = 0
    if len(team_name) > 0:
        for week, matchups in schedule.items():
            for matchup in matchups:
                if matchup.get("home") == team_name:
                    score = matchup.get("homeScore")
                    sum += score
                    scores.append(score)
                    if score > 0:
                        count += 1
                    if matchup.get("homeScore") > matchup.get("awayScore"):
                        wins += 1
                if matchup.get("away") == team_name:
                    score = matchup.get("awayScore")
                    sum += score
                    scores.append(score)
                    if score > 0:
                        count += 1
                    if matchup.get("awayScore") > matchup.get("homeScore"):
                        wins += 1
        average = round(sum / count, 2)
        dev_sum = 0
        for score in scores:
            if score > 0:
                dev_sum += math.pow((score - average), 2)
        std_dev = round(math.sqrt(dev_sum / count), 2)
        return average, std_dev, wins, count - wins


class league():
    "Object representing current state of a fantasy football league."
    divisions = {}
    schedule = {}
    teams = []

    def __init__(self, league_id, season):
        self.divisions = download.league_division_data(league_id, season)
        self.schedule = download.league_schedule_data(league_id, season)
        for div, teams in self.divisions.items():
            for team_name in teams:
                average, std_dev, wins, losses = initialize_team_stats(team_name, self.schedule)
                self.teams.append(team(team_name, div, average, std_dev, wins, losses))

    def get_team_by_name(self, name):
        for tm in self.teams:
            if tm.name == name:
                return tm
        return None


class simulated_league:
    divisions = {}
    schedule = {}
    teams = []
    seed = 0

    def __init__(self, divisions, schedule, teams):
        self.divisions = divisions
        self.schedule = schedule
        self.teams = teams

    def get_team_by_name(self, team_name):
        for team in self.teams:
            if team_name == team.name:
                return team
        return None

    def simulate(self):
        for week, matchups in self.schedule.items():
            for matchup in matchups:
                if matchup.get("homeScore") == 0.0 and matchup.get("awayScore") == 0.0:
                    home = self.get_team_by_name(matchup.get("home"))
                    away = self.get_team_by_name(matchup.get("away"))
                    homeScore = round(random.gauss(home.average, home.std_dev), 1)
                    # print("Generated: ", homeScore)
                    awayScore = round(random.gauss(away.average, away.std_dev), 1)
                    matchup['homeScore'] = homeScore
                    matchup['awayScore'] = awayScore
                    if homeScore > awayScore:
                        home.wins += 1
                    else:
                        away.wins += 1

    def tiebreak(self, tied_teams):
        h2h_dict = {}
        tied_tm_names = []
        for tm in tied_teams:
            tied_tm_names.append(tm.name)
            h2h_dict[tm.name] = (0, 0)
        # print("Breaking ties between: ", tied_tm_names)
        for week, matchups in self.schedule.items():
            for matchup in matchups:
                home = matchup.get("home")
                away = matchup.get("away")
                if home in tied_tm_names and away in tied_tm_names:
                    # update h2h_dict for home
                    homeScore = matchup.get("homeScore")
                    awayScore = matchup.get("awayScore")
                    if homeScore > 0.0 and awayScore > 0.0:
                        if homeScore > awayScore:
                            h_wins, h_games = h2h_dict.get(home)
                            h2h_dict[home] = h_wins + 1, h_games + 1
                            a_wins, a_games = h2h_dict.get(away)
                            h2h_dict[away] = a_wins + 0, a_games + 1
                        else:
                            h_wins, h_games = h2h_dict.get(home)
                            h2h_dict[home] = h_wins + 0, h_games + 1
                            a_wins, a_games = h2h_dict.get(away)
                            h2h_dict[away] = a_wins + 1, a_games + 1
        tiebreak_heuristic_dict = {}
        num_games_set = set()
        for tm_name, (wins, games) in h2h_dict.items():
            tiebreak_heuristic_dict[tm_name] = wins + games
            num_games_set.add(games)
        team_heuristic_dict = {}
        for tm in tied_teams:
            team_heuristic_dict[tm] = tiebreak_heuristic_dict[tm.name]

        sorted_pf = sorted(tied_teams, key=lambda team: team.average, reverse=True)
        sorted_h2h = sorted(sorted_pf, key=lambda team: team_heuristic_dict.get(team), reverse=True)
        if (len(num_games_set) == 1 and num_games_set.pop() is not 0):
            # print("H2H was used to break the tie.")
            return sorted_h2h[0]
        else:
            # print("PF was used to break the tie.")
            return sorted_pf[0]


    def get_standings(self):
        wins_dict = {}
        standings = []
        for team in self.teams:
            wins_dict.setdefault(team.wins, []).append(team)
        win_list = sorted(wins_dict.keys(), reverse=True)
        for num in win_list:
            tied_teams = wins_dict.get(num)
            if len(tied_teams) == 1:
                standings.append(tied_teams[0])
            else:
                while (len(tied_teams) > 1):
                    tie_winner = self.tiebreak(tied_teams)
                    # print ("Tie winner: ", tie_winner.name)
                    standings.append(tie_winner)
                    tied_teams.remove(tie_winner)
                standings.append(tied_teams[0])
        div1 = standings[0].division
        div_2_winner_index = -1
        div_standings = []
        div_standings.append(standings[0])
        for i in range(1, len(standings)):
            if standings[i].division is not div1:
                div_2_winner_index = i
                break
        if div_2_winner_index is not 1:
            # move div_2_ winner to index 1, move everyone else down.
            div_standings.append(standings[div_2_winner_index])
            for i in range(1, len(standings)):
                if standings[i] not in div_standings:
                    div_standings.append(standings[i])
            return div_standings
        else:
            return standings
        # for tm in standings:
        #     print(tm.name, end=",")
        # print()
        # return standings

class team:
    "Class representing a fantasy football team"
    name = ""
    division = ""
    average = 0.0
    std_dev = 0.0
    wins = 0
    losses = 0
    average_allowed = 0.0

    def __init__(self, name, division, average, std_dev, wins, losses):
        self.name = name
        self.division = division
        self.average = average
        self.std_dev = std_dev
        self.wins = wins
        self.losses = losses

    def __str__(self):
        team_str = str(self.name) + "(" + str(self.wins) + "-" + str(self.losses) + ") " + str(self.average) + " PF/G"
        record = str("(" + str(self.wins) + "-" + str(self.losses) + ")")
        return str("%-32s %-7s %5.1f PF/G" % (self.name, record, self.average))


def run_simulation(espn_url):
    try:
        espnurl = espn_url.split('?')
        espnurl = espnurl[1] #takes second half 'leagueID=XXXXXX&seasonID=XXXX'
        espnurl = espnurl.split('&')
    # print(espn_url)
        league_id = espnurl[0].split('=')
        league_id = league_id[1]
        season_id = espnurl[1].split('=')
        season_id = season_id[1]
    except IndexError:
        return ["Sorry, the URL:", "\"" + espn_url + "\"","Didn't Work"]
    lg = league(league_id, season_id)
    results_dict = {}
    for tm in lg.teams:
        results_dict[tm.name] = [0 for i in range(len(lg.teams))]
    sims = 100
    for i in range(sims):
        curr_teams = copy.deepcopy(lg.teams)
        curr_schedule = copy.deepcopy(lg.schedule)
        sim_lg = simulated_league(lg.divisions, curr_schedule, curr_teams)
        # sim_lg.simulate()
        standings = sim_lg.get_standings()
        adjusted_standings = []
        team_average = None
        for k in range(len(standings)):
            if standings[k].name != "Team Average":
                adjusted_standings.append(standings[k])
            else:
                team_average = standings[k]
        adjusted_standings.append(team_average)
        # for j in range(len(standings)):
        #     results_dict[standings[j].name][j] += 1
        for j in range(len(adjusted_standings)):
            results_dict[adjusted_standings[j].name][j] += 1
            # print(j + 1, adjusted_standings[j].name, end=", ")
        # print()
    csv_file = open("results.csv", "w")
    finstr = []
    for tm, results in results_dict.items():
        print(lg.get_team_by_name(tm))
        finstr.append(str(lg.get_team_by_name(tm)))
    #     csv_file.write(tm + ",")
    #     for num in results:
    #         csv_file.write(str(num / sims) + ",")
    #     csv_file.write("\n")
    # csv_file.close()
    return finstr
# run_simulation(565232, 2016)
# espn_url = "http://games.espn.go.com/ffl/schedule?leagueId=565232&seasonId=2016"
# espn_url = espn_url.split('?')
# espn_url = espn_url[1] #takes second half 'leagueID=XXXXXX&seasonID=XXXX'
# espn_url = espn_url.split('&')
# league_id = espn_url[0].split('=')
# league_id = league_id[1]
# season_id = espn_url[1].split('=')
# season_id = espn_url[1]
