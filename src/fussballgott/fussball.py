# Copyright (C) 2021 Silvan Fischbacher

import numpy as np
from tqdm.auto import trange


def simulate_game_wo_overtime(
    AvGoalsF1,
    AvGoalsF2,
    AvGoalsA1=1,
    AvGoalsA2=1,
    include_goals_against=False,
    multiplier=1,
):
    """
    Simulate a game between two teams with given average goals for and against in
    90 minutes.

    :param AvGoalsF1: Average goals for team 1
    :param AvGoalsF2: Average goals for team 2
    :param AvGoalsA1: Average goals against team 1
    :param AvGoalsA2: Average goals against team 2
    :param include_goals_against: If True, the average goals against are included
    :param multiplier: Multiplier for the average goals, e.g. 1/3 for overtime
    :return: home goals, away goals
    """
    if include_goals_against:
        home = np.random.poisson(multiplier * (AvGoalsF1 + AvGoalsA2) / 2)
        away = np.random.poisson(multiplier * (AvGoalsF2 + AvGoalsA1) / 2)
    else:
        home = np.random.poisson(multiplier * AvGoalsF1)
        away = np.random.poisson(multiplier * AvGoalsF2)
    return home, away


def penalty_shootout(penalty_scoring1, penalty_scoring2):
    """
    Simulate a penalty shootout between two teams with given penalty scoring.

    :param penalty_scoring1: Penalty scoring of team 1 (between 0 and 1)
    :param penalty_scoring2: Penalty scoring of team 2 (between 0 and 1)
    :return: home goals, away goals
    """

    home = sum(np.random.rand(5) < penalty_scoring1)
    away = sum(np.random.rand(5) < penalty_scoring2)
    while home == away:
        home += sum(np.random.rand(1) < penalty_scoring1)
        away += sum(np.random.rand(1) < penalty_scoring2)
    return home, away


def simulate_game_from_teams(
    team1,
    team2,
    include_goals_against=False,
    extra_time=False,
    return_when=False,
):
    """
    Simulate a game between two teams (with given team classes)

    :param team1: team class of team 1
    :param team2: team class of team 2
    :param include_goals_against: If True, the average goals against are included
    :param extra_time: If True, extra time and penalty shootout are included
    :param return_when: If True, the result is returned together with the time when
        the game was decided and the result before overtime
    :return: home goals, away goals
    :return: when, home goals and away goals after 90 minutes (if return_when=True)
    """
    return simulate_game(
        AvGoalsF1=team1.AvGoalsF,
        AvGoalsF2=team2.AvGoalsF,
        AvGoalsA1=team1.AvGoalsA,
        AvGoalsA2=team2.AvGoalsA,
        include_goals_against=include_goals_against,
        extra_time=extra_time,
        penalty_scoring1=team1.penalty_scoring,
        penalty_scoring2=team2.penalty_scoring,
        return_when=return_when,
    )


def simulate_game_stats_from_teams(
    team1,
    team2,
    include_goals_against=False,
    extra_time=False,
    n_sim=1e5,
):
    """
    Simulate the statistics of a game between two teams.

    :param team1: team class of team 1
    :param team2: team class of team 2
    :param include_goals_against: If True, the average goals against are included
    :param extra_time: If True, extra time and penalty shootout are included
    :param n_sim: Number of simulations
    :return: home goals, away goals
    """
    return simulate_game_stats(
        AvGoalsF1=team1.AvGoalsF,
        AvGoalsF2=team2.AvGoalsF,
        AvGoalsA1=team1.AvGoalsA,
        AvGoalsA2=team2.AvGoalsA,
        include_goals_against=include_goals_against,
        extra_time=extra_time,
        penalty_scoring1=team1.penalty_scoring,
        penalty_scoring2=team2.penalty_scoring,
        n_sim=n_sim,
    )


