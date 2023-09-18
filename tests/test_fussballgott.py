# Copyright (C) 2021 Silvan Fischbacher

import os

import pytest

from fussballgott import fussball, league, load, plot, team, tournament


def _get_abspath(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


def test_penalty_shootout():
    penalty_scoring1 = 0.5
    penalty_scoring2 = 0.5
    for _ in range(100):
        home, away = fussball.penalty_shootout(penalty_scoring1, penalty_scoring2)
        assert home != away


def test_simulate_game():
    AvGoalsF1 = 1.5
    AvGoalsF2 = 1.5
    AvGoalsA1 = 1.5
    AvGoalsA2 = 1.5
    for _ in range(100):
        home, away = fussball.simulate_game(
            AvGoalsF1,
            AvGoalsF2,
            AvGoalsA1,
            AvGoalsA2,
            include_goals_against=True,
            extra_time=False,
            return_when=False,
        )
        assert home >= 0
        assert away >= 0
        assert isinstance(home, int)
        assert isinstance(away, int)

    for _ in range(100):
        home, away, when, home90, away90 = fussball.simulate_game(
            AvGoalsF1,
            AvGoalsF2,
            AvGoalsA1,
            AvGoalsA2,
            include_goals_against=False,
            extra_time=True,
            return_when=True,
        )
        assert home != away
        assert isinstance(when, str)
        assert when in ["reg", "AET", "PSO"]
        if when == "reg":
            assert home90 != away90
        elif when == "AET":
            assert home90 == away90
        elif when == "PSO":
            assert home90 == away90


def test_simulate_game_stats():
    stat, winprob = fussball.simulate_game_stats(
        AvGoalsF1=10,
        AvGoalsF2=0.5,
        AvGoalsA1=0.5,
        AvGoalsA2=10,
        include_goals_against=True,
    )
    assert winprob[0] > winprob[2]
    plot.game_stat(stat, winprob)


def test_simulate_game_from_teams():
    team1 = team.Team(name="FCB", GoalsF=2.3, GoalsA=1.7)
    team2 = team.Team(name="FCZ", GoalsF=1, GoalsA=4.3)
    h, a = fussball.simulate_game_from_teams(team1, team2)
    assert h >= 0
    assert a >= 0


def test_simulate_game_stats_from_teams():
    team1 = team.Team(name="GCZ", GoalsF=10, GoalsA=1.7)
    team2 = team.Team(name="FCZ", GoalsF=1, GoalsA=4.3)
    stat, winprob = fussball.simulate_game_stats_from_teams(team1, team2)
    assert winprob[0] > winprob[2]


def test_simulate_league():
    teams = {}
    teams["GCZ"] = team.Team(name="GCZ", GoalsF=3.1, GoalsA=0.9)
    teams["YB"] = team.Team(name="FCB", GoalsF=2.3, GoalsA=1.7)
    teams["FCB"] = team.Team(name="FCB", GoalsF=2, GoalsA=3.2)
    teams["FCZ"] = team.Team(name="FCZ", GoalsF=1, GoalsA=4.3)

    sim = league.simulate(teams, schedule=4, n_sim=1e5)
    assert sim.index[0] == "GCZ"
    assert sim.index[-1] == "FCZ"

    sim = league.simulate(teams, schedule=5, n_sim=1e5)
    assert sim.index[0] == "GCZ"
    assert sim.index[-1] == "FCZ"

    plot.league(sim)


def test_simulate_league_from_schedule():
    file = _get_abspath("test_csv_files/demo_league.CSV")
    teams, schedule, table, missing_games = load.league(file)
    sim = league.simulate(teams, schedule, table, missing_games, n_sim=1e5)
    assert sim.index[0] == "GCZ"
    assert sim.index[1] == "YB"


def test_simulate_league_from_schedule2():
    file_sched = _get_abspath("test_csv_files/demo_league_sep_schedule.CSV")
    file_tab = _get_abspath("test_csv_files/demo_league_sep_table.CSV")
    teams, schedule, table, missing_games = load.league([file_sched, file_tab])
    sim = league.simulate(teams, schedule, table, missing_games, n_sim=1e5)
    assert sim.index[0] == "GCZ"
    assert sim.index[1] == "YB"


def test_simulate_tournament():
    mode, ko_round, teams, groups = load.tournament(
        "demo_tournament_", path=_get_abspath("test_csv_files/demo_group_stage")
    )
    sim = tournament.simulate(mode, ko_round, teams, groups, n_sim=1e4)
    assert sim["1st"]["England"] > 0.1
    assert sim["Group Stage"]["Hungary"] > 0.4
    plot.tournament(sim)
    plot.tournament(sim, prob_style="cumulative", sort_for="1st", save="test.png")
    with pytest.raises(ValueError):
        plot.tournament(sim, prob_style="funky")


def test_load_league():
    file = ["file1.csv", "file2.csv", "file3.csv"]
    with pytest.raises(ValueError):
        load.league(file)


def test_simulate_tournament_no_group_stage():
    mode, ko_round, teams = load.tournament(
        "demo_tournament_", path=_get_abspath("test_csv_files/demo_no_group_stage")
    )
    tournament.simulate(mode, ko_round, teams, n_sim=1e4, small_final=True)
    with pytest.raises(ValueError):
        load.tournament(
            "demo_tournament_", path=_get_abspath("test_csv_files/demo_error")
        )
    mode["Group Stage"] = "maybe"
    with pytest.raises(ValueError):
        tournament.simulate(mode, ko_round, teams, n_sim=1e4)


def test_tiebreaker_error():
    table = None
    with pytest.raises(NotImplementedError):
        load.tiebreaker(table, "who_has_better_haircut")


def test_sorting_error():
    table = None
    with pytest.raises(NotImplementedError):
        fussball.sort(table, "who_has_better_haircut")
