# concatenate two csv files based on Proj and Subj
import sys
import pandas as pd

df_top_path = str(sys.argv[1])
df_bottom_path = str(sys.argv[2])
save_path = str(sys.argv[3])

df_top = pd.read_csv(df_top_path)
df_bottom = pd.read_csv(df_bottom_path)

df_combined = pd.concat([df_top,df_bottom])
df_combined.to_csv(save_path, index=False)