def simulate_game(
    AvGoalsF1,
    AvGoalsF2,
    AvGoalsA1=1,
    AvGoalsA2=1,
    include_goals_against=False,
    extra_time=False,
    penalty_scoring1=0.75,
    penalty_scoring2=0.75,
    return_when=False,
):
    """
    Simulate a game between two teams with given average goals for and against.

    :param AvGoalsF1: Average goals for team 1
    :param AvGoalsF2: Average goals for team 2
    :param AvGoalsA1: Average goals against team 1
    :param AvGoalsA2: Average goals against team 2
    :param include_goals_against: If True, the average goals against are included
    :param extra_time: If True, extra time and penalty shootout are included
    :param penalty_scoring1: Penalty scoring of team 1 (between 0 and 1)
    :param penalty_scoring2: Penalty scoring of team 2 (between 0 and 1)
    :param return_when: If True, the result is returned together with the time when
        the game was decided and the result before overtime
    :return: home goals, away goals
    :return: when, home goals and away goals after 90 minutes (if return_when=True)
    """
    home, away = simulate_game_wo_overtime(
        AvGoalsF1, AvGoalsF2, AvGoalsA1, AvGoalsA2, include_goals_against
    )
    home_r = home
    away_r = away
    when = "reg"
    if extra_time and (home == away):
        home_o, away_o = simulate_game_wo_overtime(
            AvGoalsF1,
            AvGoalsF2,
            AvGoalsA1,
            AvGoalsA2,
            include_goals_against,
            multiplier=1 / 3,
        )
        home_r += home_o
        away_r += away_o
        when = "AET"
        if home_o == away_o:
            home_p, away_p = penalty_shootout(penalty_scoring1, penalty_scoring2)
            home_r += home_p
            away_r += away_p
            when = "PSO"
    if return_when:
        return home_r, away_r, when, home, away
    else:
        return home_r, away_r


def who_won(home, away):
    """
    Returns who won the game. 0 if home won, 1 if draw and 2 if away won.

    :param home: Home goals
    :param away: Away goals
    :return: 0 if home won, 1 if draw and 2 if away won
    """
    if home > away:
        return 0
    elif home == away:
        return 1
    else:
        return 2


def simulate_game_stats(
    AvGoalsF1,
    AvGoalsF2,
    AvGoalsA1,
    AvGoalsA2,
    n_sim=1e5,
    include_goals_against=False,
    extra_time=False,
    penalty_scoring1=0.75,
    penalty_scoring2=0.75,
):
    """
    Simulate the statistics of a game between two teams.

    :param AvGoalsF1: Average goals for team 1
    :param AvGoalsF2: Average goals for team 2
    :param AvGoalsA1: Average goals against team 1
    :param AvGoalsA2: Average goals against team 2
    :param n_sim: Number of simulations
    :param include_goals_against: If True, the average goals against are included
    :param extra_time: If True, extra time and penalty shootout are included
    :param penalty_scoring1: Penalty scoring of team 1 (between 0 and 1)
    :param penalty_scoring2: Penalty scoring of team 2 (between 0 and 1)
    :return: table of results, win probabilities
    """
    n_sim = int(n_sim)
    table = np.zeros((11, 11))
    win_prob = np.zeros(3)
    for i in trange(n_sim):
        home120, away120, when, home, away = simulate_game(
            AvGoalsF1,
            AvGoalsF2,
            AvGoalsA1,
            AvGoalsA2,
            include_goals_against,
            extra_time,
            penalty_scoring1,
            penalty_scoring2,
            return_when=True,
        )
        win_prob[who_won(home120, away120)] += 1
        table[min(home, 10), min(away, 10)] += 1

    return table / n_sim, win_prob / n_sim


def sort(table, sorting="standard"):
    """
    Sorts a table of results.

    :param table: Table of results
    :param sorting: Sorting method
    :return: Sorted table, ranking
    """

    if sorting == "standard":
        table = table[table[:, 1].argsort()]  # sort GF
        table = table[(table[:, 1] - table[:, 2]).argsort(kind="mergesort")]  # sort GD
        table = table[table[:, 3].argsort(kind="mergesort")]  # sort points
        table = np.flip(table, axis=0)
        ranking = table[:, -1]
    else:
        raise NotImplementedError("Only standard sorting implemented")
    return table, ranking
