# pyqct
pyqct is a python repository to calculate and extract Quantitative Computed Tomography (QCT) variables. 

# Installation
Install requirements
```bash
# if you use viertual environment, activate it. 
# conda activate
python -m pip install -r requirements.txt 
```


# 1. Extract QCT
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

# 2. Quality check 
Find outliers for each variable.
```bash
python quality_check.py csv_path std_factor
```
- csv_path: path to csv file (first two columns are Proj and Subj)
- std_factor: mean +- std * std_factor to determine outliers

# 3. Statistical Analysis

## Correlation

## Correlation plots


# QCTs

## Deploy
./deploy_QCT.sh Proj_path/
```bash
./deploy_QCT.sh sample_data/ENV18PM/
# run for each subject
cd sample_data/ENV18PM/ENV18PM_PMSN12002/
./step16.sh PMSN12002
```
## Airtrapping

## Emph_fSAD

## HAA

## S_norm

## RRAVC


