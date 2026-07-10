"""

Testing total module

"""

import os
from pathlib import Path
from Densitometry.total_ROI_functions.total import get_roi_names,is_roi_empty,find_rt_st,parallel_fun,res_and_create_histo,no_res_parallel_fun,no_res_and_create_histo
import SimpleITK as sitk
import pandas as pd
import pydicom
from joblib import Parallel, delayed
import numpy as np
import pytest
import gc
import matplotlib
matplotlib.use("Agg")


def test_get_roi_names(reference_RT_path:Path):
    
    """ Test if get_roi_names runs correctly. """
    
    roi_names=get_roi_names(reference_RT_path)

    assert isinstance(roi_names,list)
    assert not len(roi_names)==0

@pytest.mark.parametrize("roi_name",["GTV-1"])
def test_is_roi_empty(reference_RT_path:Path, roi_name:str):
    
    """ Test if is_roi_empty checks correctly the ROI. """
    
    flag=is_roi_empty(reference_RT_path,roi_name)

    assert isinstance(flag,bool)
    

def test_is_roi_empty_not_valid_roi(reference_RT_path:Path):
    
    """ Test if is_roi_empty raises error if missing ROI is required. """
    
    roi_name="Heart"
    
    with pytest.raises(ValueError, match="not found"):
        flag=is_roi_empty(reference_RT_path,roi_name)



    
@pytest.mark.parametrize("rt_kind,list_roi",[("DCM_RS",["GTV-1"]),("DCM_RS",["Heart"])])
def test_find_rt_st(reference_CT:Path, rt_kind:str, list_roi:list):
    
    """ Test if find_rt_st works correctly. """

    result =find_rt_st(reference_CT,rt_kind,list_roi)
    
    if result is not None:
        ROI_name, path_rt_st = result
    else:
        ROI_name = None
        path_rt_st = None
        
    assert isinstance(ROI_name,str) or ROI_name is None
    assert isinstance(path_rt_st,Path) or path_rt_st is None
    
    if path_rt_st is not None:
        assert path_rt_st.exists()
        


@pytest.mark.parametrize("pz",[0])
def test_parallel_fun(pz:int, reference_dict_resampling:dict):
    
    """ Test if parallel_fun works correctly. """
    
    
    df,ID_list=parallel_fun(pz,reference_dict_resampling)
    
    assert isinstance(df,pd.DataFrame) or df is None
    assert isinstance(ID_list,list) or ID_list is None
    
    

def test_parallel_fun_not_valid_pz(reference_dict_resampling:dict):
    
    """ Test if parallel_fun works raises Error if pz is not valid. """
    
    pz=1
    
    with pytest.raises(ValueError):
        df,ID_list=parallel_fun(pz,reference_dict_resampling)
        
@pytest.mark.parametrize("pz",[0])    
def test_parallel_fun_old_sp(pz:int,reference_dict_resampling:dict,reference_py_patient_file_dataset:pd.DataFrame):
    
    """ Test if parallel_fun works using old_sp. """
    
    x=reference_py_patient_file_dataset.loc[pz,"VoxelSpacingX"]
    y=reference_py_patient_file_dataset.loc[pz,"VoxelSpacingY"]
    z=reference_py_patient_file_dataset.loc[pz,"VoxelSpacingZ"]
    
    sp=np.array([x,y,z])
    reference_dict_resampling["new_sp"]=sp


    df,ID_list=parallel_fun(pz,reference_dict_resampling)
    assert isinstance(df,pd.DataFrame) or df is None
    assert isinstance(ID_list,list) or ID_list is None
    
    
@pytest.mark.parametrize("pz",[0])    
def test_parallel_fun_mising_roi(pz:int,reference_dict_resampling:dict):
    
    """ Test if parallel_fun raises Exception when missing ROI is considered. """


    reference_dict_resampling["list_roi"]=["Heart"]


    df,ID_list=parallel_fun(pz,reference_dict_resampling)
    assert df is None
    assert isinstance(ID_list,list)
    

@pytest.mark.parametrize("pz",[0])    
def test_parallel_fun_ID_problem(pz:int,reference_dict_resampling:dict):
    
    """ Test if parallel_fun detects correctly ID_problems. """


    reference_dict_resampling["ID_problems"]=["1"]


    df,ID_list=parallel_fun(pz,reference_dict_resampling)
    assert df is None
    assert isinstance(ID_list,list)
   


