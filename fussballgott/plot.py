import matplotlib, matplotlib.pyplot as plt , seaborn as sns

def league(sim):
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","green"])
    plt.figure(figsize=(11,10))
    ax = sns.heatmap(sim,cmap=cmap,vmin=0,vmax=1,annot=True,fmt='.3',)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.tick_params(length=0)

def tournament(sim):
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","green"])
    plt.figure(figsize=(11,10))
    ax = sns.heatmap(sim,cmap=cmap,vmin=0,vmax=1,annot=True,fmt='.2')
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.tick_params(length=0)

def game_stat(sim, winprob, team1='home', team2='away'):
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","green"])
    plt.figure(figsize=(11,10))
    ax = sns.heatmap(sim,cmap=cmap,annot=True,fmt='.3',)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    plt.xlabel(team2)
    plt.ylabel(team1)
    ax.tick_params(length=0)

    plt.figure()
    plt.bar(x=['1','X','2'],height=winprob)
