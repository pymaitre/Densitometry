"""

Testing analyze_dcm module 

"""

import os
from pathlib import Path
import pandas as pd
import re
import pytest
import pydicom
from datetime import datetime
from Densitometry.dcm_functions.analyze_dcm import find_ct_info





@pytest.mark.parametrize("imm_mod",["CT"])
def test_find_ct_info(patient_directory:Path,imm_mod:str,reference_py_patient_file:Path):
    
    """ Test to verify if the py_patient file is created correctly. """
    
    df_py=find_ct_info(patient_directory,imm_mod,reference_py_patient_file)
    
    assert isinstance(df_py, pd.DataFrame)
    assert not df_py.empty
    assert "PatientID" in df_py.columns
    assert "PatientName" in df_py.columns
    assert "PatientAge" in df_py.columns
    assert "VoxelSpacingX" in df_py.columns
    assert "VoxelSpacingY" in df_py.columns
    assert "VoxelSpacingZ" in df_py.columns
    assert "Path" in df_py.columns

    

        
def test_find_ct_info_create_excel(patient_directory:Path,tmp_path:Path):
    
    """ Test to verify if the path of the patient_file is wrong or not valid for the function find_ct_info function. """

    fake_excel = Path(tmp_path) / "patient_file.xlsx"

    df = find_ct_info(patient_directory,"CT",fake_excel)

    assert isinstance(df, pd.DataFrame)
    assert fake_excel.exists()


