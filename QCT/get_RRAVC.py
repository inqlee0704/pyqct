# ##############################################################################
# Usage: python get_RRAVC.py Subj
# Run Time: ~15s
# Ref: [Relative Regional Air Volume Change Maps at the Acinar scale ...]
# ##############################################################################
# 20220118, In Kyu Lee
# No version suffix
# ##############################################################################
# 02/24/2021, In Kyu Lee
# Desc: Calculate RRAVC
# 03/18/2021, In Kyu Lee
#  - I1 & I2 are added as arguments
# ##############################################################################
# Input: 
#  - airDiff img, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_airDiff.img  
#  - Fixed Air volume img, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_fixed_airVol.img
#  - IN lobe mask, ex) PMSN03001_IN0_vida-lobes.img
# Output:
#  - RRAVC_img, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_RRAVC.img
#  - RRAVC_stat, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_lobar_RRAVC.txt
# ##############################################################################

# import libraries
import os
import sys
import time
import numpy as np
import pandas as pd
from medpy.io import load, save
import SimpleITK as sitk
sitk.ProcessObject_SetGlobalWarningDisplay(False)
import warnings
warnings.filterwarnings("ignore")

start = time.time()
Subj = str(sys.argv[1]) # Subj = 'PMSN03001'
I1 = str(sys.argv[2]) # I1 = 'IN0'
I2 = str(sys.argv[3]) # I2 = 'EX0'

# Input Path
airdiff_path  = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_airDiff.img'
if not os.path.exists(airdiff_path):
    airdiff_path  = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_airDiff.img.gz'

fixed_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_fixed_airVol.img'
if not os.path.exists(fixed_path):
    fixed_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_fixed_airVol.img.gz'
IN_lobe_path = f'{Subj}_{I1}_vida-lobes.img'
if not os.path.exists(IN_lobe_path):
    IN_lobe_path = f'{Subj}_{I1}_vida-lobes.img.gz'
# Output Path
RRAVC_stat_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_lobar_RRAVC.txt'
RRAVC_img_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_RRAVC.img'

# Data Loading . . .
av_fixed_img, av_fixed_h = load(fixed_path)
airdiff_img, airdiff_h = load(airdiff_path)
IN_lobe_img, IN_lobe_header = load(IN_lobe_path)
# get .hdr from IN.hdr
RRAVC_h = av_fixed_h

# air_dff/fixed_airvol
# RRAVC_Denominator
V_airdiff = np.sum(airdiff_img)
V_airfixed = np.sum(av_fixed_img)
RRAVC_den = V_airdiff/V_airfixed

RRAVC_num = airdiff_img/av_fixed_img
RRAVC_num[np.isnan(RRAVC_num)] = 0

RRAVC_img = RRAVC_num/RRAVC_den

# Set background to be -100
RRAVC_img[IN_lobe_img==0] = -100

# Prep stat
RRAVC_l0 = np.mean(RRAVC_img[IN_lobe_img==8])
RRAVC_l1 = np.mean(RRAVC_img[IN_lobe_img==16])
RRAVC_l2 = np.mean(RRAVC_img[IN_lobe_img==32])
RRAVC_l3 = np.mean(RRAVC_img[IN_lobe_img==64])
RRAVC_l4 = np.mean(RRAVC_img[IN_lobe_img==128])
RRAVC_mean = (RRAVC_l0 + RRAVC_l1 + RRAVC_l2 + RRAVC_l3 + RRAVC_l4)/5

RRAVC_l0_sd = np.std(RRAVC_img[IN_lobe_img==8])
RRAVC_l1_sd = np.std(RRAVC_img[IN_lobe_img==16])
RRAVC_l2_sd = np.std(RRAVC_img[IN_lobe_img==32])
RRAVC_l3_sd = np.std(RRAVC_img[IN_lobe_img==64])
RRAVC_l4_sd = np.std(RRAVC_img[IN_lobe_img==128])
RRAVC_sd = np.std(RRAVC_img[IN_lobe_img!=0])

# CV = std/mean
RRAVC_l0_cv = RRAVC_l0_sd/RRAVC_l0
RRAVC_l1_cv = RRAVC_l1_sd/RRAVC_l1
RRAVC_l2_cv = RRAVC_l2_sd/RRAVC_l2
RRAVC_l3_cv = RRAVC_l3_sd/RRAVC_l3
RRAVC_l4_cv = RRAVC_l4_sd/RRAVC_l4
RRAVC_cv = RRAVC_sd/RRAVC_mean

RRAVC_stat = pd.DataFrame({'Lobes':['Lobe0','Lobe1','Lobe2','Lobe3','Lobe4','All'],
              'RRAVC_m':np.float16([RRAVC_l0,RRAVC_l1,RRAVC_l2,RRAVC_l3,RRAVC_l4,RRAVC_mean]),
              'RRAVC_sd':np.float16([RRAVC_l0_sd,RRAVC_l1_sd,RRAVC_l2_sd,RRAVC_l3_sd,RRAVC_l4_sd,RRAVC_sd]),
              'RRAVC_cv':np.float16([RRAVC_l0_cv,RRAVC_l1_cv,RRAVC_l2_cv,RRAVC_l3_cv,RRAVC_l4_cv,RRAVC_cv])})

# Save
# Convert float64 -> float32
save(RRAVC_img.astype('float32'),RRAVC_img_path,hdr=RRAVC_h)
RRAVC_stat.to_csv(RRAVC_stat_path, index=False, sep=' ')

end = time.time()
print(f'Elapsed time: {end-start}s')
