from pprint import pprint

import pandas
import requests

ENDPOINT = "http://games.espn.com/ffl/api/v2/"
LEAGUE_SETTINGS = ENDPOINT + "leagueSettings"
SCOREBOARD = ENDPOINT + "scoreboard"
SCHEDULE = ENDPOINT + "schedule"


def request_from_json(url, params, cookies=None):
    """
    Performs a get request and parses the response JSON into a dict
    :param url:
    :param params:
    :param cookies:
    :return: dict from JSON response
    """
    if cookies is None:
        cookies = {}
    r = requests.get(url, params, cookies=cookies)
    status = r.status_code
    data = {}
    if status == 200:
        data = r.json()
    data['status_code'] = r.status_code
    return data


def get_data(league_id, year):
    params = {'leagueId': league_id,
              'seasonId': year}

    data = request_from_json(LEAGUE_SETTINGS, params)
    scoreboard_data = request_from_json(SCOREBOARD, params)
    schedule_data = request_from_json(SCHEDULE, params)
    league = get_league_data(data, scoreboard_data)
    teams = get_team_data(data)
    schedule = get_schedule_data(schedule_data)

    return league, teams, schedule


def get_league_data(data, scoreboard_data):
    settings = data.get('leaguesettings', {})

    name = settings.get('name', '')
    num_teams = settings.get('size', 0)
    num_playoff_teams = settings.get('playoffTeamCount', 0)
    tie_rule = settings.get('tieRule', -1)
    seed_tiebreaker = settings.get('playoffSeedingTieRule', -1)
    num_regular_season_matchups = settings.get('regularSeasonMatchupPeriodCount', 0)

    div_data = settings.get('divisions', {})
    divisions = {}
    for div in div_data:
        id = div.get('divisionId')
        divisions[id] = div.get('name')

    team_data = settings.get('teams', {})
    team_names = {}
    for id, team in team_data.items():
        id = team.get('teamId')
        team_names[id] = team.get('teamLocation', '') + " " + team.get('teamNickname', '')

    scoreboard = scoreboard_data.get('scoreboard', {})
    current_period = scoreboard.get('scoringPeriodId', 0)
    return {'name': name, 'num_teams': num_teams, 'num_playoff_teams': num_playoff_teams, 'tie_rule': tie_rule,
            'seed_tiebreaker': seed_tiebreaker, 'num_regular_season_matchups': num_regular_season_matchups,
            'current_period': current_period, 'divisions': divisions, 'team_names': team_names}


def get_team_data(data):
    settings = data.get('leaguesettings', {})

    raw_team_data = settings.get('teams', {})
    team_data = {}
    for tm_id, tm in raw_team_data.items():
        id = tm.get('teamId')
        name = tm.get('teamLocation', '') + " " + tm.get('teamNickname', '')
        owner = tm.get('owners', [{}])[0].get('firstName', '') + " " + tm.get('owners', [{}])[0].get('lastName', '')
        logo = tm.get('logoUrl', '')
        div_id = tm.get('division', {}).get('divisionId', -1)
        team_data[id] = {'name': name, 'owner': owner, 'logo': logo, 'id': id, 'div_id': div_id}

    return team_data


def get_schedule_data(schedule_data):
    """
    Returns the schedule as Pandas dataframe
    :param schedule_data: raw response of schedule data from API
    :return: scheudle as a Pandas dataframe
    """
    schedule_items = schedule_data.get("leagueSchedule", {}).get('scheduleItems', [])
    schedule_dict = {'week': [], 'home_id': [], 'home_score': [], 'away_id': [], 'away_score': [], 'outcome': [],
                     'probability': []}
    for matchup_data in schedule_items:
        matchup_period = matchup_data.get('matchupPeriodId')
        matchups = matchup_data.get('matchups', [{}])
        for matchup in matchups:
            home_team_id = matchup.get('homeTeamId', -1)
            home_team_score = matchup.get('homeTeamScores', [0.0])[0]
            away_team_id = matchup.get('awayTeamId', -1)
            away_team_score = matchup.get('awayTeamScores', [0.0])[0]
            outcome_data = matchup.get('outcome')
            schedule_dict['week'].append(matchup_period)
            schedule_dict['home_id'].append(home_team_id)
            schedule_dict['home_score'].append(home_team_score)
            schedule_dict['away_id'].append(away_team_id)
            schedule_dict['away_score'].append(away_team_score)
            schedule_dict['outcome'].append(outcome_data)
            schedule_dict['probability'].append(None)

    return pandas.DataFrame.from_dict(schedule_dict)

# pprint(get_data(2253602, 2017)[0])
# pprint(get_data(2253602, 2017)[0])