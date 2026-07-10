"""

Testing analyze_spacing module

"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import pytest
from Densitometry.total_ROI_functions.analyze_spacing import read_spacing,histo_spacing,find_global_scale
import matplotlib.pyplot as plt


@pytest.mark.parametrize("save_sp",[True])
def test_read_spacing(reference_py_patient_file_dataset:pd.DataFrame, reference_dir_out:Path,save_sp: bool):
    
    """ Test if read_spacing works correctly. """
    
    
    new_x,new_y,new_z=read_spacing(reference_py_patient_file_dataset,reference_dir_out,save_sp)

    assert new_x is not None
    assert new_x>0
    assert new_y>0
    assert new_z>0
    
@pytest.mark.parametrize("name, n_size, save_sp",[("X", 0.01, True)])
def test_histo_spacing(reference_voxelspacingx: pd.Series, reference_dir_out: Path, name: str, n_size: float, save_sp: bool):
    
    """ Test if histo_spacing runs correctly. """
  
    co_mas_in=histo_spacing(reference_voxelspacingx,reference_dir_out,name,n_size,save_sp)
    
    assert isinstance(co_mas_in,float)
    assert co_mas_in is not None

    
@pytest.mark.parametrize("new_spacing_approach",["min_global","max_global","mean_global"])
def test_find_global_scale(reference_py_patient_file_dataset: pd.DataFrame,new_spacing_approach:str):
    
    """ Test if find_global_scale works correctly. """
    
    new_sp=find_global_scale(reference_py_patient_file_dataset,new_spacing_approach)
    
    assert isinstance(new_sp,np.ndarray)
    assert new_sp is not None
    assert len(new_sp)==3
    assert new_sp[0]>0
    assert new_sp[1]>0
    assert new_sp[2]>0


@pytest.mark.parametrize("new_spacing_approach",["median"])
def test_not_valid_scale(reference_py_patient_file_dataset: pd.DataFrame,new_spacing_approach:str):
    
    """ Test if find_global_scale works correctly. """
    
    with pytest.raises(ValueError):
        new_sp=find_global_scale(reference_py_patient_file_dataset,new_spacing_approach)
    

    
    
    
    