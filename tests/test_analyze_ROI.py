"""
Test module for analyze_ROI.py
"""

import os
import pytest
from pathlib import Path
from Densitometry.total_ROI_functions import extract_info as info
from Densitometry.total_ROI_functions.analyze_ROI import all_ROI
import matplotlib.pyplot as plt
import pandas as pd
import pydicom


def assert_all_ROI_dataframes_is_valid(df_ROI:pd.DataFrame,df_counts:pd.DataFrame):
    
    """ Check if df_ROI and df_counts are valid. """
    
    assert isinstance(df_ROI,pd.DataFrame)
    assert isinstance(df_counts,pd.DataFrame)
    assert not len(df_ROI)==0
    assert not len(df_counts)==0
    assert "Counts" in df_counts.columns
    assert "count" in df_counts.columns


@pytest.mark.parametrize("ID_problems, rt_kind",[([],"DCM_RS")])
def test_all_ROI(reference_py_patient_file_dataset:pd.DataFrame, ID_problems:list, reference_dir_out:Path, rt_kind:str):
    
    """ Check if the dataframe with all the patient's ROIs is created. """
    
    df_ROI, df_counts=all_ROI(reference_py_patient_file_dataset,ID_problems,reference_dir_out,rt_kind)
    
    assert_all_ROI_dataframes_is_valid(df_ROI,df_counts)

    



@pytest.mark.parametrize("ID_problems, rt_kind",[([],"DCM_RS")])
def test_all_ROI_exception(reference_py_patient_file_dataset:pd.DataFrame,reference_dir_out_empty:Path,ID_problems:list, rt_kind:str):
    
    """ Test the behavior of the function all_ROI when you provide an empty directory_out. """
    
    
    df_ROI, df_counts=all_ROI(reference_py_patient_file_dataset,ID_problems,reference_dir_out_empty,rt_kind)
    
    assert_all_ROI_dataframes_is_valid(df_ROI,df_counts)