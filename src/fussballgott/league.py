# Copyright (C) 2021 Silvan Fischbacher

from itertools import combinations, permutations

import numpy as np
import pandas as pd
from tqdm.auto import trange

from fussballgott import fussball


def simulate(
    teams,
    schedule=2,
    table=None,
    missing_games=None,
    n_sim=1,
    include_goals_against=True,
    sorting="standard",
    progressbar=True,
    tournament_mode=False,
):
    """
    Simulate a league with given teams and schedule.

    :param teams: Dictionary with teams as keys and team objects as values
    :param schedule: Schedule of the league. If int, all teams play against each other
        schedule times. If pd.DataFrame, the schedule is given as a table with columns
        "Home" and "Away".
    :param table: Table of the league. If None, a new table is created
    :param missing_games: List of games that are not played
    :param n_sim: Number of simulations
    :param include_goals_against: If True, the average goals against are included
    :param sorting: Sorting of the table
    :param progressbar: If True, a progressbar is shown
    :param tournament_mode: If True, the table is returned, if False, the ranking table
        is returned
    :return: table (if tournament_mode) or ranking table (if not tournament_mode)
    """
    team_list = teams.keys()

    # no schedule given, create one
    if isinstance(schedule, int):
        if schedule % 2 == 0:
            one_round = pd.DataFrame(
                list(permutations(teams, 2)), columns=["Home", "Away"]
            )
            sch = one_round
            while schedule > 2:
                sch = pd.concat([sch, one_round], ignore_index=True)
                schedule -= 2
        else:
            one_round = pd.DataFrame(
                list(combinations(teams, 2)), columns=["Home", "Away"]
            )
            sch = one_round
            while schedule > 1:
                sch = pd.concat([sch, one_round], ignore_index=True)
                schedule -= 1
        schedule = sch
        missing_games = np.ones(schedule.shape[0], dtype=bool)

    # table not given, create one
    if table is None:
        table = pd.DataFrame(columns=["Team", "Played", "GF", "GA", "GD", "Points"])
        table["Team"] = team_list
        table = table.fillna(0)
        table.index = np.arange(1, len(team_list) + 1)

    n_sim = int(n_sim)
    n_teams = len(teams)
    sched, tab, dict_num2team = pd_to_np(schedule, table)
    ranking_table = np.zeros((n_teams, n_teams))

    # simulate the whole league n_sim times
    for _ in trange(n_sim, disable=not progressbar):
        changed_table = simulate_once(
            sched,
            tab,
            teams,
            missing_games,
            dict_num2team,
            include_goals_against,
        )

        changed_table, ranking = fussball.sort(changed_table, sorting=sorting)

        for j in range(n_teams):
            ranking_table[int(ranking[j]), j] += 1

    if tournament_mode:
        return changed_table, dict_num2team
    else:
        return np_to_pd(ranking_table / n_sim, dict_num2team)


def simulate_once(
    schedule,
    table,
    teams,
    missing_games,
    dict_num2team,
    include_goals_against=True,
):
    """
    Simulate a league with given teams and schedule.

    :param schedule: numpy array with schedule
    :param table: numpy array with table
    :param teams: Dictionary with teams as keys and team objects as values
    :param missing_games: List of games that are not played
    :param dict_num2team: Dictionary that maps indices to teams
    :param include_goals_against: If True, the average goals against are included
    :return: changed table
    """

    changed_table = table.copy()
    index = np.arange(len(missing_games))
    for i in index[missing_games]:
        s1 = schedule[i, 0]
        s2 = schedule[i, 1]
        t1 = dict_num2team[s1]
        t2 = dict_num2team[s2]
        h, a = fussball.simulate_game(
            teams[t1].AvGoalsF,
            teams[t2].AvGoalsF,
            teams[t1].AvGoalsA,
            teams[t2].AvGoalsA,
            include_goals_against=include_goals_against,
        )
        changed_table[s1, 0] += 1  # Played
        changed_table[s2, 0] += 1

        changed_table[s1, 1] += h  # GF
        changed_table[s2, 1] += a

        changed_table[s1, 2] += a  # GA
        changed_table[s2, 2] += h
        if h > a:
            changed_table[s1, 3] += 3  # Points
        elif h < a:
            changed_table[s2, 3] += 3
        else:
            changed_table[s1, 3] += 1
            changed_table[s2, 3] += 1
    return changed_table


def pd_to_np(schedule, table):
    """
    Convert pandas schedule and table to numpy arrays.

    :param schedule: Schedule of the league
    :param table: Table of the league
    :return: schedule and table as numpy arrays
    """
    new_schedule = schedule.copy()
    dict_n2t = {}
    np_table = table[["Played", "GF", "GA", "Points"]].values
    a, b = np.shape(np_table)
    new_table = np.zeros((a, b + 1))
    new_table[:, :-1] = np_table
    for i in range(len(table)):
        team = table["Team"][i + 1]
        new_schedule = new_schedule.replace(team, i)
        dict_n2t[team] = i
        dict_n2t[i] = team
        new_table[i, -1] = i
    return new_schedule.values, new_table, dict_n2t


def np_to_pd(table, dict_num2team):
    """
    Convert numpy table to pandas table.

    :param table: Table of the league
    :param dict_num2team: Dictionary that maps indices to teams
    :return: Table of the league as pandas table
    """
    n = np.shape(table)[0]
    t = []
    for i in range(n):
        t.append(dict_num2team[i])
    pd_table = pd.DataFrame(index=t, columns=np.arange(1, n + 1), data=table)
    return pd_table
