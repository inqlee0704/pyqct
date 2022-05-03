import numbers
import pandas as pd
import os
import os
import pandas as pd
import sys
import numpy as np
from tqdm.auto import tqdm
import SimpleITK as sitk
from medpy.io import load, save
import medpy
from scipy.ndimage.interpolation import zoom

# own modules
from medpy.io import header

def resample(img, hdr, target_spacing, bspline_order=3, mode='constant'):
        # set bsplie_order=0 if mask
        if isinstance(target_spacing, numbers.Number):
            target_spacing = [target_spacing] * img.ndim
        # compute zoom values
        zoom_factors = [old / float(new) for new, old in zip(target_spacing, header.get_pixel_spacing(hdr))]
        # zoom image
        img = zoom(img, zoom_factors, order=bspline_order, mode=mode)
        # set new voxel spacing
        header.set_pixel_spacing(hdr, target_spacing)
        
        return img, hdr

def crop_mask_img(mask,img,margin=20):
    for x in range(mask.shape[0]):
        slice = mask[x,:,:]
        if np.sum(slice)!=0:
            x_l = x
            break
    for x in range(mask.shape[0]):
        slice = mask[-x,:,:]
        if np.sum(slice)!=0:
            x_r = x
            break

    for y in range(mask.shape[1]):
        slice = mask[:,y,:]
        if np.sum(slice)!=0:
            y_l = y
            break
    for y in range(mask.shape[1]):
        slice = mask[:,-y,:]
        if np.sum(slice)!=0:
            y_r = y
            break

    for z in range(mask.shape[2]):
        slice = mask[:,:,z]
        if np.sum(slice)!=0:
            z_l = z
            break
    for z in range(mask.shape[2]):
        slice = mask[:,:,-z]
        if np.sum(slice)!=0:
            z_r = z
            break

    mask_cropped = mask[x_l-margin:-x_r+margin,y_l-margin:-y_r+margin,z_l:-z_r]
    img_cropped = img[x_l-margin:-x_r+margin,y_l-margin:-y_r+margin,z_l:-z_r]
    return mask_cropped, img_cropped

df = pd.read_csv('D:\AnimalCT_2021_sorted\\ENV18PM_animal_ProjSubjList_20220428.in')

# Convert dicom to analyze
missing_img = []
missing_mask = []
pbar = tqdm(range(len(df)))
for i in pbar:
    imgdir_path = df.loc[i,'ImgDir']
    mask_path = df.loc[i,'MaskDir']
    INEX = df.loc[i,'INEX']
    if INEX == 'IN':
        img_path = os.path.join(imgdir_path,'IN','zunu_vida-ct.img')
        img_save_path = os.path.join(imgdir_path,'IN','zunu_vida-ct_resample.img')
        mask_save_path = os.path.join(imgdir_path,'IN','ZUNU_lobes_resample.img')
    else:
        img_path = os.path.join(imgdir_path,'EX','zunu_vida-ct.img')
        img_save_path = os.path.join(imgdir_path,'EX','zunu_vida-ct_resample.img')
        mask_save_path = os.path.join(imgdir_path,'EX','ZUNU_lobes_resample.img')

    if os.path.exists(img_path):
        img, hdr = load(img_path)
    else:
        missing_img.append(img_path)
        continue

    if os.path.exists(mask_path):
        mask, mask_hdr = load(mask_path)
    else:
        missing_mask.append(mask_path)
        continue

    # Crop
    mask_crop, img_crop = crop_mask_img(mask,img,margin=20)
    # resample
    old_shape = mask_crop.shape
    new_shape = (512,512,old_shape[2])
    old_spacing = hdr.get_voxel_spacing()
    new_spacing = (old_spacing[0]*(old_shape[0]/new_shape[0]),old_spacing[1]*(old_shape[1]/new_shape[1]),old_spacing[2])

    if not os.path.exists(mask_save_path):
        resampled_mask, resampled_mask_hdr = resample(mask_crop, hdr, new_spacing,bspline_order=0, mode='nearest')
        save(resampled_mask,mask_save_path,resampled_mask_hdr)
    if not os.path.exists(img_save_path):
        resampled_img, resampled_hdr = resample(img_crop, hdr, new_spacing)
        save(resampled_img,img_save_path,resampled_hdr)

print(missing_img)
print(missing_mask)

    



