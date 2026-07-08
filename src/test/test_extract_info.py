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
import pytest
matplotlib.use("Agg")


@pytest.mark.parametrize("save_info_all,ID",[(True,"1")],)
def test_save_info_nifti(save_info_all:bool, reference_dir_out:Path, reference_CT:rsm.Image, reference_RT:rsm.RTStructureSet, ID:str)->None:
    """
    Save an image in NIFTI format
    
    :param save_info_all: save all the information.
    :type save_info_all: bool
    :param directory_out: where to save the desired information.
    :type directory_out: Path
    :param CT: CT image.
    :type CT: rsm.Image
    :param rt: RT Structure Set.
    :type rt: rsm.RTStructureSet
    :param ID: patient ID.
    :type ID: str
    
    :return: None
    
    """
    if save_info_all:
        dir_nifti = Path(reference_dir_out) / "dataset" / "imagesTr"
        Path(dir_nifti).mkdir(parents=True, exist_ok=True)
    
        dir_RTst = Path(reference_dir_out) / "dataset" / "labelsTr"
        Path(dir_RTst).mkdir(parents=True, exist_ok=True)
        
        CT_nifti_path = dir_nifti / f'test_{ID}_0000.nii.gz'
        RTst_nifti_path = dir_RTst / f'test_{ID}.nii.gz'
        
        try:
            sitk.WriteImage(reference_CT, str(CT_nifti_path))
            print("CT_saved in:")
            print(CT_nifti_path)
            sitk.WriteImage(reference_RT, str(RTst_nifti_path))

            print("RTst_saved in: ")
            print(RTst_nifti_path)
            print("")
        except Exception as e:
            print("problem: ", e)
            
            
@pytest.mark.parametrize("ROI_founded,show_CT_ROI,save_info_all,ID,slice",[("GTV-1",True,False,"1",0)],)
def test_ROI_ok(reference_CT_path:Path, reference_RT_path:Path, ROI_founded:str, show_CT_ROI:bool, save_info_all:bool, reference_dir_out:Path, ID:str, slice:int)->Tuple[np.array,np.array]:
    """
    Function for obtaining ROIs and its distribution of HU.

    :param ct_path: path to the CT.
    :type ct_path: Path
    :param rt_path: path to the RT.
    :type rt_path: Path
    :param ROI_founded: ROI you are looking for.
    :type ROI_founded: str
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :param show_CT_ROI: bool
    :param save_info_all: save all the information.
    :type save_info_all: bool
    :param directory_out: output folder.
    :type directory_out: Path
    :param ID: patient ID.
    :type ID: str
    :param slice: input number for slice view.
    :type slice: int

    :return: array of HU in the ROI and array of HU relative counts.
    :rtype: Tuple[np.array,np.array]
    """
    
    #Read CT and CT_arr
    CT, CT_arr = test_read_and_show_ct(reference_CT_path, show_CT_ROI, slice)
    
    #Get RT Structure Set
    rt=rsm.RTStructureSet.read(filename=reference_RT_path,structure_names=ROI_founded,reference_image=CT)
    
    #Mask
    mask = test_read_and_show_RTst(rt, ROI_founded)
    
    #Get HU and counts for each ROI
    HU_ROI, counts_ROI = test_obtain_ROI(mask, CT_arr, show_CT_ROI, slice)
    
    return HU_ROI, counts_ROI

@pytest.mark.parametrize("new_sp,ROI_founded,show_CT_ROI,save_info_all,ID,resampler,slice",[([1,1,3],"GTV-1",True,False,"1",sitk.sitkNearestNeighbor,0)],)
def test_ROI_res(reference_CT_path:Path, reference_RT_path:Path, new_sp:np.array, ROI_founded:str, show_CT_ROI:bool, save_info_all:bool,
            reference_dir_out:Path, ID:str, resampler,slice:int)->Tuple[np.array,np.array]:
    """
    Function for obtaining ROIs and its distribution of HU
    in patients with different voxel spacing.

    :param ct_path: CT image path.
    :type ct_path: Path
    :param rt_path: RT Structure set path.
    :type rt_path: Path
    :param new_sp: new spacing.
    :type new_sp: np.array
    :param ROI_founded: ROI you are looking for.
    :type ROI_founded: str
    :param show_CT_ROI: flag used to show the CT slice.
    :type show_CT_ROI: bool
    :param save_info_all: save all the information.
    :type save_info_all: bool
    :param directory_out: path where to save output.
    :type directory_out: Path
    :param ID: patient's ID.
    :type ID: str
    :param slice: desired slice.
    :type slice: int
    
    :return: array of HU in the resampled ROI and array of HU relative counts of resampled ROI.
    :rtype: Tuple[np.array,np.array]
    """
    
    #CT and CT_arr
    CT, CT_arr = test_read_and_show_ct(reference_CT_path, show_CT_ROI, slice)
    
    #Resampling
    CT_res = test_resample(CT, new_sp[0], new_sp[1], new_sp[2],resampler)
    CT_res_arr=CT_res.numpy()

    #Get RTStructure Set
    rt_res=rsm.RTStructureSet.read(filename=reference_RT_path,structure_names=ROI_founded,reference_image=CT_res)
    
    #Get the mask
    mask_res = test_read_and_show_RTst(rt_res, ROI_founded)    
    
    #Get HU and counts for ROI
    HU_ROI_res, counts_ROI_res = test_obtain_ROI(mask_res, CT_res_arr, show_CT_ROI, slice)

    return HU_ROI_res, counts_ROI_res
 
