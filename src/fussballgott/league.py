# Copyright (C) 2021 Silvan Fischbacher

"""
File with all functions needed to simulate a league
"""
from itertools import combinations, permutations

import numpy as np
import pandas as pd
from tqdm import trange

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
    team_list = teams.keys()
    if isinstance(schedule, int):
        if schedule % 2 == 0:
            one_round = pd.DataFrame(
                list(permutations(teams, 2)), columns=["Home", "Away"]
            )
            sch = one_round
            while schedule > 2:
                sch = sch.append(one_round, ignore_index=True)
                schedule -= 2
        else:
            one_round = pd.DataFrame(
                list(combinations(teams, 2)), columns=["Home", "Away"]
            )
            sch = one_round
            while schedule > 1:
                sch = sch.append(one_round, ignore_index=True)
                schedule -= 1
        schedule = sch
        missing_games = np.ones(schedule.shape[0], dtype=bool)

    if table is None:
        table = pd.DataFrame(columns=["Team", "Played", "GF", "GA", "GD", "Points"])
        table["Team"] = team_list
        table = table.fillna(0)
        table.index = np.arange(1, len(team_list) + 1)
    n_sim = int(n_sim)
    n_teams = len(teams)
    sched, tab, dict_num2team = pd_to_np(schedule, table)
    ranking_table = np.zeros((n_teams, n_teams))
    for i in trange(n_sim, disable=not progressbar):
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
    n = np.shape(table)[0]
    t = []
    for i in range(n):
        t.append(dict_num2team[i])
    pd_table = pd.DataFrame(index=t, columns=np.arange(1, n + 1), data=table)
    return pd_table
