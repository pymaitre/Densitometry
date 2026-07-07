"""

Fixtures for testing

"""

import pytest
import resmip
import numpy as np
import pandas as pd
from pathlib import Path



@pytest.fixture
def patient_directory()->Path:
    """Path of the patient folder used for testing."""
    return Path(Path(__file__).parent.parent.parent / "tutorials" / "tutorial_patient")


@pytest.fixture
def reference_dir_out()->Path:
    """Path to the directory out used for tesing."""
    return Path(Path(__file__).parent/"output_test")

@pytest.fixture
def reference_py_patient_file()->Path:
    """Path to the py_patient.xlsx file used for tesing."""
    return Path(Path(__file__).parent/"output_test"/"py_patient.xlsx")

@pytest.fixture
def reference_py_patient_file_dataset()->Path:
    """DataFrame py_patient.xlsx used for tesing."""
    return pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))

@pytest.fixture
def reference_folder_files_ok()->Path:
    """Path to the folder with the DataFrames that stores HU and counts (if resampling has been performed, it stores information after resampling)"""
    return (Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok")

@pytest.fixture
def reference_file_ok()->pd.DataFrame:
    """Dataframe with HU and counts (if resampling has been performed, it stores information after resampling)"""
    return pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")

@pytest.fixture
def reference_HU_ok()->pd.Series:
    """HU of reference_file_ok DataFrame"""
    file_ok=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")
    return file_ok["HU"]

@pytest.fixture
def reference_counts_ok()->pd.Series:
    """Counts of reference_file_ok DataFrame"""
    file_ok=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")
    return file_ok["Counts"]

@pytest.fixture
def reference_voxelspacingx()->pd.Series:
    df_py=pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))
    return df_py["VoxelSpacingX"]
    
    
    


    



