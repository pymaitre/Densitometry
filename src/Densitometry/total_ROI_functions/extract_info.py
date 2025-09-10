"""
Module for:
- reading and showing CT images;
- reading and showing the RTst;
- finding the ROI needed;
- recreating the ROI on the CT;
- extracting HU and Counts.

"""

import os
from pathlib import Path
from Densitometry.total_ROI_functions import dicom_to_nifti as dtn
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt


def save_info_nifti(save_info_all, directory_out, CT, rt, ID):
    if save_info_all:
        dir_nifti = Path(directory_out) / "dataset" / "imagesTr"
        Path(dir_nifti).mkdir(parents=True, exist_ok=True)
    
        dir_RTst = Path(directory_out) / "dataset" / "labelsTr"
        Path(dir_RTst).mkdir(parents=True, exist_ok=True)

        # CT_nifti_path = dir_nifti / f'PAN_NET_{ID}_0000.nii.gz'
        CT_nifti_path = dir_nifti / f'prova_colangio_{ID}_0000.nii.gz'
        RTst_nifti_path = dir_RTst / f'prova_colangio_{ID}.nii.gz'
        
        try:
            sitk.WriteImage(CT, str(CT_nifti_path))
            print("CT_saved in:")
            print(CT_nifti_path)
            sitk.WriteImage(rt, str(RTst_nifti_path))
            
            # for roi in rt:
            #     if roi.name == "pancreas":
            #         roi1_label = 1
            #         roi1_labeled = sitk.Multiply(roi.mask, roi1_label)
            #     else:
            #         roi2_label = 2
            #         roi2_labeled = sitk.Multiply(roi.mask, roi2_label)

            # # Combina le due maschere. Se ci sono sovrapposizioni, la seconda ROI può sovrascrivere la prima.
            # combined_mask = sitk.Maximum(roi1_labeled, roi2_labeled)

            # # Salva come NIfTI
            # sitk.WriteImage(combined_mask, str(RTst_nifti_path))
            print("RTst_saved in: ")
            print(RTst_nifti_path)
            print("")
        except Exception as e:
            print("problem: ", e)

def ROI_ok(ct_path, rt_path, ROI_founded, show_CT_ROI, save_info_all, directory_out, ID, slice):
    """
    Function for obtaining ROIs and its distribution of HU.

    :param rt: RTst image.
    :param ROI_founded: ROI you are looking for.
    :param ct_arr: CT array showable.
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :param slice: input number for slice view.

    :return HU_ROI: array of HU in the ROI.
    :return counts_ROI: array of HU relative counts.
    """

    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)
    rt = dtn.read_dicom_rtstruct(rt_path, CT, ROI_founded)
    rt_nifti = dtn.read_dicom_rtstruct(rt_path, CT)

    # save_info_nifti(save_info_all, directory_out, CT, rt_nifti, ID)
    
    mask = read_and_show_RTst(rt, ROI_founded)
    HU_ROI, counts_ROI = obtain_ROI(mask, CT_arr, show_CT_ROI, slice)
    
    return HU_ROI, counts_ROI


def ROI_res(ct_path, rt_path, new_sp, ROI_founded, show_CT_ROI, save_info_all, directory_out, ID, slice):
    """
    Function for obtaining ROIs and its distribution of HU
    in patients with different voxel spacing.

    :param Ct: CT image.
    :return rt_path: RTst's dcm file.
    :param ROI_founded: ROI you are looking for.
    :param new_sp: new voxel spacing for resampling.
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :param slice: input number for slice view.
    
    :return HU_ROI_res: array of HU in the resampled ROI.
    :return counts_ROI_res: array of HU relative counts of resampled ROI.
    """
    
    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)
    # new_sp = [0.703125,	0.703125,	1.25]
    CT_res, CT_res_arr = resample(CT, new_sp[0], new_sp[1], new_sp[2])
    
    rt_res = dtn.read_dicom_rtstruct(rt_path, CT_res, ROI_founded)
    # print(type(rt_res), type(rt_res[0]))
    rt_res_nifti = dtn.read_dicom_rtstruct(rt_path, CT_res)

    # save_info_nifti(save_info_all, directory_out, CT_res, rt_res_nifti, ID)    
    
    mask_res = read_and_show_RTst(rt_res, ROI_founded)    
    HU_ROI_res, counts_ROI_res = obtain_ROI(mask_res, CT_res_arr, show_CT_ROI, slice)

    return HU_ROI_res, counts_ROI_res
 

