# Copyright (C) 2021 Silvan Fischbacher

import numpy as np
import pandas as pd

from fussballgott import team


def get_teams_from_df(df, columns=["Home", "Away"]):
    teams = []
    for c in columns:
        teams.append(df[c])
    teams = np.concatenate(teams)
    return np.unique(teams)


def league(files, delimiter=";"):
    if len(files) == 1 or isinstance(files, str):
        schedule_and_results = pd.read_csv(
            files, delimiter=delimiter, encoding="unicode_escape"
        )
        schedule = schedule_and_results[["Home", "Away"]].copy()
        teams = get_teams_from_df(schedule_and_results)
        table, missing_games = create_table(schedule_and_results, teams)
    elif len(files) == 2:
        schedule = pd.read_csv(files[0], delimiter=delimiter, encoding="unicode_escape")
        table = pd.read_csv(
            files[1],
            delimiter=delimiter,
            encoding="unicode_escape",
            index_col=0,
        )
        teams = get_teams_from_df(table, ["Team"])
        missing_games = get_missing_games(table, schedule)
    else:
        print("files has wrong type, should be list, array or str")
    teams_dict = {}
    for t in teams:
        teams_dict[t] = team.team(
            name=t,
            GoalsF=table[table["Team"] == t]["GF"].values[0],
            GoalsA=table[table["Team"] == t]["GA"].values[0],
            played=table[table["Team"] == t]["Played"].values[0],
            penalty_scoring=0.75,
        )
    return teams_dict, schedule, table, missing_games


def tournament(filename, path="", delimiter=";"):
    mode = pd.read_csv(
        path + filename + "mode.CSV",
        header=None,
        index_col=0,
        squeeze=True,
        delimiter=";",
    ).to_dict()
    if mode["Group Stage"] == "True":
        group_stage = True
    elif mode["Group Stage"] == "False":
        group_stage = False
    else:
        print(
            "Don't know {} in the mode file for 'Group Stage'. "
            "Use 'True' or 'False'.".format(mode["Group Stage"])
        )
    ko = int(mode["First knockout round"])
    ko_round = []
    while ko > 1:
        ko_round.append(
            pd.read_csv(path + filename + "{}.CSV".format(ko), delimiter=delimiter)
        )
        ko = int(ko / 2)
    try:
        if int(mode["number of additional teams qualified"]) > 0:
            ko_round.append(
                pd.read_csv(path + filename + "special_rule.CSV", delimiter=delimiter)
            )
    except Exception:
        pass
    team_table = pd.read_csv(path + filename + "teams.csv", delimiter=";")
    teams = {}
    if group_stage:
        groups = dict.fromkeys(team_table["Group"])

    def update_group(dic, k, value):
        a = dic[k]
        if a is None:
            return [value]
        else:
            a.append(value)
        return a

    for name in team_table["Name"].values:
        try:
            penalty = team_table[team_table["Name"] == name]["Penalty Scoring"].values[
                0
            ]
        except Exception:
            penalty = 0.75
        teams[name] = team.team(
            name=name,
            GoalsF=team_table[team_table["Name"] == name]["GoalsF"].values[0],
            GoalsA=team_table[team_table["Name"] == name]["GoalsA"].values[0],
            played=team_table[team_table["Name"] == name]["Played"].values[0],
            penalty_scoring=penalty,
        )
        if group_stage:
            g = team_table[team_table["Name"] == name]["Group"].values[0]
            groups[g] = update_group(groups, g, name)
    if group_stage:
        return mode, ko_round, teams, groups
    else:
        return mode, ko_round, teams


def enrich_table(table):
    if "GD" not in table.index:
        table["GD"] = table["GF"] - table["GA"]
    return table


def create_table(sched_n_r, teams):
    games = np.shape(sched_n_r)[0]
    missing_games = np.ones(games, dtype=bool)
    table = pd.DataFrame(index=teams)
    table["Team"] = table.index
    table["Played"] = 0
    table["GF"] = 0
    table["GA"] = 0
    table["GD"] = 0
    table["Points"] = 0

    for i in range(games):
        game = sched_n_r[i : i + 1]
        if game["Goals Home"].isnull().values[0]:
            pass
        else:
            missing_games[i] = False
            table["Played"][game["Home"].values[0]] += 1
            table["Played"][game["Away"].values[0]] += 1
            table["GF"][game["Home"].values[0]] += game["Goals Home"].values[0]
            table["GF"][game["Away"].values[0]] += game["Goals Away"].values[0]
            table["GA"][game["Home"].values[0]] += game["Goals Away"].values[0]
            table["GA"][game["Away"].values[0]] += game["Goals Home"].values[0]
            if game["Goals Home"].values[0] > game["Goals Away"].values[0]:
                table["Points"][game["Home"].values[0]] += 3
            if game["Goals Home"].values[0] < game["Goals Away"].values[0]:
                table["Points"][game["Away"].values[0]] += 3
            if game["Goals Home"].values[0] == game["Goals Away"].values[0]:
                table["Points"][game["Home"].values[0]] += 1
                table["Points"][game["Away"].values[0]] += 1
    table["GD"] = table["GF"] - table["GA"]
    sorted_table = tiebreaker(table, rule="Goal Difference")
    sorted_table.index = np.arange(1, len(teams) + 1)
    return sorted_table, missing_games


def tiebreaker(table, rule="Goal Difference"):
    if rule == "Goal Difference":
        return table.sort_values(["Points", "GD", "GF"], ascending=False)
    else:
        print("Rule {} not implemented yet".format(rule))


def get_missing_games(table, schedule):
    index = np.zeros_like(schedule["Home"].values, dtype=bool)
    teams = get_teams_from_df(schedule, ["Home", "Away"])
    for t in teams:
        played = table[table["Team"] == t]["Played"].values[0]
        t_schedule = schedule[
            np.logical_or(schedule["Home"] == t, schedule["Away"] == t)
        ].index
        index[t_schedule[played:]] = True
    return index
