import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set_theme(color_codes=True)
sns.set(rc={'figure.figsize':(9,9)},font_scale=1.5)
sns.set_style("white")

def plot_corr(df,p,corr,var1,var2,save_path):
    df_temp = df.loc[:,[var1,var2]].dropna()
    x = df_temp[var1].dropna().values
    y = df_temp[var2].dropna().values

    fig, ax = plt.subplots()
    sns.scatterplot(x=var1,y=var2,data=df,ax=ax,s=70)
    sns.regplot(x=var1,y=var2,color='k',data=df,scatter=False,ax=ax)
    text1 = f'r = {corr:0.3f}'
    if p<0.001:
        text2 = f'p < 0.001'
    else:
        text2 = f'p = {p:0.3f}'
    plt.text(x=min(x), y=max(y)-max(y)*0.05, s=text1)
    plt.text(x=min(x), y=max(y)-max(y)*0.1, s=text2)
    plt.grid(True)
    plt.savefig(save_path)

def main():
    # excel file
    df_path = str(sys.argv[1])
    var1 = str(sys.argv[2])
    var2 = str(sys.argv[3])
    save_path = f'{df_path[:-5]}_{var1}_{var2}.png'
    df_corr = pd.read_excel(df_path,sheet_name='corr',index_col=0)
    df_p = pd.read_excel(df_path,sheet_name='p-value',index_col=0)
    df = pd.read_excel(df_path,sheet_name='data',index_col=0)

    corr = df_corr.loc[var1,var2]
    p = df_p.loc[var1,var2]
    plot_corr(df,p,corr,var1,var2,save_path)



if __name__ == "__main__":
    main()
