# Copyright (C) 2021 Silvan Fischbacher

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


def league(sim):
    """
    Plot the league table in a heatmap.

    :param sim: DataFrame with the simulation results
    """

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "green"])
    plt.figure(figsize=(11, 10))
    ax = sns.heatmap(
        sim,
        cmap=cmap,
        vmin=0,
        vmax=1,
        annot=True,
        fmt=".3",
    )
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(length=0)


def tournament(sim, sort_for=None, save=None, prob_style="standard"):
    """
    Plot the tournament table in a heatmap.

    :param sim: DataFrame with the simulation results
    :param sort_for: Column to sort for
    :param save: Path to save the plot
    :param prob_style: "standard" or "cumulative"
    """
    if prob_style == "standard":
        sim = sim
    elif prob_style == "cumulative":
        sim = sim.iloc[:, ::-1].cumsum(axis=1).iloc[:, ::-1]
    else:
        raise ValueError(
            'prob_style {} is not implemented, use "standard" or'
            ' "cumulative"'.format(prob_style)
        )

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "green"])
    plt.figure(figsize=(11, 10))
    if sort_for is None:
        ax = sns.heatmap(sim, cmap=cmap, vmin=0, vmax=1, annot=True, fmt=".2")
    else:
        ax = sns.heatmap(
            sim.sort_values(by=sort_for, ascending=False),
            cmap=cmap,
            vmin=0,
            vmax=1,
            annot=True,
            fmt=".2",
        )
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.tick_params(length=0)
    plt.yticks(rotation=0)
    if save is not None:
        plt.savefig(save)


def game_stat(sim, winprob=None, team1="home", team2="away"):
    """
    Plot the game statistics in a heatmap.

    :param sim: DataFrame with the simulation results
    :param winprob: Array with the win probabilities
    :param team1: Name of the first team
    :param team2: Name of the second team
    """

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "green"])
    plt.figure(figsize=(11, 10))
    ax = sns.heatmap(
        sim,
        cmap=cmap,
        annot=True,
        fmt=".3",
    )
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    plt.xlabel(team2)
    plt.ylabel(team1)
    ax.tick_params(length=0)

    if winprob is not None:
        plt.figure()
        plt.bar(x=["1", "X", "2"], height=winprob)
