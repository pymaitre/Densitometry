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
from src.Densitometry.total_ROI_functions import dicom_to_nifti as dtn
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt


def CT_and_ROI(df_py, pz, specific_ROI, show_CT_ROI, slice=40):
    """
    This function resumes the more important information for 
    recreating and showing the ROI of a specific CT.

    :param df_py: database of headers information.
    :param pz: iterator on the database for selecting the patient.
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :param slice: input number for slice view.

    :return CT: CT image.
    :return CT_arr: CT conversion in array for reading and showing
                    in Python.
    :return rt_path: RTst's dcm file.
    :return rt: RTst with all ROI's masks.
    :return ROI_founded: ROI you are looking for.
    """
    
    ct_path = df_py.loc[pz, "Path"]
    print("")
    print("The CT is in: ", Path(ct_path).parent)
    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)
    
    rt_folder = (Path(ct_path).parent / "RTst")
    rt_path = list(rt_folder.glob("RS*"))[0]
    rt = dtn.read_dicom_rtstruct(rt_path, CT)    
    # print(rt)
    ROI_founded = ""
    if not specific_ROI[0]:
        ROI_founded = find_ROI(rt)
        
    return CT, CT_arr, rt_path, rt, ROI_founded


def read_and_show_ct(ct_path, show_CT_ROI, slice=40):
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
    
    if show_CT_ROI:
        print("The CT has a shape: ", ct_arr.shape)        
        # plt.imshow(ct_arr[slice])
        # plt.show()

    return ct, ct_arr


def find_ROI(rt):
    """
    This function checks correspondences in ROIs names.

    :param rt: RTst image

    :return ROI_fin: ROI found.
    """
    
    nomi_ROI = ['CTV_Mammella', 'CTV', 'PTV_Mammella', 'PTV', 'ctv', 'ptv']
    importanza = {'CTV_Mammella':6, 'CTV':5, 'ctv':4, 'PTV_Mammella':3, 'PTV':2, 'ptv':1}
    # nomi_ROI = ['PTV_Mammella', 'PTV']
    # importanza = {'PTV_Mammella':2, 'PTV':1}
    
    nomi_con_importanza = [(nome, importanza[nome]) for nome in nomi_ROI]
    nomi_ordinati = sorted(nomi_con_importanza, key=lambda x: x[1], reverse=True)

    nomi_contours = []    
    for ROI in rt:        
        nomi_contours.append(ROI.name)
    
    print("The contours of the patient are: ", nomi_contours)
    print("")

    ROI_fin = None
    for nome, _ in nomi_ordinati:
        for ROI_founded in nomi_contours:
            # print("Check Nomi", nome, ROI_founded)
            if (ROI_founded is not None and ROI_founded == nome):                 
                print("Match found for equality between ", nome, "and ", ROI_founded)  
                ROI_fin = ROI_founded               
                break
                
            else:
                if (ROI_founded is not None and nome in ROI_founded):
                    print("Match found because ", nome, "is in", ROI_founded)  
                    ROI_fin = ROI_founded               
                    break
                
        if ROI_fin is not None:
            break
        
    return ROI_fin


def ROI_ok(rt, ROI_founded, CT_arr, show_CT_ROI, slice=40):
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

    mask = read_and_show_RTst(rt, ROI_founded)
    HU_ROI, counts_ROI = obtain_ROI(mask, CT_arr, show_CT_ROI, slice)
    
    return HU_ROI, counts_ROI
  

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
        if ROI.name == ROI_founded:
            rt = ROI.mask
            # print("Prendo la ROI con nome: ", ROI.name, "coincidente con ", ROI_founded)
                    
    rt_arr = sitk.GetArrayFromImage(rt)
    print("The RTst has a shape: ", rt_arr.shape, " and contains: ", np.unique(rt_arr, return_counts=True)[1][1], " 1")

    mask = rt_arr.astype(float)
    mask[mask == 0] = np.nan
    
    # if show_CT_ROI:
    #     print("The ROI has a shape: ", np.unique(rt_arr, return_counts=True))
    #     plt.imshow(rt_arr[slice])

    #     print("The CT mask has a shape: ", np.unique(mask, return_counts=True))
    #     plt.imshow(mask[slice])
        
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
    
    if show_CT_ROI:
        print("The number of HU and counts in the ROI is: ", len(HU_ROI_no_nan), " and ", len(counts_ROI_no_nan))
        # print("La CT di partenza nella ROI è del tipo: ", ct_ROI.shape, " e contiene: ")
        # print(HU_ROI_no_nan)
        # print(counts_ROI_no_nan)
        # plt.imshow(ct_ROI[slice])
        # plt.colorbar()
        # plt.show()

    return HU_ROI_no_nan, counts_ROI_no_nan


def ROI_res(CT, new_sp, rt_path, ROI_founded, show_CT_ROI, slice=40):
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
    
    CT_res, CT_res_arr = resample(CT, new_sp[0], new_sp[1], new_sp[2])
    rt_res = dtn.read_dicom_rtstruct(rt_path, CT_res)
    mask_res = read_and_show_RTst(rt_res, ROI_founded)    
    HU_ROI_res, counts_ROI_res = obtain_ROI(mask_res, CT_res_arr, show_CT_ROI, slice)

    return HU_ROI_res, counts_ROI_res
    

def resample(
    # image: sitk.Image, xy_rescale_factor: float = 2, z_rescale_factor: float = 1,
    image: sitk.Image, new_x, new_y, new_z
) -> sitk.Image:
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