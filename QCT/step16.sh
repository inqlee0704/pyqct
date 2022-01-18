#!/bin/bash
# ###################################################################################
# step16 to run calculate qCT variables
# ###################################################################################
# step16_*.sh {Subj}
# ###################################################################################
# 8/10/2021, Jiwoong Choi, In Kyu Lee
#  - nreg and for loop added.
#  - Emph_fSAD, instead of Emph. 
#  - Update S_norm is used (S_norm_v1b.py)
# 03/18/2021, In Kyu Lee
#  - < step16_v0b.sh
#  - s* is added 
#  - I1 and I2 are added as arguments
# ###################################################################################
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Step 16. Calculate Airtrapping, Emphysema, HAA, RRAVC, S_norm 
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# print commands and their arguments as they are executed
  set -x
# ------
  nreg=1
# ------
  Subj=$1  # H10892, PMSN02016

# Registration sets
# ---------------------------
  I1[1]='IN0';   I2[1]='EX0'
# I1[1]='TLC0';  I2[1]='FRC0'
# I1[2]='IND0';  I2[2]='FRC0'
# ---------------------------

  echo 'Starting at...'; date
# ###################################################################################
# Step 16. Airtrapping, Emphysema, HAA, RRAVC, s*
  for (( i=1; i<=$nreg ; i++ )); do
    python get_Airtrapping.py $Subj ${I1[i]} ${I2[i]} -856
    python get_Emph_fSAD.py $Subj ${I1[i]} ${I2[i]} -950 -856
    python get_HAA.py $Subj ${I1[i]} ${I2[i]} -700 0
    python get_RRAVC.py $Subj ${I1[i]} ${I2[i]} 
    python get_S_norm.py $Subj ${I1[i]} ${I2[i]} 
  done
# ############################################################################### END