@pytest.mark.parametrize("show_CT_ROI,slice",[(True,0)],)
def test_read_and_show_ct(reference_CT_path:Path, show_CT_ROI:bool, slice:int)->Tuple[rsm.Image,np.array]:
    """
    Take CT from ct_path and show the slice you want.

    :param ct_path: path of CT directory.
    :type ct_path: Path
    :param show_CT_ROI: selector for showing CT slice and ROI.
    :type show_CT_ROI: bool
    :param slice: input number for slice view.
    :type slice: int
    
    :return: CT image and CT array showable.
    :rtype: Tuple[rsm.Image,np.array]
    """
    
    #Read image
    ct=rsm.Image.read(reference_CT_path)
    
    #Get the CT array
    ct_arr = ct.numpy()
    print("The CT has a shape: ", ct_arr.shape)
    
    #Remove comments if you want to see the slice
    # if show_CT_ROI:
    #     plt.imshow(ct_arr[slice])
    #     plt.show()

    

    return ct, ct_arr

@pytest.mark.parametrize("ROI_founded",[("GTV-1")],)
def test_read_and_show_RTst(reference_RT:rsm.RTStructureSet, ROI_founded:str)->np.array:
    """
    This function relates to and shows the specific ROI founded for the CT.
    Because of significative value for 0 HU in CT, ROI of 0 and 1 is 
    converted in 1 and nan.

    :param rt_0: RTst image.
    :type rt_0: rsm.RTStructureSet
    :param ROI_founded: ROI you are looking for.
    :type ROI_founded: str

    :return: ROI's mask of 1 and nan instead of 1 and 0.
    :rtype: np.array
    """
    #Check the different ROIs
    print(f"ROI: {reference_RT.keys()}")
    
    roi_obj = None
    
    
    #Get the desired RTStructures
    for name_ROI in reference_RT.keys():
        if ROI_founded==name_ROI:
            print("Consider the ROI: ", name_ROI, ", coinciding with: ", ROI_founded)
            roi_obj = reference_RT[name_ROI]
            
            break
        else:
            print("I'm analyzing the ROI: ", name_ROI)
    
    
    rt = roi_obj
    
    #Convert in array  
    rt_arr = rt.numpy()
    print("The RTst has a shape: ", rt_arr.shape, " and contains: ", np.unique(rt_arr, return_counts=True)[1][1], " 1")

    #Get the mask
    mask = rt_arr.astype(float)
    mask[mask == 0] = np.nan
        
    return mask
    

@pytest.mark.parametrize("show_CT_ROI,slice",[(True,0)],)
def test_obtain_ROI(reference_mask:np.array, reference_CT_arr:np.array, show_CT_ROI:bool, slice:int)->Tuple[np.array,np.array]:
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

    :return: array of HU in the ROI and array of HU relative counts.
    :rtype: Tuple[np.array,np.array]
    """
    
    #Compute ct, HU, HU not NaN and counts not NaN for the desired ROI
    ct_ROI = reference_mask * reference_CT_arr
    HU_ROI, counts_ROI = np.unique(ct_ROI, return_counts=True)
    HU_ROI_no_nan=HU_ROI[np.where(~np.isnan(HU_ROI))[0]]
    counts_ROI_no_nan=counts_ROI[np.where(~np.isnan(HU_ROI))[0]]
    
    #Remove comments if you want the following prints
    # if show_CT_ROI:
        # print("The number of HU and counts in the ROI is: ", len(HU_ROI_no_nan), " and ", len(counts_ROI_no_nan))
        # print("starting CT in ROI has type: ", ct_ROI.shape)
        # print(HU_ROI_no_nan)
        # print(counts_ROI_no_nan)
        # plt.imshow(ct_ROI[slice])
        # plt.colorbar()
        # plt.show()
    

    return HU_ROI_no_nan, counts_ROI_no_nan

@pytest.mark.parametrize("new_x,new_y,new_z,resampler",[(1,1,3,sitk.sitkNearestNeighbor)],)
def test_resample(reference_CT: rsm.Image, new_x:float, new_y:float, new_z:float,resampler) -> rsm.Image:
    """
    Resample image (increase pixel density) in order to increase computation accuracy.

    :param image: image to be resampled.
    :type image: rsm.Image
    :param new_x: new_pixels for the x-axis.
    :type new_x: float
    :param new_y: new_pixels for the y-axis.
    :type new_y: float
    :param new_z: new_pixels for the z-axis.
    :type new_z: float


    :return: resampled image and array of the resampled image.
    :rtype: rsm.Image
    """   
    
    #Fill new_spacing
    new_spacing=np.array([new_x,new_y,new_z])
    
    #Check if all the dimensions are greater than 0
    orig_size=reference_CT.size
    for s in orig_size: 
        if s==0: 
            print("The image has one dimension equal to zero")

    new_image=rsm.Image.resample(reference_CT,new_spacing,resampler,0)
    
    return new_image
