# Copyright (C) 2021 Silvan Fischbacher

import numpy as np
import pandas as pd
from tqdm.auto import trange

from fussballgott import fussball, league


def simulate(
    mode,
    ko_round,
    teams,
    groups=None,
    n_sim=1,
    include_goals_against=True,
    sorting="standard",
    small_final=False,
    progressbar=True,
):
    """
    Simulate a tournament with given teams and schedule.

    :param mode: Dictionary with the mode of the tournament
    :param ko_round: List of pandas DataFrames with the knockout rounds
    :param teams: Dictionary with teams as keys and team objects as values
    :param groups: Dictionary with groups as keys and teams as values
    :param n_sim: Number of simulations
    :param include_goals_against: If True, the average goals against are included
    :param sorting: Sorting of the table
    :param small_final: If True, the tournament ends has a small final
    :param progressbar: If True, a progressbar is shown
    :return: simlated tournament table
    """
    n_sim = int(n_sim)

    if mode["Group Stage"] == "True":
        group_stage = True
    elif mode["Group Stage"] == "False":
        group_stage = False
    else:
        raise ValueError("Group Stage must be defined as True or False")

    first_ko = int(mode["First knockout round"])
    if group_stage:
        games = int(mode["Games against each opponent in group stage"])
        n_dir_qual = int(mode["number of teams qualified per group"])
        n_add = int(mode["number of additional teams qualified"])

        dict_group = {}
        for g in groups.keys():
            for t in groups[g]:
                dict_group[t] = g

    n_of_rounds = int(np.log2(first_ko)) + 3 + small_final * 1
    result_table = np.zeros((len(teams), n_of_rounds))

    if small_final:
        ocol = np.array(
            ["1/64", "1/32", "1/16", "1/8", "QF", "4th", "3rd", "2nd", "1st"]
        )
    else:
        ocol = np.array(["1/64", "1/32", "1/16", "1/8", "QF", "SF", "2nd", "1st"])

    output_col = np.zeros(n_of_rounds, dtype="<U32")
    output_col[0] = "Group Stage"
    output_col[1:] = ocol[-(n_of_rounds - 1) :]

    team_list = teams.keys()
    dict_res = {}
    for i, t in enumerate(team_list):
        dict_res[t] = i
        dict_res[i] = t

    for i_sim in trange(n_sim, disable=not progressbar):
        if group_stage:
            ###############
            # GROUP STAGE #
            ###############
            final_round = 0
            rounds_left = n_of_rounds

            if n_add > 0:
                best_third = {}
            group_index = groups.keys()
            dict_ko = {}
            for g in group_index:
                team_g = {}
                for t in groups[g]:
                    team_g[t] = teams[t]
                tab, dict_num2team = league.simulate(
                    team_g,
                    schedule=games,
                    n_sim=1,
                    include_goals_against=include_goals_against,
                    sorting=sorting,
                    progressbar=False,
                    tournament_mode=True,
                )
                for i in range(len(groups[g])):
                    if i < n_dir_qual:
                        dict_ko["{}{}".format(i + 1, g)] = dict_num2team[tab[i, -1]]
                    else:
                        result_table[
                            dict_res[dict_num2team[tab[i, -1]]], final_round
                        ] += 1
                if n_add > 0:
                    best_third[dict_num2team[tab[n_dir_qual, -1]]] = tab[n_dir_qual, :]

            ###################
            # FIND BEST THIRD #
            ###################
            if n_add > 0:
                d_3 = {}
                t_3 = np.empty((len(best_third), 5))
                for i, t in enumerate(best_third.keys()):
                    d_3[t] = i
                    d_3[i] = t
                    t_3[i, :] = best_third[t]
                    t_3[i, -1] = i
                sorted_table, ranking = fussball.sort(t_3, "standard")
                group = ""
                for i in range(n_add):
                    q_team = d_3[ranking[i]]
                    result_table[dict_res[q_team], final_round] -= 1
                    group += dict_group[q_team]
                combination = "".join(sorted(group))
                special_rule = ko_round[-1][
                    (ko_round[-1]["Combinations"] == combination)
                ]
                for t in best_third:
                    if dict_group[t] in sorted(group):
                        for c in special_rule.columns:
                            if special_rule[c].values[0] == dict_group[t]:
                                dict_ko[c] = t
        else:
            dict_ko = {}
            for t in team_list:
                dict_ko[t] = t
            final_round = 0
            rounds_left = n_of_rounds
        rounds_left -= 1
        ###################
        # KNOCK-OUT-PHASE #
        ###################
        minimal_round = 2 + small_final * 2
        while rounds_left > minimal_round:
            sch = ko_round[final_round]
            final_round += 1
            dict_current_round = {}
            for game in sch.index:
                team1 = dict_ko[sch.loc[game]["Home"]]
                team2 = dict_ko[sch.loc[game]["Away"]]
                h, a = fussball.simulate_game(
                    teams[team1].AvGoalsF,
                    teams[team2].AvGoalsF,
                    teams[team1].AvGoalsA,
                    teams[team2].AvGoalsA,
                    include_goals_against=include_goals_against,
                    extra_time=True,
                    penalty_scoring1=teams[team1].penalty_scoring,
                    penalty_scoring2=teams[team2].penalty_scoring,
                )
                if h > a:
                    dict_current_round[sch.loc[game]["Game"]] = team1
                    result_table[dict_res[team2], final_round] += 1
                else:
                    dict_current_round[sch.loc[game]["Game"]] = team2
                    result_table[dict_res[team1], final_round] += 1
            rounds_left -= 1
            dict_ko = dict_current_round

        ##########
        # FINALS #
        ##########

        if small_final:
            # SEMIFINAL #
            sch = ko_round[final_round]
            final_round += 1
            dict_final = {}
            dict_small_final = {}
            for game in sch.index:
                team1 = dict_ko[sch.loc[game]["Home"]]
                team2 = dict_ko[sch.loc[game]["Away"]]
                h, a = fussball.simulate_game(
                    teams[team1].AvGoalsF,
                    teams[team2].AvGoalsF,
                    teams[team1].AvGoalsA,
                    teams[team2].AvGoalsA,
                    include_goals_against=include_goals_against,
                    extra_time=True,
                    penalty_scoring1=teams[team1].penalty_scoring,
                    penalty_scoring2=teams[team2].penalty_scoring,
                )
                if h > a:
                    dict_final[sch.loc[game]["Game"]] = team1
                    dict_small_final[sch.loc[game]["Game"]] = team2
                else:
                    dict_final[sch.loc[game]["Game"]] = team2
                    dict_small_final[sch.loc[game]["Game"]] = team1

            # SMALL FINAL #
            team1 = dict_small_final[1]
            team2 = dict_small_final[2]
            h, a = fussball.simulate_game(
                teams[team1].AvGoalsF,
                teams[team2].AvGoalsF,
                teams[team1].AvGoalsA,
                teams[team2].AvGoalsA,
                include_goals_against=include_goals_against,
                extra_time=True,
                penalty_scoring1=teams[team1].penalty_scoring,
                penalty_scoring2=teams[team2].penalty_scoring,
            )
            if h > a:
                result_table[dict_res[team1], final_round + 1] += 1
                result_table[dict_res[team2], final_round] += 1
            else:
                result_table[dict_res[team1], final_round] += 1
                result_table[dict_res[team2], final_round + 1] += 1

            # FINAL #
            final_round += 2
            team1 = dict_final[1]
            team2 = dict_final[2]
            h, a = fussball.simulate_game(
                teams[team1].AvGoalsF,
                teams[team2].AvGoalsF,
                teams[team1].AvGoalsA,
                teams[team2].AvGoalsA,
                include_goals_against=include_goals_against,
                extra_time=True,
                penalty_scoring1=teams[team1].penalty_scoring,
                penalty_scoring2=teams[team2].penalty_scoring,
            )
            if h > a:
                result_table[dict_res[team1], final_round + 1] += 1
                result_table[dict_res[team2], final_round] += 1
            else:
                result_table[dict_res[team1], final_round] += 1
                result_table[dict_res[team2], final_round + 1] += 1
        else:
            # FINAL #
            final_round += 1
            team1 = dict_ko[1]
            team2 = dict_ko[2]
            h, a = fussball.simulate_game(
                teams[team1].AvGoalsF,
                teams[team2].AvGoalsF,
                teams[team1].AvGoalsA,
                teams[team2].AvGoalsA,
                include_goals_against=include_goals_against,
                extra_time=True,
                penalty_scoring1=teams[team1].penalty_scoring,
                penalty_scoring2=teams[team2].penalty_scoring,
            )
            if h > a:
                result_table[dict_res[team1], final_round + 1] += 1
                result_table[dict_res[team2], final_round] += 1
            else:
                result_table[dict_res[team1], final_round] += 1
                result_table[dict_res[team2], final_round + 1] += 1
    if not group_stage:
        return pd.DataFrame(
            index=teams.keys(), columns=output_col, data=result_table / n_sim
        ).drop(columns="Group Stage")
    else:
        return pd.DataFrame(
            index=teams.keys(), columns=output_col, data=result_table / n_sim
        )