def read_and_show_ct(ct_path, show_CT_ROI, slice):
    """
    Take CT from ct_path and show the slice you want.

    :param ct_path: path of CT directory.
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :param slice: input number for slice view.
    
    :return ct: CT image
    :return ct_arr: CT array showable
    """
    
    ct = dtn.read_dicom_image(ct_path)
    ct_arr = sitk.GetArrayFromImage(ct)
    print("The CT has a shape: ", ct_arr.shape)
    
    # if show_CT_ROI:
    #     plt.imshow(ct_arr[slice])
    #     plt.show()

    return ct, ct_arr


def read_and_show_RTst(rt, ROI_founded):
    """
    This function relates to and shows the specific ROI founded for the CT.
    Because of significative value for 0 HU in CT, ROI of 0 and 1 is 
    converted in 1 and nan.

    :param rt: RTst image.
    :param ROI_founded: ROI you are looking for.

    :return mask: ROI's mask of 1 and nan instead of 1 and 0.
    """
 
    for ROI in rt:
        if ROI_founded in ROI.name:
            print("Prendo la ROI con nome: ", ROI.name, "coincidente con ", ROI_founded)
            break
        else:
            print("I'm analyzing the ROI: ", ROI.name)
            
    rt = ROI.mask
                    
    rt_arr = sitk.GetArrayFromImage(rt)
    print("The RTst has a shape: ", rt_arr.shape, " and contains: ", np.unique(rt_arr, return_counts=True)[1][1], " 1")

    mask = rt_arr.astype(float)
    mask[mask == 0] = np.nan
    
    # if show_CT_ROI:
    #     print("The ROI has a shape: ", np.unique(rt_arr, return_counts=True))
    #     plt.imshow(rt_arr[slice])

        # print("The CT mask has a shape: ", np.unique(mask, return_counts=True))
        # plt.imshow(mask[slice])
        
    return mask
    


def obtain_ROI(mask, ct_arr, show_CT_ROI, slice):
    """
    Here the real visualization of the ROI is given thanks to
    the product between the array of the CT and mask. 
    Than nan values are deleted.

    :param mask: ROI's mask of 1 and nan instead of 1 and 0.
    :param CT_arr: CT conversion in array for reading and showing
                    in Python.
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :param slice: input number for slice view.

    :return HU_ROI_no_nan: array of HU in the ROI.
    :return counts_ROI_no_nan: array of HU relative counts.
    """
    
    ct_ROI = mask * ct_arr
    HU_ROI, counts_ROI = np.unique(ct_ROI, return_counts=True)
    HU_ROI_no_nan=HU_ROI[np.where(~np.isnan(HU_ROI))[0]]
    counts_ROI_no_nan=counts_ROI[np.where(~np.isnan(HU_ROI))[0]]
    
    # if show_CT_ROI:
    #     print("The number of HU and counts in the ROI is: ", len(HU_ROI_no_nan), " and ", len(counts_ROI_no_nan))
        # print("La CT di partenza nella ROI è del tipo: ", ct_ROI.shape)
        # print(HU_ROI_no_nan)
        # print(counts_ROI_no_nan)
        # plt.imshow(ct_ROI[slice])
        # plt.colorbar()
        # plt.show()

    return HU_ROI_no_nan, counts_ROI_no_nan


from typing import Tuple
def resample(
    # image: sitk.Image, xy_rescale_factor: float = 2, z_rescale_factor: float = 1,
    image: sitk.Image, new_x, new_y, new_z
) -> Tuple[sitk.Image, np.array]:
    """
    Resample image (increase pixel density) in order to increase computation accuracy.

    :param image: image to be resampled (sitk.Image)
    :param xy_rescale_factor: new_pixels/old_pixels ratio for the x-y plane (float)
    :param z_rescale_factor: new_pixels/old_pixels ratio for the z axis (float)
    :return: resampled image (sitk.Image)
    """   
    original_spacing = image.GetSpacing()
    original_size = image.GetSize()
    spacing = min(original_spacing)
    new_spacing = [new_x, new_y, new_z]
    new_size = list(original_size)
    for i in range(3):
        new_size[i] = int(round(original_spacing[i] / new_spacing[i] * original_size[i]))
    resampled_image = sitk.Resample(
        image,
        new_size,
        sitk.Transform(),
        sitk.sitkNearestNeighbor,
        # sitk.sitkLinear,
        # sitk.sitkBSpline,
        image.GetOrigin(),
        new_spacing,
        image.GetDirection(),
        0,
        image.GetPixelID(),
    )
    return resampled_image, sitk.GetArrayFromImage(resampled_image)