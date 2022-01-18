# ##############################################################################
# Usage: python get_HAA.py Subj lower_threshold upper_threshold
# Time: ~ 15s
# Ref: 
# ##############################################################################
# 20220118, In Kyu Lee
# No version suffix
# ##############################################################################
# 02/19/2021, In Kyu Lee
# Calculate HAA 
# 03/18/2021, In Kyu Lee
#  - I1 & I2 are added as arguments
# ##############################################################################
# Input: 
#  - IN CT image, ex) PMSN03001_IN0.img.gz
#  - IN lobe mask, ex) PMSN03001_IN0_vida-lobes.img
# Output:
#  - HAA statistics, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_lobar_HAA.txt
#  - HAA image, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_HAA.img
# ##############################################################################w

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
if len(sys.argv)==4: # No threshold is given
    l_threshold = -700
    u_threshold = 0
elif len(sys.argv)==5: # Only lower threshold is given
    l_threshold = int(sys.argv[4])
    u_threshold = 1000
else: # Both lower and upper threshold are given
    l_threshold = int(sys.argv[4])
    u_threshold = int(sys.argv[5])
    
print(f'Lower Threshold: {l_threshold}  | Upper Threshold: {u_threshold}')

# Input Path
IN_path = f'{Subj}_{I1}.img.gz'
IN_lobe_path = f'{Subj}_{I1}_vida-lobes.img'
if not os.path.exists(IN_lobe_path):
    IN_lobe_path = f'{Subj}_{I1}_vida-lobes.img.gz'
# Output Path
HAA_stat_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_lobar_HAA{l_threshold}to{u_threshold}.txt'
HAA_img_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_HAA{l_threshold}to{u_threshold}.img'

# Data Loading . . .
IN_img,IN_header = load(IN_path)
IN_lobe_img, IN_lobe_header = load(IN_lobe_path)
# get .hdr from IN.hdr
HAA_h = IN_header

# prepare .img
HAA_img = np.zeros((IN_img.shape),dtype='uint8')
HAA_img[(l_threshold<=IN_img)&(IN_img<=u_threshold)] = 1
# 0 if outside lobe
HAA_img[IN_lobe_img==0] = 0

IN_l0 = len(IN_img[IN_lobe_img==8])
IN_l1 = len(IN_img[IN_lobe_img==16])
IN_l2 = len(IN_img[IN_lobe_img==32])
IN_l3 = len(IN_img[IN_lobe_img==64])
IN_l4 = len(IN_img[IN_lobe_img==128])
IN_t = IN_l0 + IN_l1 + IN_l2 + IN_l3 + IN_l4

HAA_l0 = HAA_img[IN_lobe_img==8].sum()
HAA_l1 = HAA_img[IN_lobe_img==16].sum()
HAA_l2 = HAA_img[IN_lobe_img==32].sum()
HAA_l3 = HAA_img[IN_lobe_img==64].sum()
HAA_l4 = HAA_img[IN_lobe_img==128].sum()
HAA_t = HAA_l0 + HAA_l1 + HAA_l2 + HAA_l3 + HAA_l4

HAA_stat = pd.DataFrame({'Lobes':['Lobe0','Lobe1','Lobe2','Lobe3','Lobe4','total'],
              'HAAratio':np.float16([HAA_l0/IN_l0,HAA_l1/IN_l1,HAA_l2/IN_l2,HAA_l3/IN_l3,HAA_l4/IN_l4,HAA_t/IN_t]),
              'voxels_HAA':[HAA_l0,HAA_l1,HAA_l2,HAA_l3,HAA_l4,HAA_t],
              'Voxels':[IN_l0,IN_l1,IN_l2,IN_l3,IN_l4,IN_t]})

# Save
HAA_stat.to_csv(HAA_stat_path, index=False, sep=' ')
save(HAA_img,HAA_img_path,hdr=HAA_h)
end = time.time()
print(f'Elapsed time: {end-start}s')
