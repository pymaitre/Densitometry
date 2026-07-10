"""

Testing extract_histo module

"""

import os
import re
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from Densitometry.total_ROI_functions.extract_histo import features_ROI,make_histo,make_file,plot_stat,calculate_and_save_statistics,compare_histo_res,extract_hist
from scipy import stats
import pytest
import pandas as pd
import pytest


@pytest.mark.parametrize("ID,ROI_name,save",[("1","GTV-1",True),("1","GTV-1",False)],)
def test_features_ROI(ID:str, reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, reference_sp: np.array, ROI_name:str,
                 reference_dir_histo_ok:Path, reference_folder_files_ok:Path, save:bool):
    
    """ Test if features_ROI works correctly. """
    
    
    stats_df=features_ROI(ID,reference_HU_ok,reference_counts_ok,reference_sp,ROI_name,reference_dir_histo_ok,reference_folder_files_ok,save)

    assert isinstance(stats_df,pd.DataFrame)
    assert not len(stats_df)==0

@pytest.mark.parametrize("n_size,ROI_name,name,save",[(1,"GTV-1","1",True),(1,"GTV-1","1",False)])
def test_make_histo(reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, n_size:int, reference_sp:np.array, ROI_name:str, reference_dir_histo_ok:Path, name:str, save:bool):
    
    """ Test make_histo function, to check if it performs correctly. """
    
    HU, count, stats_df=make_histo(reference_HU_ok, reference_counts_ok, n_size, reference_sp, ROI_name, reference_dir_histo_ok, name, save)

    assert isinstance(HU,np.ndarray)
    assert isinstance(count,np.ndarray)
    assert isinstance(stats_df,pd.DataFrame)
    assert HU is not None
    assert count is not None
    assert stats_df is not None
    assert len(HU)==len(count)


@pytest.mark.parametrize("name,save",[("1",True),("1","False")],)
def test_make_file(reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, reference_folder_files_ok:Path, name:str, save:bool):
    
    """ Test make_file function. """
    
    
    df=make_file(reference_HU_ok,reference_counts_ok,reference_folder_files_ok,name,save)

    assert isinstance(df,pd.DataFrame)
    assert not len(df)==0


def test_plot_stat(reference_data:np.array):
    
    """ Test plot_stat function. """
    
    plot_stat(reference_data)
    
    

@pytest.mark.parametrize("histo_name,region,ROI_name",[("1","GTV-1","GTV-1")],)
def test_calculate_and_save_statistics(histo_name:str, region:str, reference_data:np.array, reference_sp: np.array, ROI_name:str):
    
    """ Test if calculate_and_save_statistics works correctly. """

    stats_data=calculate_and_save_statistics(histo_name,region,reference_data,reference_sp,ROI_name)
    assert isinstance(stats_data,pd.DataFrame)
    assert not len(stats_data)==0
    assert "PatientID" in stats_data.columns
    assert "ROI_name" in stats_data.columns
    assert "VoxelSpacingX" in stats_data.columns
    assert "VoxelSpacingY" in stats_data.columns
    assert "VoxelSpacingZ" in stats_data.columns
    assert f"Tot_counts_{region}" in stats_data.columns
    assert f"Volume_mm3_{region}" in stats_data.columns
    assert f"Volume_cc_{region}" in stats_data.columns
    assert f"Min_{region}" in stats_data.columns
    assert f"Max_{region}" in stats_data.columns
    assert f"Mean_{region}" in stats_data.columns
    assert f"Mode_{region}" in stats_data.columns
    assert f"Count_Max_{region}" in stats_data.columns
    assert f"Median_{region}" in stats_data.columns
    assert f"Std Dev_{region}" in stats_data.columns
    assert f"Skewness_{region}" in stats_data.columns
    assert f"Kurtosis_{region}" in stats_data.columns
    assert f"10th Percentile_{region}" in stats_data.columns
    assert f"25th Percentile_{region}" in stats_data.columns
    assert f"75th Percentile_{region}" in stats_data.columns
    assert f"90th Percentile_{region}" in stats_data.columns
    assert f"95th Percentile_{region}" in stats_data.columns
    
    

@pytest.mark.parametrize("ID,save",[("1",True),("1",False)],)
def test_compare_histo_res(reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, reference_HU_no_res:pd.Series, reference_counts_no_res:pd.Series, reference_compare_dir:Path, ID:str, save): 
    
    """ Test if compare_histo_res runs correctly. """

    compare_histo_res(reference_HU_ok,reference_counts_ok,reference_HU_no_res,reference_counts_no_res,reference_compare_dir,ID,save)

@pytest.mark.parametrize("n_size,color,label",[(1,"b","Histo_CT_res")],)
def test_extract_hist(reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, n_size:int, color:str, label:str):
    
    """ Test for extract_hist function. """
    extract_hist(reference_HU_ok,reference_counts_ok,n_size,color,label)
    