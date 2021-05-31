import numpy as np, pandas as pd, sys, os
from fussballgott import team

def get_teams_from_df(df, columns=['Home','Away']):
    teams = []
    for c in columns:
        teams.append(df[c])
    teams = np.concatenate(teams)
    return np.unique(teams)

def load(files, style='league', delimiter=';'):
    if style=='league':
        schedule_and_results = pd.read_csv(files, delimiter=delimiter, encoding= 'unicode_escape')
        schedule = schedule_and_results[['Home','Away']].copy()
        teams = get_teams_from_df(schedule_and_results)
        table, missing_games = create_table(schedule_and_results, teams)
    if style=='league_sep':
        schedule = pd.read_csv(files[0], delimiter=delimiter, encoding= 'unicode_escape')
        table = pd.read_csv(files[1], delimiter=delimiter, encoding= 'unicode_escape', index_col=0)
        teams = get_teams_from_df(table, ['Team'])
        missing_games = get_missing_games(table, schedule)
    teams_dict = {}
    for t in teams:
        teams_dict[t] = team.team(name = t, GoalsF = table[table['Team'] == t]['GF'].values[0],
                             GoalsA = table[table['Team'] == t]['GA'].values[0],
                             played = table[table['Team'] == t]['Played'].values[0],
                             penalty_scoring = 0.75)
    return teams_dict, schedule, table, missing_games

def enrich_table(table):
    if 'GD' not in table.index:
        table['GD'] = table['GF'] - table['GA']
    return table

def create_table(sched_n_r,teams):
    next_game=sched_n_r[sched_n_r['Goals Home'].isnull()].index[0]
    games=np.shape(sched_n_r)[0]
    missing_games = np.ones(games, dtype=bool)
    table=pd.DataFrame(index=teams)
    table['Team']=table.index
    table['Played']=0
    table['GF']=0
    table['GA']=0
    table['GD']=0
    table['Points']=0

    for i in range(games):
        game=sched_n_r[i:i+1]
        if game['Goals Home'].isnull().values[0]:
            pass
        else:
            missing_games[i]=False
            table['Played'][game['Home'].values[0]]+=1
            table['Played'][game['Away'].values[0]]+=1
            table['GF'][game['Home'].values[0]]+=game['Goals Home'].values[0]
            table['GF'][game['Away'].values[0]]+=game['Goals Away'].values[0]
            table['GA'][game['Home'].values[0]]+=game['Goals Away'].values[0]
            table['GA'][game['Away'].values[0]]+=game['Goals Home'].values[0]
            if game['Goals Home'].values[0]>game['Goals Away'].values[0]: table['Points'][game['Home'].values[0]]+=3
            if game['Goals Home'].values[0]<game['Goals Away'].values[0]: table['Points'][game['Away'].values[0]]+=3
            if game['Goals Home'].values[0]==game['Goals Away'].values[0]:
                table['Points'][game['Home'].values[0]]+=1
                table['Points'][game['Away'].values[0]]+=1
    table['GD']=table['GF']-table['GA']
    sorted_table = tiebreaker(table, rule='Goal Difference')
    sorted_table.index=np.arange(1,len(teams)+1)
    return sorted_table, missing_games

def tiebreaker(table, rule='Goal Difference'):
    if rule == 'Goal Difference':
        return table.sort_values(['Points','GD', 'GF'],ascending=False)
    else:
        print('Rule {} not implemented yet'.format(rule))

def get_missing_games(table, schedule):
    index = np.zeros_like(schedule['Home'].values, dtype=bool)
    teams = get_teams_from_df(schedule, ['Home', 'Away'])
    for t in teams:
        played = table[table['Team'] == t]['Played'].values[0]
        t_schedule = schedule[np.logical_or(schedule['Home']==t,schedule['Away']==t)].index
        index[t_schedule[played:]] = True
    return index
