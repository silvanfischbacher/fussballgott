# Copyright (C) 2024 Silvan Fischbacher

import numpy as np

from fussballgott import plot


class BettingFunction:
    """
    Class to define a general function to return points for a bet given a true result.
    """

    def __init__(self, betting_function):
        if callable(betting_function):
            self.betting_function = betting_function
        elif betting_function == "ETH":
            self.betting_function = bet_func_ETH
        elif betting_function == "SRF":
            self.betting_function = bet_func_SRF
        elif betting_function == "kt":
            self.betting_function = bet_func_kt
        else:
            raise ValueError("Invalid betting function")

    def __call__(self, bet1x2, goal_difference, total_result, n_goal, draw):
        """
        Returns the number of points given for such a bet

        :param bet1x2: 1 if the choice of 1, X or 2 is correct, 0 otherwise
        :param goal_difference: 1 if the goal difference is correct, 0 otherwise
        :param total_result: 1 if the total result is correct, 0 otherwise
        :param n_goal: 2 if the number of goals is correct for both teams, 1 if correct for one, 0 otherwise
        :param draw: True if the game was a draw and the bet was also a draw, False otherwise
        :return: number of points of this betting function
        """
        return self.betting_function(
            bet1x2, goal_difference, total_result, n_goal, draw
        )


def bet_func_ETH(bet1x2, GD, total_result, n_goal, draw):
    if total_result == 1:
        return 4
    else:
        return bet1x2 * 2 + GD


def bet_func_SRF(bet1x2, GD, total_result, n_goal, draw):
    return bet1x2 * 5 + n_goal + 3 * GD


def bet_func_kt(bet1x2, GD, total_result, n_goal, draw):
    if draw:
        return bet1x2 * 2 + total_result * 2
    else:
        return bet1x2 * 2 + GD + total_result


def points(bet, result, bet_func):
    bet_fct = BettingFunction(bet_func)
    bet1x2 = 0
    GD = 0
    total_result = 0
    n_goal = 0
    draw = False

    if bet[0] > bet[1] and result[0] > result[1]:
        bet1x2 = 1
    if bet[0] == bet[1] and result[0] == result[1]:
        bet1x2 = 1
        draw = True
    if bet[0] < bet[1] and result[0] < result[1]:
        bet1x2 = 1

    if bet[0] - bet[1] == result[0] - result[1]:
        GD = 1

    if bet[0] == result[0] and bet[1] == result[1]:
        total_result = 1

    if bet[0] == result[0]:
        n_goal += 1
    if bet[1] == result[1]:
        n_goal += 1

    return bet_fct(bet1x2, GD, total_result, n_goal, draw)


def expvalue(bet, prob, bet_func, max_goals=10):
    expvalue = 0
    for i in range(max_goals):
        for j in range(max_goals):
            expvalue += prob[i, j] * points(bet, (i, j), bet_func)
    return expvalue


def get_expvalue(sim, bet_func):
    max_h, max_a = np.shape(sim)
    expectation_value = np.zeros_like(sim)
    for h in range(max_h):
        for a in range(max_a):
            expectation_value[h, a] = expvalue((h, a), sim, bet_func)
    plot.game_stat(expectation_value)
    return expectation_value
