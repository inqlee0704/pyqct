# ##############################################################################
# Usage: python get_S_norm.py Subj I1 I2
# Time: ~ 20s
# Ref: 
# ##############################################################################
# 20220118, In Kyu Lee
# No version suffix
# ##############################################################################
# v1c: 08/11/2021, In Kyu Lee
# - Fixed: when V_IN < V_EX, s_norm returns nan issue.
#   - ownpow is used
# v1b: 08/10/2021, In Kyu Lee
# - S* stat is added
# 03/18/2021, In Kyu Lee
# Calculate S*
# ##############################################################################
# Input: 
#  - displacement img, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_disp_resample.mhd'
#  - IN lobe mask, ex) PMSN03001_IN0_vida-lobes.img
# Output:
#  - s* image, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_s_norm.img
#  - s* stat, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_lobar_s_norm.txt
# ##############################################################################w

# import libraries
import os
import sys
import numpy as np
import time
import pandas as pd
from medpy.io import load, save
import SimpleITK as sitk
sitk.ProcessObject_SetGlobalWarningDisplay(False)
import warnings
warnings.filterwarnings("ignore")

def ownpow(a, b):
    if a > 0:
        return a**b
    if a < 0:
        temp = abs(a)**b
        return -1*temp

start = time.time()
Subj = str(sys.argv[1]) # PMSN03001
I1 = str(sys.argv[2]) # 'IN0'
I2 = str(sys.argv[3]) # 'EX0'

disp_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_disp_resample.mhd'
histo_EX = pd.read_csv(f'{Subj}_{I2}_vida-histo.csv')
histo_IN = pd.read_csv(f'{Subj}_{I1}_vida-histo.csv')
s_norm_stat_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_lobar_s_norm.txt'

IN_lobe_path = f'{Subj}_{I1}_vida-lobes.img'
if not os.path.exists(IN_lobe_path):
    IN_lobe_path = f'{Subj}_{I1}_vida-lobes.img.gz'

s_norm_img_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_s_norm.img'
# V_cm3_IN 
V_EX = histo_EX.loc[histo_EX.location=='both', 'total-volume-cm3'].values[0]
V_IN = histo_IN.loc[histo_IN.location=='both', 'total-volume-cm3'].values[0]
# cm^3 -> mm^3
V_EX = V_EX * 1000
V_IN = V_IN * 1000

# Data Loading . . .
disp, disp_h = load(disp_path)
IN_lobe_img, IN_lobe_header = load(IN_lobe_path)
s_norm_h = disp_h
# [mm]
s = (disp[:,:,:,0]**2+disp[:,:,:,1]**2+disp[:,:,:,2]**2)**0.5
# This doesn't work if V_IN- V_EX is negative
# s_norm = s/((V_IN-V_EX)**(1/3))
s_norm = s/ownpow(V_IN-V_EX,1/3)

# Prep stat
s_norm_l0 = np.mean(s_norm[IN_lobe_img==8])
s_norm_l1 = np.mean(s_norm[IN_lobe_img==16])
s_norm_l2 = np.mean(s_norm[IN_lobe_img==32])
s_norm_l3 = np.mean(s_norm[IN_lobe_img==64])
s_norm_l4 = np.mean(s_norm[IN_lobe_img==128])
s_norm_mean = (s_norm_l0 + s_norm_l1 + s_norm_l2 + s_norm_l3 + s_norm_l4)/5

s_norm_l0_sd = np.std(s_norm[IN_lobe_img==8])
s_norm_l1_sd = np.std(s_norm[IN_lobe_img==16])
s_norm_l2_sd = np.std(s_norm[IN_lobe_img==32])
s_norm_l3_sd = np.std(s_norm[IN_lobe_img==64])
s_norm_l4_sd = np.std(s_norm[IN_lobe_img==128])
s_norm_sd = np.std(s_norm[IN_lobe_img!=0])

# CV = std/mean
s_norm_l0_cv = s_norm_l0_sd/s_norm_l0
s_norm_l1_cv = s_norm_l1_sd/s_norm_l1
s_norm_l2_cv = s_norm_l2_sd/s_norm_l2
s_norm_l3_cv = s_norm_l3_sd/s_norm_l3
s_norm_l4_cv = s_norm_l4_sd/s_norm_l4
s_norm_cv = s_norm_sd/s_norm_mean

s_norm_stat = pd.DataFrame({'Lobes':['Lobe0','Lobe1','Lobe2','Lobe3','Lobe4','All'],
              'sStar_m':np.float16([s_norm_l0,s_norm_l1,s_norm_l2,s_norm_l3,s_norm_l4,s_norm_mean]),
              'sStar_sd':np.float16([s_norm_l0_sd,s_norm_l1_sd,s_norm_l2_sd,s_norm_l3_sd,s_norm_l4_sd,s_norm_sd]),
              'sStar_cv':np.float16([s_norm_l0_cv,s_norm_l1_cv,s_norm_l2_cv,s_norm_l3_cv,s_norm_l4_cv,s_norm_cv])})


# Save
save(s_norm,s_norm_img_path,hdr=s_norm_h)
s_norm_stat.to_csv(s_norm_stat_path, index=False, sep=' ')
end = time.time()
print(f'Elapsed time: {end-start}s')
