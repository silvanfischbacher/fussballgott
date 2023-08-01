# FUSSBALLGOTT

![example workflow](https://github.com/silvanfischbacher/fussballgott/actions/workflows/ci.yml/badge.svg)

                         ___
     o__        o__     |   |\
    /|          /\      |   |X\
    / > o        <\     |   |XX\

This repository provides all important functions to simulate football games, leagues or tournaments.

# Usage

## Single games

You find an example notebook at `demos/single_games/demo_single_games.ipynb`

1. Import the fussballgott package

`import fussballgott`

2. To simulate one game, you need the following information of both teams:

* Average Goals for the team per game: `AvGoalsF1, AvGoalsF2`

* Average Goals against the team (optional, default=1): `AvGoalsA1, AvGoalsA2`

* Should goals against the team be included in the simulation? (optional, default=False): `include_goals_against`

* Will there be extra time and penalty shootout in case of a draw? (optional, default=False): `extra_time`

* What is the chance of the team to score in a penalty (for penalty_shootout)? (optional, default=0.75): `penalty_scoring1, penalty_scoring2`

* Should the function return when the game was over (only relevant for extra time)? (optional, default=False): `return when`

Then, you can run the simulation by

`home, away = fussballgott.fussball.simulate_game(AvGoalsF1, AvGoalsF2, ...)`

and you get the result of the simulated game home:away. If you set `return_when = True`, you will get

`home, away, when, home90, away90 = fussballgott.fussball.simulate_game(AvGoalsF1, AvGoalsF2, ...)`

with `home90:away90` the result after 90 minutes and `home:away` after extra_time or penalty_shootout. The parameter `when` tells you when the game was decided: `reg` for regular time, `AET` after extra time, `PSO` after penalty shootout.

If you want have a statistic of the game, you can use

`stat, win_prob = fussballgott.fussball.simulate_games_stats(AvGoalsF1, AvGoalsF2, ..., n_sim = 1e5)`

This runs the simulation `n_sim` times and returns the probability of each result as well as the winning probability of each team.

## Leagues

You find an example notebook at `demos/league/demo_leagues.ipynb`

There are three ways of simulating a league:

1. Full simulation: Most convenient for simulation at the beginning of a season. For doing that, you have to initialize the team strengths first by creating a dictionary where you create for each team a teamclass object:

```
teams = {}
teams['GCZ'] = team.team(name='GCZ', GoalsF=3.1, GoalsA=0.9)
teams['YB'] = team.team(name='YB', GoalsF=2.3, GoalsA=1.7)
teams['FCB'] = team.team(name='FCB', GoalsF=2, GoalsA=3.2)
teams['FCZ'] = team.team(name='FCZ', GoalsF=1, GoalsA=4.3)
```

Then you can run the simulation using

`fussballgott.league.simulate(teams, schedule = 4, n_sim = 1e5)`

where `schedule` determines how many times each team play against the other teams.

2. Simulation from schedule: Most convenient for simulation that you repeat every week after games are played. For that, you have to create a CSV file with the full schedule and the results of the games played so far. You can load this by

`teams, schedule, table, missing_games = fussballgott.load.league('file.CSV')`

This initializes the teams dictionary, loads the schedule, current table and an array for the missing games. The simulation is then done by using

`sim = fussballgott.league.simulate(teams, schedule, table, missing_games, n_sim = 1e5)`

And you can plot the result using `plot.league(sim)`. You can find an example CSV-file at `demos/league/demo_league.CSV`.

3. Simulation from schedule and current table: Most convenient for simulation of an ongoing season that won't be repeated weekly. For that, you have to create two CSV file: One with the full schedule and one with the current table. You can load this by

`teams, schedule, table, missing_games = fussballgott.load.league(['schedule.CSV', 'table.CSV'])`

This initializes the teams dictionary, loads the schedule, current table and an array for the missing games (assuming the games took place from the top of the schedule in order). The simulation is then done by using

`sim = fussballgott.league.simulate(teams, schedule, table, missing_games, n_sim = 1e5)`

And you can plot the result using `plot.league(sim)`. You can find example CSV-files at `demos/league/demo_league_sep_schedule.CSV` and `demos/league/demo_league_sep_table.CSV`.

## Tournaments

You find an example notebook at `demos/tournament/demo_tournament.ipynb` that uses the European Championship in 2021.

1. To simulate tournaments like the World Cup or the European Championship, you have to set up a few CSV files to describe the match plan. Examples of such files can be found at `demos/tournament/`. The files should all be in the same folder and start with the same name, in the demo case `demo_tournament_`. The endings of the files have to match the following description. Ideally, you use the demo_tournament files and insert new numbers. You need

* `mode.CSV`: This file contains general information about the mode of the tournament, like first knockout round (Eighty Finals=8, Quarter Finals=4, etc.), the amount of games against each opponent in group stage (typically 1), the number of teams that are qualified per group (typically 2), number of additional teams that are qualified due to a special rule (typically 0 for World Cups, 4 for European Championship where the 4 best 3rd of each group still qualify) and the path where the game plan distribution for this additionally qualified teams would be found if necessarry.

* `teams.CSV`: Defining all teams, the group they belong to and the Goals that they have scored and received (e.g. in the qualifiers) and the number of games that they've played. To directly plug in the number of goals per match, set Played to 1. Optionally, you can also adjust penalty scoring strenght in this file.

* `2.CSV`, `4.CSV`, etc. : Defining which team plays against which team in the knockout rounds. In the first knockout round, the name of the team is given by the rank followed by the group. So the 1st of group A would be `1A`. For later rounds, the game number of the previous round is sufficient.

* `special_rule.CSV`: Defining allocation of additionally qualified teams to the first knockout round.

2. Load all the CSV files by

`mode, ko_round, teams, groups = fussballgott.load.tournament('demo_tournament_')`

where `demo_tournament_` is the prefix of all your CSV files. Let the simulation run by

`sim = tournament.simulate(mode, ko_round, teams, groups, n_sim = 1e4)`

The simulation will take much longer than a league simulation due to the complexity of the schedule. Finally, you can plot the result with

`fussballgott.plot.tournament(sim)`
