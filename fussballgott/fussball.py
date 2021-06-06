import numpy as np
from tqdm import trange

def simulate_game_wo_overtime(AvGoalsF1, AvGoalsF2, AvGoalsA1=1, AvGoalsA2=1,
                              include_goals_against=False, multiplier = 1):
    if include_goals_against:
        home = np.random.poisson(multiplier*(AvGoalsF1+AvGoalsA2)/2)
        away = np.random.poisson(multiplier*(AvGoalsF2+AvGoalsA1)/2)
    else:
        home = np.random.poisson(multiplier*AvGoalsF1)
        away = np.random.poisson(multiplier*AvGoalsF2)
    return home, away

def penalty_shootout(penalty_scoring1, penalty_scoring2):
    home = sum(np.random.rand(5)<penalty_scoring1)
    away = sum(np.random.rand(5)<penalty_scoring2)
    while home==away:
        home += sum(np.random.rand(1)<penalty_scoring1)
        away += sum(np.random.rand(1)<penalty_scoring2)
    return home, away

def simulate_game(AvGoalsF1, AvGoalsF2, AvGoalsA1=1, AvGoalsA2=1,
                  include_goals_against=False, extra_time = False,
                  penalty_scoring1 = 0.75, penalty_scoring2= 0.75,
                  return_when = False):
    home, away = simulate_game_wo_overtime(AvGoalsF1, AvGoalsF2, AvGoalsA1, AvGoalsA2, include_goals_against)
    home_r = home
    away_r = away
    when = 'reg'
    if (extra_time and (home==away)):
        home_o, away_o = simulate_game_wo_overtime(AvGoalsF1, AvGoalsF2, AvGoalsA1, AvGoalsA2,
                                                   include_goals_against, multiplier = 1/3)
        home_r += home_o
        away_r += away_o
        when = 'AET'
        if home_o==away_o:
            home_p, away_p = penalty_shootout(penalty_scoring1, penalty_scoring2)
            home_r += home_p
            away_r += away_p
            when = 'PSO'
    if return_when:
        return home_r, away_r, when, home, away
    else:
        return home_r, away_r

def who_won(home, away):
    if home>away:
        return 0
    elif home==away:
        return 1
    else:
        return 2

def simulate_game_stats(AvGoalsF1, AvGoalsF2, AvGoalsA1, AvGoalsA2, n_sim = 1e5,
                        include_goals_against=False, extra_time = False,
                        penalty_scoring1 = 0.75, penalty_scoring2= 0.75):
    n_sim = int(n_sim)
    table = np.zeros( (11,11) )
    win_prob = np.zeros(3)
    for i in trange(n_sim):
        home120, away120, when, home, away = simulate_game(AvGoalsF1, AvGoalsF2, AvGoalsA1, AvGoalsA2,
                                                           include_goals_against, extra_time,
                                                           penalty_scoring1, penalty_scoring2,
                                                           return_when = True)
        win_prob[who_won(home120,away120)] += 1
        table[min(home,10), min(away,10)] += 1

    return table/n_sim, win_prob/n_sim

def sort(table, sorting='standard'):
    if sorting == 'standard':
        table = table[table[:, 1].argsort()] #sort GF
        table = table[(table[:, 1]-table[:,2]).argsort(kind='mergesort')] #sort GD
        table = table[table[:, 3].argsort(kind='mergesort')] #sort points
        table = np.flip(table, axis=0)
        ranking = table[:,-1]
    return table, ranking