@pytest.mark.parametrize("ID_problems,new_sp,rt_kind,list_roi,show_info_all,save_info_all,N_jobs,resampler",[([],[1,1,3],"DCM_RS",["GTV-1"],True,True,2,sitk.sitkBSpline),
                                                                                                             ([],[1,1,3],"DCM_RS",["GTV-1"],True,False,2,sitk.sitkBSpline),
                                                                                                             ([],[1,1,3],"DCM_RS",["GTV-1"],False,True,2,sitk.sitkBSpline),
                                                                                                             ([],[1,1,3],"DCM_RS",["GTV-1"],False,False,2,sitk.sitkBSpline),(["1"],[1,1,3],"DCM_RS",["GTV-1"],False,False,2,sitk.sitkBSpline)])
def test_res_and_create_histo(reference_py_patient_file_dataset:pd.DataFrame, ID_problems:list, new_sp:np.array, rt_kind:str, list_roi:list, 
                         reference_dir_out:Path, show_info_all:bool, save_info_all:bool,N_jobs:int,resampler):
    
    """ Test if res_and_create_histo works correctly. """

    dir_files_fin=res_and_create_histo(reference_py_patient_file_dataset,ID_problems,new_sp,rt_kind,list_roi,reference_dir_out,show_info_all,save_info_all,N_jobs,resampler)

    assert isinstance(dir_files_fin,Path)
    assert dir_files_fin.exists()
    
    


@pytest.mark.parametrize("pz",[0])
def test_no_res_parallel_fun(pz:int, reference_dict_no_res:dict):
    
    """ Test if no_res_parallel_fun works correctly. """
    
    df,ID_list=no_res_parallel_fun(pz,reference_dict_no_res)
    
    assert isinstance(df,pd.DataFrame) or df is None
    assert isinstance(ID_list,list) or ID_list is None
    

@pytest.mark.parametrize("pz",[0])    
def test_no_res_parallel_fun_mising_roi(pz:int,reference_dict_no_res:dict):
    
    """ Test if no_res_parallel_fun raises Exception when missing ROI is considered. """


    reference_dict_no_res["list_roi"]=["Heart"]


    df,ID_list=no_res_parallel_fun(pz,reference_dict_no_res)
    assert df is None
    assert isinstance(ID_list,list)

    
def test_no_res_parallel_fun_not_valid_pz(reference_dict_no_res:dict):
    
    """ Test if no_res_parallel_fun works raises Error if pz is not valid. """
    
    pz=1
    
    with pytest.raises(ValueError):
        df,ID_list=no_res_parallel_fun(pz,reference_dict_no_res)


@pytest.mark.parametrize("pz",[0])    
def test_no_res_parallel_fun_ID_problem(pz:int,reference_dict_no_res:dict):
    
    """ Test if no_res_parallel_fun detects correctly ID_problems. """


    reference_dict_no_res["ID_problems"]=["1"]


    df,ID_list=no_res_parallel_fun(pz,reference_dict_no_res)
    assert df is None
    assert isinstance(ID_list,list)
    

   
@pytest.mark.parametrize("ID_problems,rt_kind,list_roi,show_info_all,save_info_all,N_jobs",[([],"DCM_RS",["GTV-1"],True,True,2),([],"DCM_RS",["GTV-1"],True,False,2),
                                                                                            ([],"DCM_RS",["GTV-1"],False,True,2),([],"DCM_RS",["GTV-1"],False,False,2),
                                                                                            (["1"],"DCM_RS",["GTV-1"],True,True,2)])
def test_no_res_and_create_histo(reference_py_patient_file_dataset:pd.DataFrame, ID_problems:list, rt_kind:str, list_roi:list, 
                         reference_dir_out:Path, show_info_all:bool, save_info_all:bool,N_jobs:int):
    
    """ Test if no_res_and_create_histo works correctly. """

        
    dir_files_fin=no_res_and_create_histo(reference_py_patient_file_dataset,ID_problems,rt_kind,list_roi,reference_dir_out,show_info_all,save_info_all,N_jobs)

    assert isinstance(dir_files_fin,Path)
    assert dir_files_fin.exists()