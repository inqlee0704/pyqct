# pyqct
pyqct is a python repository to calculate and extract Quantitative Computed Tomography (QCT) variables. 

# Installation
Install requirements
```bash
git clone https://github.com/inqlee0704/pyqct.git
# if you don't have viertual environment, create it
conda create --name pyqct_test python=3.8
# and activate it.
conda activate pyqct_test
# Let's install requirement packages.
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


Outputs 
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
Calculate correlations
```bash
python run_corr.py {csv_path}
```
- csv_path: path to csv file (first two columns are Proj and Subj)

Output:
- excel file: f'{csv_path}_corr.xlsx'

## Correlation plots
Plot correlation
```bash
python plot_corr.py {excel_path} {var1} {var2}
```
- excel_path: *_corr.xlsx
- var1: first variable (x-axis)
- var2: second variable (y-axis)

Output:
- *_corr_{var1}_{var2}.png

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


# Data Organization
## Merge data
Merge two csv files based on Proj and Subj
```bash
python merge_csv {df_left_path} {df_right_path} {save_path}
```
## Sort dicom files 
Run this when more than one dicom series are stored in one folder.

```bash
cd utils
python sort_dicom_series.py {root_path} {save_path}
```
convert: Proj/date/Subj/*.dcm => Proj/Subj/DCM_series/*.dcm\
**Need to modify the code if data structure is different**

- Proj_path: root path to dicom directory, ex) /d/AnimalCT_2021
- save_path: save_path, ex) /d/AnimalCT_2021_sorted 