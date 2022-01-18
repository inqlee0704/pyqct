# pyqct
pyqct is a python repository to calculate and extract Quantitative Computed Tomography (QCT) variables. 

# Installation



# extract_QCT
Calculate some QCTs and combine QCTs calculated in previous steps.
## run extract_QCT
python extract_QCT.py Proj_path Demo_path Proj
```
python extract_QCT.py data/sample_Proj/Proj_Subj data/sample_demo.csv ENV18PM
```

## QCTs calculated in extract_QCT:
- Circularity
- Normalized Wall Thickness
- Normalized Hydarulic Diameter
- Angles between:
  - RMB and LMB
  - sRUL and BronInt


Inputs:
- demographics: sample_data/ENV18PM_demo.csv


outputs 
- _QCT.csv file for each subject in a subject folder
- _QCT_all.csv file for one project in a project folder


# QCTs
