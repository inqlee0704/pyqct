# merge two csv files based on Proj and Subj
import sys
import pandas as pd

df_left_path = str(sys.argv[1])
df_right_path = str(sys.argv[2])
save_path = str(sys.argv[3])

df_left = pd.read_csv(df_left_path)
df_right = pd.read_csv(df_right_path)

df_combined = df_left.merge(df_right, how='left', on=['Proj','Subj'])
df_combined.to_csv(save_path, index=False)
