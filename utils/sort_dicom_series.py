# Adopted from Alex Weston
# https://towardsdatascience.com/a-python-script-to-sort-dicom-files-f1623a7f40b8

import os
import sys
from tqdm.auto import tqdm
import pydicom
from tqdm.auto import tqdm

def clean_text(string):
    # clean and standardize text descriptions, which makes searching files easier
    forbidden_symbols = ["*", ".", ",", "\"", "\\", "/", "|", "[", "]", ":", ";", " ", "(", ")"]
    for symbol in forbidden_symbols:
        string = string.replace(symbol, "_")
        string = string.replace("__", "_")
        if len(string)>1:
            string = string[:-1] if string[-1]=="_" else string
    return string.lower()  


# root_path = "D:\AnimalCT_2021"
# root_path = "/D/AnimalCT_2021"
# save_path = "D:\AnimalCT_2021_sorted"
# save_path = "/D/AnimalCT_2021_sorted"

def main():
    root_path = str(sys.argv[1])
    save_path = str(sys.argv[2])

    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    unsortedList = []
    for root, _, files in os.walk(root_path):
        for file in files: 
            if ".dcm" in file:# exclude non-dicoms, good for messy folders
                unsortedList.append(os.path.join(root, file))

    pbar = tqdm(unsortedList)
    for dicom_loc in pbar:
        Subj = dicom_loc.split('\\')[-2]
        # read the file
        ds = pydicom.read_file(dicom_loc, force=True)
    
        # get patient, study, and series information
        patientID = clean_text(ds.get("PatientID", "NA"))
        studyDate = clean_text(ds.get("StudyDate", "NA"))
        studyDescription = clean_text(ds.get("StudyDescription", "NA"))
        seriesDescription = clean_text(ds.get("SeriesDescription", "NA"))
    
        # generate new, standardized file name
        modality = ds.get("Modality","NA")
        studyInstanceUID = ds.get("StudyInstanceUID","NA")
        seriesInstanceUID = ds.get("SeriesInstanceUID","NA")
        instanceNumber = str(ds.get("InstanceNumber","0"))
        fileName = modality + "." + seriesInstanceUID + "." + instanceNumber + ".dcm"

        # uncompress files (using the gdcm package)
        # try:
        #     ds.decompress()
        # except:
        #     print('an instance in file %s - %s - %s - %s" could not be decompressed. exiting.' % (patientID, studyDate, studyDescription, seriesDescription ))
    
        # save files
        if not os.path.exists(os.path.join(save_path, Subj)):
            os.makedirs(os.path.join(save_path, Subj))

        if not os.path.exists(os.path.join(save_path, Subj, seriesDescription)):
            os.makedirs(os.path.join(save_path, Subj, seriesDescription))
            print('Saving out file: %s - %s.' % (Subj, seriesDescription ))
        
        ds.save_as(os.path.join(save_path, Subj, seriesDescription, fileName))

    
        # if not os.path.exists(os.path.join(save_path, Subj, studyDate)):
        #     os.makedirs(os.path.join(save_path, Subj, studyDate))
        
        # if not os.path.exists(os.path.join(save_path, Subj, studyDate, studyDescription)):
        #     os.makedirs(os.path.join(save_path, Subj, studyDate, studyDescription))
        
        # if not os.path.exists(os.path.join(save_path, Subj, studyDate, studyDescription, seriesDescription)):
        #     os.makedirs(os.path.join(save_path, Subj, studyDate, studyDescription, seriesDescription))
        #     print('Saving out file: %s - %s - %s - %s.' % (Subj, studyDate, studyDescription, seriesDescription ))
        
        # ds.save_as(os.path.join(save_path, Subj, studyDate, studyDescription, seriesDescription, fileName))

if __name__ == "__main__":

    main()