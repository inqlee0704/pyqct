import sys
import numpy as np
import pandas as pd

df_path = str(sys.argv[1])
dis_col = str(sys.argv[2])

df = pd.read_csv(df_path)
diseases = np.unique(df[dis_col])

print(f"Split {df_path} by {dis_col}")
print('=============================')
for d in diseases:
    df_disease = df[df[dis_col]==d]
    df_disease.reset_index(drop=True,inplace=True)
    save_path = f'{df_path[:-4]}_{d}.csv'
    print(f'Save: {save_path}')
    df_disease.to_csv(save_path,index=False)