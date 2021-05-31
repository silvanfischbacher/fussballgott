import matplotlib, matplotlib.pyplot as plt , seaborn as sns

def league(sim):
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","green"])
    plt.figure(figsize=(11,10))
    sns.heatmap(sim,cmap=cmap,vmin=0,vmax=1,annot=True,fmt='.3',)
