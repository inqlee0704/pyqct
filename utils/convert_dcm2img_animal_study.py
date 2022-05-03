import pandas as pd
import os
import os
import pandas as pd
import sys
from tqdm.auto import tqdm
import SimpleITK as sitk
from medpy.io import load

def DCMtoVidaCT(pathImage,mask_folder='dicom',saveImage=None):

    if saveImage == None:
        print(f'Save path is  not given, image will be saved in: ')
        print(pathImage)
        saveImage = pathImage
    if not os.path.exists(saveImage):
        os.mkdir(saveImage)

    os.chdir(pathImage)
    path = os.getcwd()

    nImage = 1

    i = 0
    for i in range(nImage):
        pathDicom = os.path.join(pathImage,mask_folder)
        reader = sitk.ImageSeriesReader()
        filenamesDICOM = reader.GetGDCMSeriesFileNames(pathDicom)
        reader.SetFileNames(filenamesDICOM)
        imgOriginal = reader.Execute()
        # print("    The origin after creating DICOM:", imgOriginal.GetOrigin())
        # Flip the image. 
        # The files from Apollo have differnt z direction. 
        # Thus, we need to flip the image to make it consistent with Apollo.
        flipAxes = [ False, False, False ]
        flipped = sitk.Flip(imgOriginal,flipAxes,flipAboutOrigin=True)
        # print("    The origin after flipping DICOM:", flipped.GetOrigin())
        # Move the origin to (0,0,0)
        # After converting dicom to .hdr with itkv4, the origin of images changes. 
        # Thus we need to reset it to (0,0,0) to make it consistent with Apollo files.
        origin = [0.0,0.0,0.0]
        flipped.SetOrigin(origin)
        print("    The origin after flipping and changing origin to [0.,0.,0.]:", flipped.GetOrigin())
        sitk.WriteImage(flipped,saveImage + "/" + "zunu_vida-ct.hdr")
        

df = pd.read_csv('D:\AnimalCT_2021_sorted\\ENV18PM_animal_ProjSubjList_20220428.in')

IN_dir = 'ins_helical_idose_3'
EX_dir = 'exp_helical_idose_3'
pbar = tqdm(range(len(df)))
empty_list = []
# Convert dicom to analyze
for i in pbar:
    imgdir_path = df.loc[i,'ImgDir']
    IN_save_path = os.path.join(imgdir_path,'IN')
    if not os.path.exists(IN_save_path):
        if os.path.exists(os.path.join(imgdir_path,IN_dir)):
            DCMtoVidaCT(imgdir_path,mask_folder=IN_dir,saveImage=IN_save_path)
        else:
            empty_list.append(os.path.join(imgdir_path,IN_dir))
            
    EX_save_path = os.path.join(imgdir_path,'EX')
    if not os.path.exists(EX_save_path):
        if os.path.exists(os.path.join(imgdir_path,EX_dir)):
            DCMtoVidaCT(imgdir_path,mask_folder=EX_dir,saveImage=EX_save_path)
        else:
            empty_list.append(os.path.join(imgdir_path,EX_dir))
