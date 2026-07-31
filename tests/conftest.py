"""
Fixtures used during testing
"""

import pytest
import os
import resmip as rsm
import numpy as np
import pandas as pd
import SimpleITK as sitk
from pathlib import Path
import yaml




@pytest.fixture
def patient_directory()->Path:
    """Path of the patient folder used for testing."""
    return Path(Path(__file__).parent.parent / "tutorials" / "tutorial_patient")


@pytest.fixture
def reference_dir_out()->Path:
    """Path to the directory_out used for tesing."""
    return Path(Path(__file__).parent/"output_test")


@pytest.fixture
def reference_py_patient_file()->Path:
    """Path to the py_patient file used for tesing."""
    return Path(Path(__file__).parent/"output_test"/"py_patient.xlsx")


@pytest.fixture
def reference_py_patient_file_dataset()->Path:
    """DataFrame of the py_patient file used for tesing."""
    return pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))


@pytest.fixture
def reference_folder_files_ok()->Path:
    """Path to the folder with the DataFrames that stores HU and counts of the patient (if resampling has been performed, it stores information after resampling)."""
    return (Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok")


@pytest.fixture
def reference_file_ok()->pd.DataFrame:
    """Dataframe with HU and counts of the patient (if resampling has been performed, it stores information after resampling)."""
    return pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")


@pytest.fixture
def reference_HU_ok()->pd.Series:
    """HU of reference_file_ok DataFrame."""
    file_ok=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")
    return file_ok["HU"]


@pytest.fixture
def reference_counts_ok()->pd.Series:
    """Counts of reference_file_ok DataFrame."""
    file_ok=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")
    return file_ok["Counts"]


@pytest.fixture
def reference_voxelspacingx()->pd.Series:
    """VoxelSpacingX of the original CT."""
    df_py=pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))
    return df_py["VoxelSpacingX"]
    
    
@pytest.fixture
def reference_dir_histo_ok()->Path:
    """Path to the Histo_ok folder."""
    return Path(Path(__file__).parent/"output_test"/ "Total_ROI" / "Histograms_ok")


@pytest.fixture
def reference_data()->np.array:
    """array used as data for testing."""
    file_ok=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")
    return np.repeat(file_ok["HU"],file_ok["Counts"])


@pytest.fixture
def reference_sp()->np.array:
    """array containing the original VoxelSpacing."""
    df_py=pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))
    x=df_py["VoxelSpacingX"]
    y=df_py["VoxelSpacingY"]
    z=df_py["VoxelSpacingZ"]
    return np.array([x, y, z], dtype=float)


@pytest.fixture
def reference_HU_no_res()->pd.Series:
    """HU of the patient before resampling."""
    file_no_res=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"To_be_resampled"/"Files"/"1.xlsx")
    return file_no_res["HU"]


@pytest.fixture
def reference_counts_no_res()->pd.Series:
    """Counts of the HU before resampling."""
    file_no_res=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"To_be_resampled"/"Files"/"1.xlsx")
    return file_no_res["Counts"]


@pytest.fixture
def reference_compare_dir()->Path:
    """Path where compare histogram plots are stored."""
    return Path(Path(__file__).parent/"output_test"/"Total_ROI"/"To_be_resampled"/"Compare_histo")


@pytest.fixture
def reference_CT_path()->Path:
    """Path to the patient CT folder."""
    return Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"CT"


@pytest.fixture
def reference_CT()->rsm.Image:
    """rsm.Image of the patient's CT used for testing."""
    return rsm.Image.read(Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"CT")


@pytest.fixture
def reference_CT_arr()->rsm.Image:
    """arry of the patient's CT used for testing."""
    ct=rsm.Image.read(Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"CT")
    return ct.numpy()


@pytest.fixture
def reference_RT_path()->Path:
    """Path to the patient's RTSTRUCT file."""
    return Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"Rtst"/"DCM_RS_00060.dcm"


