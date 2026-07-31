"""
Test module for analyze_dcm.py 
"""

import os
from pathlib import Path
import pandas as pd
import re
import pytest
import pydicom
from datetime import datetime
from Densitometry.dcm_functions.analyze_dcm import find_ct_info



def assert_summary_dataframe_is_valid(df_py:pd.DataFrame):
    
    """ Check if all the columns of df_py are created correctly. """
    
    assert isinstance(df_py, pd.DataFrame)
    assert not df_py.empty
    
    cols=["PatientID","PatientName","PatientAge","VoxelSpacingX","VoxelSpacingY","VoxelSpacingZ","Path"]
    
    for c in cols:
        assert  c in df_py.columns

    


@pytest.mark.parametrize("imm_mod",["CT"])
def test_find_ct_info(patient_directory:Path,imm_mod:str,reference_py_patient_file:Path):
    
    """ Check if the py_patient file is created correctly. """
    
    df_py=find_ct_info(patient_directory,imm_mod,reference_py_patient_file)
    
    assert_summary_dataframe_is_valid(df_py)

    

        
def test_find_ct_info_create_excel(patient_directory:Path,tmp_path:Path):
    
    """ Test find_ct_info_create_excel when using an invalid path to the patient_file. """

    fake_excel = Path(tmp_path) / "patient_file.xlsx"

    df = find_ct_info(patient_directory,"CT",fake_excel)

    assert_summary_dataframe_is_valid(df)
    assert fake_excel.exists()


