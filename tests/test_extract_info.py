"""
Test for extract_info.py
"""

import os
from pathlib import Path
from typing import Tuple
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from Densitometry.total_ROI_functions.extract_info import save_info_nifti, ROI_ok, ROI_res, read_and_show_ct, read_and_show_RTst, obtain_ROI,resample
import resmip as rsm
import matplotlib
import pytest
matplotlib.use("Agg")


@pytest.mark.parametrize("save_info_all,ID,ROI_name",[(True,"1","GTV-1"),(False,"1","GTV-1")])
def test_save_info_nifti(save_info_all:bool, reference_dir_out:Path, reference_CT:rsm.Image, reference_RT:rsm.RTStructureSet,ROI_name:str,ID:str):
   
   """ Check if the image is saved in NIFTI format. """
   
   save_info_nifti(save_info_all,reference_dir_out,reference_CT,reference_RT,ROI_name,ID)


 
@pytest.mark.parametrize("save_info_all,ID,ROI_name",[(True,"1","GTV-1"),(False,"1","GTV-1")])
def test_save_info_nifti_no_CT(save_info_all:bool, reference_dir_out:Path,reference_RT:rsm.RTStructureSet,ROI_name:str,ID:str):
    
    """ Test if no CT image is provided. """
    
    CT=None
    save_info_nifti(save_info_all,reference_dir_out,CT,reference_RT,ROI_name,ID)
            
 
 
            
@pytest.mark.parametrize("ROI_founded,show_CT_ROI,slice",[("GTV-1",True,0),("GTV-1",False,0)])
def test_ROI_ok(reference_CT_path:Path, reference_RT_path:Path, ROI_founded:str, show_CT_ROI:bool, slice:int)->Tuple[np.array,np.array]:
    
    """ Obtain the HU distribution of the given ROI. """
    
    HU_ROI, counts_ROI = ROI_ok(reference_CT_path,reference_RT_path,ROI_founded,show_CT_ROI,slice)
    
    assert isinstance(HU_ROI,np.ndarray)
    assert isinstance(counts_ROI,np.ndarray)
    assert len(HU_ROI)==len(counts_ROI)
    assert HU_ROI is not None
    assert counts_ROI is not None



@pytest.mark.parametrize("new_sp,ROI_founded,show_CT_ROI,resampler,slice",[([1,1,3],"GTV-1",True,sitk.sitkBSpline,0),([1,1,3],"GTV-1",False,sitk.sitkBSpline,0)])
def test_ROI_res(reference_CT_path:Path, reference_RT_path:Path, new_sp:np.array, ROI_founded:str, show_CT_ROI:bool,resampler,slice:int):
    
    """ Obtain the HU distribution of the given ROI after resampling. """
    
    HU_ROI_res, counts_ROI_res=ROI_res(reference_CT_path,reference_RT_path,new_sp,ROI_founded,show_CT_ROI,resampler,slice)
    
    assert isinstance(HU_ROI_res,np.ndarray)
    assert isinstance(counts_ROI_res,np.ndarray)
    assert len(HU_ROI_res)==len(counts_ROI_res)
    assert HU_ROI_res is not None
    assert counts_ROI_res is not None
 
 
 
@pytest.mark.parametrize("show_CT_ROI,slice",[(True,0),(False,0)])
def test_read_and_show_ct(reference_CT_path:Path, show_CT_ROI:bool, slice:int):
    
    """ Verify if the CT is extracted. """
    
    ct, ct_arr=read_and_show_ct(reference_CT_path,show_CT_ROI,slice)
    
    assert isinstance(ct,rsm.Image)
    assert isinstance(ct_arr,np.ndarray)
    assert ct is not None
    assert ct_arr is not None



@pytest.mark.parametrize("ROI_founded",[("GTV-1")])
def test_read_and_show_RTst(reference_RT:rsm.RTStructureSet, ROI_founded:str):
    
    """ Verify if the RTSTRUCT is extracted. """
    
    mask=read_and_show_RTst(reference_RT,ROI_founded)
    
    assert isinstance(mask,np.ndarray)
    assert mask is not None
    

@pytest.mark.parametrize("show_CT_ROI,slice",[(True,0),(False,0)])
def test_obtain_ROI(reference_mask:np.array, reference_CT_arr:np.array, show_CT_ROI:bool, slice:int):
    
    """ Test if obtain_ROI behaves correctly. """
    
    HU_ROI_no_nan, counts_ROI_no_nan=obtain_ROI(reference_mask,reference_CT_arr,show_CT_ROI,slice)
    assert isinstance(HU_ROI_no_nan,np.ndarray)
    assert isinstance(counts_ROI_no_nan,np.ndarray)
    assert HU_ROI_no_nan is not None
    assert counts_ROI_no_nan is not None
    assert len(HU_ROI_no_nan)==len(counts_ROI_no_nan)



@pytest.mark.parametrize("new_x,new_y,new_z,resampler",[(1,1,3,sitk.sitkBSpline)])
def test_resample(reference_CT: rsm.Image, new_x:float, new_y:float, new_z:float,resampler):
    
    """ Resample a CT image. """   
    
    new_image=resample(reference_CT,new_x,new_y,new_z,resampler)
    
    assert isinstance(new_image,rsm.Image)
    assert new_image is not None



