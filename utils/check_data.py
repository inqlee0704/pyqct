import os
import sys
import pandas as pd
from medpy.io import load
from tqdm.auto import tqdm

import SimpleITK as sitk

sitk.ProcessObject_SetGlobalWarningDisplay(False)
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def check_files(df):
    subj_paths = df.loc[:, "ImgDir"].values
    img_path_ = [
        os.path.join(subj_path, "zunu_vida-ct.img") for subj_path in subj_paths
    ]
    mask_path_ = [
        os.path.join(subj_path, "ZUNU_vida-airtree.img.gz") for subj_path in subj_paths
    ]
    for i in range(len(img_path_)):
        if not os.path.exists(img_path_[i]):
            print(img_path_[i], "Not exists")
        if not os.path.exists(mask_path_[i]):
            print(mask_path_[i], "Not exists")



def main():

    data_path = str(sys.argv[1]) # /data

    df = pd.read_csv(data_path, sep="\t")
    # Check if exists
    check_files(df)

    # Check dimensions of image and mask
    pbar = tqdm(enumerate(df.ImgDir), total=len(df))
    for i, subj_path in pbar:
        img, _ = load(os.path.join(subj_path, "zunu_vida-ct.img"))
        lung, _ = load(os.path.join(subj_path, "ZUNU_vida-lung.img.gz"))
        if img.shape != lung.shape:
            print(f"Dimension not match")
            print(subj_path)
            print(f"img: {img.shape}  | lung: {lung.shape}")

if __name__ == "__main__":
    main()
