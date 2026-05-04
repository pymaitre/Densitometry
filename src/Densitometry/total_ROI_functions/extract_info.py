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
from typing import Tuple
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import resmip as rsm
import matplotlib
matplotlib.use("Agg")


def save_info_nifti(save_info_all:bool, directory_out:Path, CT:rsm.Image, rt:rsm.RTStructureSet, ID:str)->None:
    """
    Save an image in NIFTI format
    
    :param save_info_all: save all the information
    :type save_info_all: bool
    :param directory_out: where to save the desired information
    :type directory_out: Path
    :param CT: CT image
    :type CT: rsm.Image
    :param rt: RT Structure Set
    :type rt: rsm.RTStructureSet
    :param ID: patient ID
    :type ID: str
    
    :return None
    
    """
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

            print("RTst_saved in: ")
            print(RTst_nifti_path)
            print("")
        except Exception as e:
            print("problem: ", e)

def ROI_ok(ct_path:Path, rt_path:Path, ROI_founded:str, show_CT_ROI:bool, save_info_all:bool, directory_out:Path, ID:str, slice:int)->Tuple[np.array,np.array]:
    """
    Function for obtaining ROIs and its distribution of HU.

    :param ct_path: path to the CT.
    :type ct_path: Path
    :param rt_path: path to the RT
    :type rt_path: Path
    :param ROI_founded: ROI you are looking for
    :type ROI_founded: str
    :param show_CT_ROI: selector for showing CT slice and ROI
    :param show_CT_ROI: bool
    :param save_info_all: save all the information
    :type save_info_all: bool
    :param directory_out: output folder
    :type directory_out: Path
    :param ID: patient ID
    :type ID: str
    :param slice: input number for slice view.
    :type slice: int

    :return HU_ROI: array of HU in the ROI.
    :return counts_ROI: array of HU relative counts.
    """
    
    #Read CT and CT_arr
    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)
    
    #Get RT Structure Set
    rt=rsm.RTStructureSet.read(filename=rt_path,structure_names=ROI_founded,reference_image=CT)
    
    #Mask
    mask = read_and_show_RTst(rt, ROI_founded)
    
    #Get HU and counts for each ROI
    HU_ROI, counts_ROI = obtain_ROI(mask, CT_arr, show_CT_ROI, slice)
    
    return HU_ROI, counts_ROI


def ROI_res(ct_path:Path, rt_path:Path, new_sp:np.array, ROI_founded:str, show_CT_ROI:bool, save_info_all:bool,
            directory_out:Path, ID:str, slice:int)->Tuple[np.array,np.array]:
    """
    Function for obtaining ROIs and its distribution of HU
    in patients with different voxel spacing.

    :param ct_path: CT image path
    :type ct_path: Path
    :param rt_path: RT Structure set path
    :type rt_path: Path
    :param new_sp: new spacing
    :type new_sp: np.array
    :param ROI_founded: ROI you are looking for
    :type ROI_founded: str
    :param show_CT_ROI: flag used to show the CT slice
    :type show_CT_ROI: bool
    :param save_info_all: save all the information
    :type save_info_all: bool
    :param directory_out: path where to save output
    :type directory_out: Path
    :param ID: patient's ID
    :type ID: str
    :param slice: desired slice
    :type slice: int
    
    :return HU_ROI_res: array of HU in the resampled ROI.
    :return counts_ROI_res: array of HU relative counts of resampled ROI.
    """
    
    #CT and CT_arr
    CT, CT_arr = read_and_show_ct(ct_path, show_CT_ROI, slice)
    
    #Resampling
    CT_res, CT_res_arr = resample(CT, new_sp[0], new_sp[1], new_sp[2])

    #Get RTStructure Set
    rt_res=rsm.RTStructureSet.read(filename=rt_path,structure_names=ROI_founded,reference_image=CT_res)
    
    #Get the mask
    mask_res = read_and_show_RTst(rt_res, ROI_founded)    
    
    #Get HU and counts for ROI
    HU_ROI_res, counts_ROI_res = obtain_ROI(mask_res, CT_res_arr, show_CT_ROI, slice)

    return HU_ROI_res, counts_ROI_res
 

