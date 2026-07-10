"""

Testing justified module

"""

import os
import re
import pytest
from Densitometry.total_ROI_functions import extract_histo as histo
from Densitometry.specific_ROI_functions.justified import just_variable,justified,histo_just
from pathlib import Path
import pandas as pd
import numpy as np



def test_just_variable(monkeypatch):
    
    """ Test the function just_variable. """
    
    inputs = iter(["100", "500", "0"])

    monkeypatch.setattr("builtins.input",lambda _: next(inputs))

    HU_min,HU_max,min_counts=just_variable()

    assert (HU_min, HU_max, min_counts) == (100, 500, 0)

@pytest.mark.parametrize("HU_min,HU_max,min_counts",[(100,500,0)])
def test_justified(reference_HU_ok: pd.Series, reference_counts_ok: pd.Series, HU_min:int , HU_max: int, min_counts:int):
    
    """ Test to verify if analyze_rate runs correctly. """
    
    HU_just, counts_just=justified(reference_HU_ok,reference_counts_ok,HU_min,HU_max,min_counts)

    assert isinstance(HU_just, pd.Series)
    assert isinstance(counts_just, pd.Series)
    assert len(HU_just)==len(counts_just)
    assert all(HU_just>=HU_min)
    assert all(HU_just<=HU_max)
    assert all(counts_just>=min_counts)
    assert HU_just is not None
    assert counts_just is not None

    
@pytest.mark.parametrize("delimiter",[([100,500,0])])
def test_histo_just(reference_folder_files_ok: str, reference_dir_out: str, delimiter: tuple[int,int,int]):
    """ Test to verify if histo_just runs correctly. """
    histo_just(reference_folder_files_ok,reference_dir_out,delimiter)

    