@pytest.fixture
def reference_RT()->rsm.RTStructureSet:
    """rsm.RTStructureSet of the patient's RTSTRUCT used for testing."""
    reference_path_rt=Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"Rtst"/"DCM_RS_00060.dcm"
    reference_CT=rsm.Image.read(Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"CT")
    return rsm.RTStructureSet.read(filename=reference_path_rt,structure_names="GTV-1",reference_image=reference_CT)


@pytest.fixture
def reference_mask()->np.array:
    """Mask of the ROI used for testing."""
    reference_path_rt=Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"Rtst"/"DCM_RS_00060.dcm"
    reference_CT=rsm.Image.read(Path(__file__).parent.parent/"tutorials"/"tutorial_patient"/"IBSI1_CT_phantom"/"CT"/"CT_1"/"CT")
    reference_RT=rsm.RTStructureSet.read(filename=reference_path_rt,structure_names="GTV-1",reference_image=reference_CT)
    RT_sub=reference_RT["GTV-1"]
    RT_sub_numpy=RT_sub.numpy()
    return np.where(RT_sub_numpy == 0, np.nan, RT_sub_numpy).astype(float)


@pytest.fixture
def reference_dict_resampling()->dict:
    """Dictionary used as input for the function parallel_fun (applied during resampling)."""
    
    df_py=pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))

    dic={
        "directory_histo_fin": Path(Path(__file__).parent/"output_test"/ "Total_ROI" / "Histograms_ok"),
        "directory_files_fin": Path(Path(__file__).parent/"output_test"/ "Total_ROI" / "Files_ok"),
        "dataset": df_py,
        "ID_problems": [],
        "new_sp": np.array([1,1,3]),
        "rt_kind": "DCM_RS",
        "list_roi": ["GTV-1"],
        "directory_out": Path(Path(__file__).parent/"output_test"),
        "show_info_all": False,
        "save_info_all": False,
        "resampler": sitk.sitkNearestNeighbor}
    
    return dic


@pytest.fixture
def reference_dict_no_res()->dict:
    """Dictionary used as input for the function no_res_parallel_fun."""
    
    df_py=pd.read_excel(Path(Path(__file__).parent/"output_test"/"py_patient.xlsx"))

    dic={
        "directory_histo_fin": Path(Path(__file__).parent/"output_test"/"Total_ROI"/"Histograms_ok"),
        "directory_files_fin": Path(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"),
        "dataset": df_py,
        "ID_problems": [],
        "rt_kind": "DCM_RS",
        "list_roi": ["GTV-1"],
        "directory_out": Path(Path(__file__).parent/"output_test"),
        "show_info_all": False,
        "save_info_all": False,
}
    return dic


@pytest.fixture
def reference_conf_ROI_analyses():
    """conf file used in test_ROI_analyses"""
    config_path= Path(__file__).parent/ "test_conf" / "test_conf_ROI_analyses.yml"
       
    return yaml.safe_load(config_path.read_text())


@pytest.fixture
def reference_conf_total_ROI_analyses():
    """conf file used for test_total_ROI_analyses"""
    
    config_path= Path(__file__).parent/ "test_conf" / "test_conf_total_ROI.yml"
       
    return yaml.safe_load(config_path.read_text())


@pytest.fixture
def reference_dir_out_empty():
    """Path to an empty directory_out used during tests."""
    path=Path(Path(__file__).parent/"output_empty")
    
    yield path
    
    #Ensure that the folder has no files (only the subfolders Total_ROI and Files_ok are kept)
    for item in path.iterdir():
        if item.is_file():
            item.unlink()


@pytest.fixture
def reference_path_conf():
    """ Path to a configuration file used for testing."""
    return Path(Path(__file__).parent/"test_conf"/"test_conf_total_ROI.yml")


@pytest.fixture
def reference_pathout():
    """ Path to the folder where the configuration files used for testing are stored."""
    return Path(Path(__file__).parent/"test_conf")

