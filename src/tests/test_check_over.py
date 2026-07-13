"""
Test module for check_over.py
"""

import os
import re
from Densitometry.total_ROI_functions import extract_histo as histo
from Densitometry.specific_ROI_functions.check_over import over_variable, over_HU_counts, check_over
from pathlib import Path
import numpy as np
import pytest
import pandas as pd



def test_over_variable(monkeypatch):
    
    """ Check if the function over_variable behaves correctly. """
    
    inputs = iter(["0", "10"])

    monkeypatch.setattr("builtins.input",lambda _: next(inputs))

    HU_min, min_counts = over_variable()

    assert (HU_min, min_counts) == (0, 10)

    
@pytest.mark.parametrize("HU_min,min_counts",[(0,10)])
def test_over_HU_counts(reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, HU_min:int, min_counts:int):
    
    """ Verify if the outcome of over ROI analysis is valid. """
    
    HU_over,counts_over=over_HU_counts(reference_HU_ok,reference_counts_ok,HU_min,min_counts)
    assert isinstance(HU_over, pd.Series)
    assert isinstance(counts_over, pd.Series)
    assert len(HU_over)==len(counts_over)
    assert all(HU_over>=HU_min)
    assert all(counts_over>=min_counts)
    assert HU_over is not None
    assert counts_over is not None

@pytest.mark.parametrize("delimiter_over_ROI",[[0,10]])
def test_check_over(reference_folder_files_ok:Path, reference_dir_out:Path, delimiter_over_ROI:tuple[int,int]):
    
    """ Perform an over ROI analysis."""
    
    check_over(reference_folder_files_ok,reference_dir_out,delimiter_over_ROI)