# ##############################################################################
# Usage: python get_Airtrapping.py Subj I1 I2 threshold
# Time: ~ 20s
# Ref:
# ##############################################################################
# 20220118, In Kyu Lee
# No version suffix
# ##############################################################################
# 02/19/2021, In Kyu Lee
# Calculate Airtrapping
# 03/18/2021, In Kyu Lee
#  - I1 & I2 are added as arguments
# 08/10/2021, In Kyu Lee
#  - Arguments error fixed
# ##############################################################################
# Input: 
#  - EX CT image, ex) PMSN03001_EX0.img.gz
#  - EX lobe mask, ex) PMSN03001_EX0_vida-lobes.img
# Output:
#  - Airtrapping statistics, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_AirT.txt
#  - Airtrapping img, ex) PMSN03001_EX0-TO-PMSN03001_IN0-SSTVD_AirT.img
# ##############################################################################

# import libraries
from medpy.io import load, save
import numpy as np
import pandas as pd
import os
import sys
import time
import SimpleITK as sitk
sitk.ProcessObject_SetGlobalWarningDisplay(False)

start = time.time()
Subj = str(sys.argv[1]) # Subj = 'PMSN03001'
I1 = str(sys.argv[2]) # I1 = 'IN0'
I2 = str(sys.argv[3]) # I2 = 'EX0'

if len(sys.argv)==4:
    threshold = -856
else:
    threshold = int(sys.argv[4])

# Input Path
EX_path = f'{Subj}_{I2}.img.gz'
EX_lobe_path = f'{Subj}_{I2}_vida-lobes.img'
if not os.path.exists(EX_lobe_path):
    EX_lobe_path = f'{Subj}_{I2}_vida-lobes.img.gz'

# Output Path
atrap_stat_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_lobar_AirT.txt'
atrap_img_path = f'{Subj}_{I2}-TO-{Subj}_{I1}-SSTVD_AirT.img'

# Data Loading . . .
EX_img,EX_header = load(EX_path)
EX_lobe_img, _ = load(EX_lobe_path)
atrap_h = EX_header

# prepare .img
atrap_img = np.zeros((EX_img.shape),dtype='uint8')
atrap_img[(EX_img<threshold)] = 1
atrap_img[EX_lobe_img==0] = 0

# prepare Airtrapping stat
EX_l0 = len(EX_img[EX_lobe_img==8])
EX_l1 = len(EX_img[EX_lobe_img==16])
EX_l2 = len(EX_img[EX_lobe_img==32])
EX_l3 = len(EX_img[EX_lobe_img==64])
EX_l4 = len(EX_img[EX_lobe_img==128])
EX_t = EX_l0 + EX_l1 + EX_l2 + EX_l3 + EX_l4

atrap_l0 = len(atrap_img[(EX_lobe_img==8)&(atrap_img==1)])
atrap_l1 = len(atrap_img[(EX_lobe_img==16)&(atrap_img==1)])
atrap_l2 = len(atrap_img[(EX_lobe_img==32)&(atrap_img==1)])
atrap_l3 = len(atrap_img[(EX_lobe_img==64)&(atrap_img==1)])
atrap_l4 = len(atrap_img[(EX_lobe_img==128)&(atrap_img==1)])
atrap_t = atrap_l0 + atrap_l1 + atrap_l2 + atrap_l3 + atrap_l4

atrap_stat = pd.DataFrame({'Lobes':['Lobe0','Lobe1','Lobe2','Lobe3','Lobe4','total'],
              'airtrapratio':np.float32([atrap_l0/EX_l0,atrap_l1/EX_l1,atrap_l2/EX_l2,atrap_l3/EX_l3,atrap_l4/EX_l4,atrap_t/EX_t]),
              'voxels_trap':[atrap_l0,atrap_l1,atrap_l2,atrap_l3,atrap_l4,atrap_t],
              'Voxels':[EX_l0,EX_l1,EX_l2,EX_l3,EX_l4,EX_t]})

# Save
atrap_stat.to_csv(atrap_stat_path, index=False, sep=' ')
save(atrap_img,atrap_img_path,hdr=atrap_h)
end = time.time()
print(f'Elapsed time: {end-start}s')
