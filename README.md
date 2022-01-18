# pyqct
pyqct is a python repository to calculate and extract Quantitative Computed Tomography (QCT) variables. 

# Installation



# extract_QCT
Calculate some QCTs and combine QCTs calculated in previous steps.
## run extract_QCT
python extract_QCT.py Proj_path Demo_path Proj
```
python extract_QCT.py sample_data/ENV18PM sample_data/ENV18PM_demo.csv ENV18PM
```

## QCTs calculated in extract_QCT:
- Circularity
- Normalized Wall Thickness
- Normalized Hydarulic Diameter
- Angles between:
  - RMB and LMB
  - sRUL and BronInt


Inputs:
- Project folder: sample_data/ENV18PM
- demographics: sample_data/ENV18PM_demo.csv


outputs 
- _QCT.csv file for each subject in a subject folder
- _QCT_all.csv file for one project in a project folder


# QCTs

## Deploy
```bash
./deploy_QCT.sh sample_data/ENV18PM/
```
## Airtrapping

## Emph_fSAD

## HAA

## S_norm

## RRAVC


