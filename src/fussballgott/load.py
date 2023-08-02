# Copyright (C) 2021 Silvan Fischbacher

import os

import numpy as np
import pandas as pd

from fussballgott import team


def get_teams_from_df(df, columns=["Home", "Away"]):
    """
    Get all teams from a DataFrame with a schedule.

    :param df: DataFrame with schedule
    :param columns: Columns of the DataFrame that contain the teams
    :return: Array with all teams
    """
    teams = []
    for c in columns:
        teams.append(df[c])
    teams = np.concatenate(teams)
    return np.unique(teams)


def league(files, delimiter=";"):
    """
    Load a league from a file or a list of files. Setups the teams classes,
    the schedule, the table and the missing games.

    Input can be:
    - One file with the schedule and results of the games played so far
    - Two files, one with the schedule and one with the table

    :param files: File or list of files
    :param delimiter: Delimiter of the files
    :return: teams, schedule, table, missing_games
    """

    # only schedule is given
    if len(files) == 1 or isinstance(files, str):
        schedule_and_results = pd.read_csv(
            files, delimiter=delimiter, encoding="unicode_escape"
        )
        schedule = schedule_and_results[["Home", "Away"]].copy()
        teams = get_teams_from_df(schedule_and_results)
        table, missing_games = create_table(schedule_and_results, teams)

    # schedule and table are given
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
        raise ValueError("files must be a list with one or two files or a str")

    # create the team classes
    teams_dict = {}
    for t in teams:
        teams_dict[t] = team.Team(
            name=t,
            GoalsF=table[table["Team"] == t]["GF"].values[0],
            GoalsA=table[table["Team"] == t]["GA"].values[0],
            played=table[table["Team"] == t]["Played"].values[0],
            penalty_scoring=0.75,
        )
    return teams_dict, schedule, table, missing_games


def tournament(filename, path="", delimiter=";"):
    """
    Load the tournament plan from file and setup team classes. Assuming your filename is
    `tournament_`, you should have the following files in your path:

    * `tournament_mode.CSV` to describe the mode of the tournament
    * `tournament_teams.CSV` to describe the teams playing
    * `tournament_{n}.CSV` with n ranging from 2 to 2**x, where x is the number of rounds
      played in the tournament. The files contain the schedule of the games played in
      the knockout round.
    * `tournament_special_rule.CSV` if there is a special rule for the tournament (e.g.
      some of the best third placed teams qualify for the next round)

    :param filename: Name of the file
    :param path: Path to the file
    :param delimiter: Delimiter of the file
    :return: teams, schedule, table, missing_games
    """

    # read out the mode files
    mode = (
        pd.read_csv(
            os.path.join(path, filename + "mode.CSV"),
            header=None,
            index_col=0,
            delimiter=delimiter,
        )
        .squeeze()
        .to_dict()
    )
    if mode["Group Stage"] == "True":
        group_stage = True
    elif mode["Group Stage"] == "False":
        group_stage = False
    else:
        raise ValueError(
            "Group Stage must be defined as True or False in your mode file"
        )

    # read out all the knockout round files
    ko = int(mode["First knockout round"])
    ko_round = []
    while ko > 1:
        ko_round.append(
            pd.read_csv(
                os.path.join(path, filename + "{}.CSV".format(ko)), delimiter=delimiter
            )
        )
        ko = int(ko / 2)

    # check if there is a special rule file for the knockout round
    try:
        if int(mode["number of additional teams qualified"]) > 0:
            ko_round.append(
                pd.read_csv(
                    os.path.join(path, filename + "special_rule.CSV"),
                    delimiter=delimiter,
                )
            )
    except Exception:
        pass

    # build the team table
    team_table = pd.read_csv(
        os.path.join(path, filename + "teams.CSV"), delimiter=delimiter
    )
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

    # building team classes
    for name in team_table["Name"].values:
        # check if there is penalty information, otherwise set to default 0.75
        try:
            penalty = team_table[team_table["Name"] == name]["Penalty Scoring"].values[
                0
            ]
        except Exception:
            penalty = 0.75
        teams[name] = team.Team(
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


def create_table(sched_n_r, teams):
    """
    Create the table from the schedule and results

    :param sched_n_r: Schedule and results
    :param teams: List of teams
    :return: Table, missing games
    """
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
            table.loc[game["Home"].values[0], "Played"] += 1
            table.loc[game["Away"].values[0], "Played"] += 1
            table.loc[game["Home"].values[0], "GF"] += game["Goals Home"].values[0]
            table.loc[game["Away"].values[0], "GF"] += game["Goals Away"].values[0]
            table.loc[game["Home"].values[0], "GA"] += game["Goals Away"].values[0]
            table.loc[game["Away"].values[0], "GA"] += game["Goals Home"].values[0]
            table.loc[game["Home"].values[0], "GD"] += (
                game["Goals Home"].values[0] - game["Goals Away"].values[0]
            )
            table.loc[game["Away"].values[0], "GD"] += (
                game["Goals Away"].values[0] - game["Goals Home"].values[0]
            )
            if game["Goals Home"].values[0] > game["Goals Away"].values[0]:
                table.loc[game["Home"].values[0], "Points"] += 3
            if game["Goals Home"].values[0] < game["Goals Away"].values[0]:
                table.loc[game["Away"].values[0], "Points"] += 3
            if game["Goals Home"].values[0] == game["Goals Away"].values[0]:
                table.loc[game["Home"].values[0], "Points"] += 1
                table.loc[game["Away"].values[0], "Points"] += 1
            """
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
            """
            table["GD"] = table["GF"] - table["GA"]
    sorted_table = tiebreaker(table, rule="Goal Difference")
    sorted_table.index = np.arange(1, len(teams) + 1)
    return sorted_table, missing_games


def tiebreaker(table, rule="Goal Difference"):
    """
    Sort the table according to the tiebreaker rule

    :param table: Table to be sorted
    :param rule: Tiebreaker rule
    :return: Sorted table
    """
    if rule == "Goal Difference":
        return table.sort_values(["Points", "GD", "GF"], ascending=False)
    else:
        raise NotImplementedError(f"Tiebreaker rule {rule} not implemented")


def get_missing_games(table, schedule):
    """
    Get the missing games from the schedule

    :param table: Table
    :param schedule: Schedule
    :return: Boolean array with missing games
    """
    index = np.zeros_like(schedule["Home"].values, dtype=bool)
    teams = get_teams_from_df(schedule, ["Home", "Away"])
    for t in teams:
        played = table[table["Team"] == t]["Played"].values[0]
        t_schedule = schedule[
            np.logical_or(schedule["Home"] == t, schedule["Away"] == t)
        ].index
        index[t_schedule[played:]] = True
    return index
