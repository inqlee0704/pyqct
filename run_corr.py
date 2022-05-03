import pandas as pd
import numpy as np
import sys
from tqdm.auto import tqdm
from scipy.stats import ttest_ind, ttest_rel

# run t-test
def calculate_pvalues(df, equal_var=False):
    dfcols = pd.DataFrame(columns=df.columns)
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    pbar = tqdm(df.columns)
    for r in pbar:
        for c in df.columns:
            try:
                pvalues[r][c] = ttest_ind(df[r],df[c],nan_policy='omit',equal_var=equal_var)[1]
            except:
                print(df[r])
                print(df[c])
                pvalues[r][c] = np.nan
                print(pvalues[r][c])
    return pvalues

def main():
    df_path = str(sys.argv[1])
    equal_var = False 
    raw_df = pd.read_csv(df_path)
    print(f"Successfully read: {df_path}!\n")
    str_cols = ['Proj','Subj','CaseType']
    drop_cols = [x for x in str_cols if x in raw_df.columns ]
    df = raw_df.drop(columns=drop_cols)
    print(f"Dropping {drop_cols} columns\n")
    print(f"Calculating correlations. . .\n")
    df_corr = df.corr()
    df_pvalues = calculate_pvalues(df, equal_var)
    print(f"Saving the results. . .\n")
    with pd.ExcelWriter(f'{df_path[:-4]}_corr.xlsx') as writer:
        df_corr.to_excel(writer,sheet_name='corr')
        df_pvalues.to_excel(writer, sheet_name='p-value')
        raw_df.to_excel(writer,sheet_name='data',index=False)

if __name__ == "__main__":
    main()
