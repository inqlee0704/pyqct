import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np

def plot_corr(df,p,corr,var1,var2,save_path):

    df_temp = df.loc[:,[var1,var2]].dropna()
    x = df_temp[var1].dropna().values
    y = df_temp[var2].dropna().values
    plt.figure(dpi=1000)
    plt.scatter(x, y, s=10)
    plt.xlabel(var1,fontsize=18)
    plt.ylabel(var2,fontsize=18)

    z = np.polyfit(x, y, 1)
    f = np.poly1d(z)
    Xs = np.linspace(min(x),max(x),num=20)
    plt.plot(Xs,f(Xs),"r--")
    text1 = f'r = {corr:0.3f}'
    if p<0.001:
        text2 = f'p < 0.001'
    else:
        text2 = f'p = {p:0.3f}'
    plt.text(x=min(x), y=max(y)-max(y)*0.1, s=text1, fontsize=14)
    plt.text(x=min(x), y=max(y)-max(y)*0.2, s=text2, fontsize=14)
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
