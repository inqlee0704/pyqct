import pandas as pd
import numpy as np
import sys
from tqdm.auto import tqdm
from scipy.stats import pearsonr

def get_corr_pvalues(df):
    df.dropna(axis='columns',how='all',inplace=True)
    dfcols = pd.DataFrame(columns=df.columns)
    corrs = dfcols.transpose().join(dfcols, how='outer')
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    pbar = tqdm(df.columns)
    for r in pbar:
        x = df[r]
        for c in df.columns:
            y = df[c]
            not_nan = ~np.logical_or(np.isnan(x),np.isnan(y))
            try:
                corrs[r][c], pvalues[r][c] = pearsonr(x[not_nan],y[not_nan])
            except:
                print("P-value can not be calculated for: ")
                print(r,c)
                pvalues[r][c] = np.nan
                corrs[r][c] = np.nan
    return corrs, pvalues

def main():
    df_path = str(sys.argv[1])
    raw_df = pd.read_csv(df_path)
    print(f"Successfully read: {df_path}!\n")
    str_cols = ['Proj','Subj','CaseType','dis','Cluster','BD']
    drop_cols = [x for x in str_cols if x in raw_df.columns ]
    df = raw_df.drop(columns=drop_cols)
    print(f"Dropping {drop_cols} columns\n")
    print(f"Calculating correlations. . .\n")
    df_corr, df_pvalues = get_corr_pvalues(df)
    print(f"Saving the results. . .\n")
    with pd.ExcelWriter(f'{df_path[:-4]}_corr.xlsx') as writer:
        df_corr.to_excel(writer,sheet_name='corr')
        df_pvalues.to_excel(writer, sheet_name='p-value')
        raw_df.to_excel(writer,sheet_name='data',index=False)

if __name__ == "__main__":
    main()
