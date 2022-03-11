# python quality_check.py csv_path std_factor
# python quality_check.py temp.csv 3
import pandas as pd
import sys

# Assume first two columns are: Proj and Subj
# df_path = '../SABD_stats/SABD_TLC0_RV0_QCT_CFD1D_all_20220303.csv'
df_path = str(sys.argv[1])
std_factor = int(sys.argv[2])

df = pd.read_csv(df_path)
df_mean = df.iloc[:,2:].mean()
df_std = df.iloc[:,2:].std()
up_thre = df_mean + df_std * std_factor
lo_thre = df_mean - df_std * std_factor

for col in lo_thre.index:
    outlier_subs = []
    print(f'Checking {col}: {df_mean[col]:.3} \u00B1 {df_std[col]:.3}')
    print('-----------------------------------------------')
    for i in range(len(df)):
        if (df.loc[i,col] < lo_thre[col]) or (df.loc[i,col] > up_thre[col]):
            outlier_subs.append(i)
            print(f'{df.iloc[i,1]}: {float(df.loc[i,col]):.3}' )
    if len(outlier_subs)==0:
        print('PASS')
    print()
        
    
    