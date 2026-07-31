"""
Test module for total_ROI_analyses.py
"""

import matplotlib
matplotlib.use("Agg")
import time
import SimpleITK as sitk
from pathlib import Path
import numpy as np
import pytest
import os
import sys
import argparse
import yaml
from Densitometry.other_functions import rtv_configuration_file
from Densitometry.dcm_functions import analyze_dcm as info_dcm
from Densitometry.total_ROI_functions import analyze_spacing as sp
from Densitometry.total_ROI_functions import analyze_ROI as ROI
from Densitometry.total_ROI_functions import total as tot
from Densitometry.main_scripts.total_ROI_analyses import main



def test_main(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Test the main function of total_ROI_analyses. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)

    main(reference_conf_total_ROI_analyses)
    


def test_main_no_dcm(reference_conf_total_ROI_analyses:dict,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Do not provide directory_dcm_out. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=None
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)



def test_main_no_dir_out(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_py_patient_file:Path):
    
    """ Do not provide directory_out. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=None
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
  
        

def test_main_no_py(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path):
    
    """ Do not provide py_patient_path. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=None

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        


def test_main_flag_parallel_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Provide an invalid flag_parallel. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_parallel"]="Yes"

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        


def test_main_N_jobs_small(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Provide N_jobs=0. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["N_jobs"]=0

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        
        
        
def test_main_N_jobs_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Provide an invalid value for N_jobs. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["N_jobs"]=0.5

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)


def test_main_sequential(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Check if sequential approches is chosen. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_parallel"]=False

    
    main(reference_conf_total_ROI_analyses)



def test_main_flag_resampling_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Provide invalid flag_resampling. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_resampling"]="Yes"

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        

def test_main_save_ROI_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Provide invalid save_ROI. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["save_ROI_info"]="Yes"

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)



def test_main_save_ROI_false(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Set save_ROI equal to False. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["save_ROI_info"]=False

    
    main(reference_conf_total_ROI_analyses)
 
 
        
def test_main_empty_list_roi(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Test when lis_roi is empty. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["list_roi"]=[]

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)



def test_main_total_ROI_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Test when total_ROI_analyses is not valid. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["total_ROI_analyses"]="Yes"

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
   
   
        
def test_main_show_info_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Test when show_total_ROI_info is not valid. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["show_total_ROI_info"]="Yes"

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)



def test_main_save_info_not_valid(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path):
    
    """ Test when save_total_ROI_info is not valid. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["save_total_ROI_info"]="Yes"

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)




@pytest.mark.parametrize("flag_res,flag_tot",[(False,True),(False,False)])
def test_main_no_res(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path,flag_res:bool,flag_tot:bool):
    
    """ Choose to not perform resampling. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_resampling"]=flag_res
    reference_conf_total_ROI_analyses["total_ROI_analyses"]=flag_tot


    main(reference_conf_total_ROI_analyses)
    

@pytest.mark.parametrize("flag_res,flag_tot",[(True,True),(True,False)])
def test_main_res(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path,flag_res:bool,flag_tot:bool):
    
    """ Choose to perform resampling. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_resampling"]=flag_res
    reference_conf_total_ROI_analyses["total_ROI_analyses"]=flag_tot


    main(reference_conf_total_ROI_analyses)



@pytest.mark.parametrize("flag",["min_global","max_global","mean_global","frequency","manual"])
def test_main_resample_new_space(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path,flag:str):
    
    """ Consider the different resampling approaches. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_resampling"]=True
    reference_conf_total_ROI_analyses["flag_new_spacing"]=flag

    main(reference_conf_total_ROI_analyses)


@pytest.mark.parametrize("flag",["median"])
def test_main_not_valid_new_sp(reference_conf_total_ROI_analyses:dict,patient_directory:Path,reference_dir_out:Path,reference_py_patient_file:Path,flag:str):
    
    """ Verify the behavior when flag_new_spacing is not valid. """
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["flag_resampling"]=True
    reference_conf_total_ROI_analyses["flag_new_spacing"]=flag

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)