import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set_theme(color_codes=True)
sns.set(rc={'figure.figsize':(9,9)},font_scale=1.5)


def plot_scatter_Cluster_dis(x_var,y_var,df):
    marker_style = {'Normal':'o','COPD':'s','IPF':'d','Asthma':'^'}
    fig, ax = plt.subplots()
    sns.scatterplot(x=x_var,y=y_var,data=df,ax=ax,
    hue='Cluster',palette="deep",style='dis',markers=marker_style,s=70)
    return ax
def plot_reg(x_var, y_var,df,ax):
    sns.regplot(x=x_var,y=y_var,color='k',data=df,scatter=False,ax=ax)
    return ax

def main():
    df_path = str(sys.argv[1])
    var1 = str(sys.argv[2])
    var2 = str(sys.argv[3])

    save_path = f'{df_path[:-5]}_{var1}_{var2}.png'
    df_corr = pd.read_excel(df_path,sheet_name='corr',index_col=0)
    df_p = pd.read_excel(df_path,sheet_name='p-value',index_col=0)
    df = pd.read_excel(df_path,sheet_name='data',index_col=0)

    corr = df_corr.loc[var1,var2]
    p = df_p.loc[var1,var2]

    ax = plot_scatter_Cluster_dis(var1,var2,df)
    ax = plot_reg(var1, var2, df, ax)
    plt.savefig(save_path)
    print(f"p-value: {p}")
    print(f"correlation coefficient: {corr}")
    print("--------------------------------")
    print("Figure is saved as: ")
    print(save_path)


if __name__ == "__main__":
    main()