def read_and_show_ct(ct_path:Path, show_CT_ROI:bool, slice:int)->Tuple[rsm.Image,np.array]:
    """
    Take CT from ct_path and show the slice you want.

    :param ct_path: path of CT directory.
    :type ct_path: Path
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :type show_CT_ROI: bool
    :param slice: input number for slice view.
    :type slice: int
    
    :return ct: CT image
    :return ct_arr: CT array showable
    """
    
    #Read image
    ct=rsm.Image.read(ct_path)
    
    #Get the CT array
    ct_arr = ct.__array__()
    print("The CT has a shape: ", ct_arr.shape)
    

    return ct, ct_arr


def read_and_show_RTst(rt_0:rsm.RTStructureSet, ROI_founded:str)->np.array:
    """
    This function relates to and shows the specific ROI founded for the CT.
    Because of significative value for 0 HU in CT, ROI of 0 and 1 is 
    converted in 1 and nan.

    :param rt_0: RTst image.
    :type rt_0: rsm.RTStructureSet
    :param ROI_founded: ROI you are looking for.
    :type ROI_founded: str

    :return mask: ROI's mask of 1 and nan instead of 1 and 0.
    """
    #Check the different ROIs
    print(f"ROI: {rt_0.keys()}")
    
    roi_obj = None
    
    #Get the desired RTStructures
    for name_ROI in rt_0.keys():
        if ROI_founded==name_ROI:
            print("Prendo la ROI con nome: ", name_ROI, "coincidente con ", ROI_founded)
            roi_obj = rt_0[name_ROI]
            break
        else:
            print("I'm analyzing the ROI: ", name_ROI)
    
    
    rt = roi_obj
    
    #Convert in array  
    rt_arr = rt.__array__()
    print("The RTst has a shape: ", rt_arr.shape, " and contains: ", np.unique(rt_arr, return_counts=True)[1][1], " 1")

    #Get the mask
    mask = rt_arr.astype(float)
    mask[mask == 0] = np.nan
        
    return mask
    


def obtain_ROI(mask:np.array, ct_arr:np.array, show_CT_ROI:bool, slice:int):
    """
    Here the real visualization of the ROI is given thanks to
    the product between the array of the CT and mask. 
    Than nan values are deleted.

    :param mask: ROI's mask of 1 and nan instead of 1 and 0.
    :type mask: np.array
    :param ct_arr: CT conversion in array for reading and showing
                    in Python.
    :type ct_arr: np.array
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :type show_CT_ROI: bool
    :param slice: input number for slice view.
    :type slice: int

    :return HU_ROI_no_nan: array of HU in the ROI.
    :return counts_ROI_no_nan: array of HU relative counts.
    """
    
    #Compute ct, HU, HU not NaN and counts not NaN for the desired ROI
    ct_ROI = mask * ct_arr
    HU_ROI, counts_ROI = np.unique(ct_ROI, return_counts=True)
    HU_ROI_no_nan=HU_ROI[np.where(~np.isnan(HU_ROI))[0]]
    counts_ROI_no_nan=counts_ROI[np.where(~np.isnan(HU_ROI))[0]]
    

    return HU_ROI_no_nan, counts_ROI_no_nan

def resample(image: rsm.Image, new_x:float, new_y:float, new_z:float) -> Tuple[rsm.Image, np.array]:
    """
    Resample image (increase pixel density) in order to increase computation accuracy.

    :param image: image to be resampled
    :type image: rsm.Image
    :param new_x: new_pixels for the x-axis
    :type new_x: float
    :param new_y: new_pixels for the y-axis
    :type new_y: float
    :param new_z: new_pixels for the z-axis
    :type new_z: float


    :return new_image: resampled image
    :return new_array_image: array of the resampled image.
    """   
    
    #Fill new_spacing
    new_spacing=np.array([new_x,new_y,new_z])
    
    #Check if all the dimensions are greater than 0
    orig_size=image.size
    for s in orig_size: 
        if s==0: 
            print("The image has one dimension equal to zero")

    #Resample the image
    new_image=rsm.Image.resample(image,new_spacing,sitk.sitkNearestNeighbor,0)
    
    
    #array from new_image
    new_array_image = new_image.__array__()
    
    
    return new_image,new_array_image
