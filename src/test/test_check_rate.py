"""

Testing check_rate module

"""

import os
import re
from pathlib import Path
import numpy as np
import pytest
from Densitometry.specific_ROI_functions.check_rate import rate_variable,analyze_rate,check_rate
import pandas as pd



def test_rate_variable(monkeypatch):
    
    """ Test the function rate_variable. """
    
    inputs = iter(["0", "100","2.5"])

    monkeypatch.setattr("builtins.input",lambda _: next(inputs))

    HU_min, HU_max, rate= rate_variable()

    assert (HU_min, HU_max,rate) == (0, 100,2.5)


@pytest.mark.parametrize("HU_min,HU_max",[(0,100)])
def test_analyze_rate(reference_HU_ok:pd.Series, reference_counts_ok:pd.Series, HU_min:int, HU_max:int):
   
    """ Test to verify if analyze_rate runs correctly.  """
    
    
    diff,HU_rate,counts_rate=analyze_rate(reference_HU_ok,reference_counts_ok,HU_min,HU_max)
    
    assert isinstance(HU_rate, pd.Series)
    assert isinstance(counts_rate, pd.Series)
    assert isinstance(diff,float)
    assert len(HU_rate)==len(counts_rate)
    assert diff is not None
    assert HU_rate is not None
    assert counts_rate is not None

    
@pytest.mark.parametrize("rate_over_ROI",[([0,100,2.5])])
def test_check_rate(reference_folder_files_ok:Path, reference_dir_out:Path, rate_over_ROI:tuple[int,int,float]):
    
    """ Test to verify if check_rate runs correctly. """
    
    check_rate(reference_folder_files_ok,reference_dir_out,rate_over_ROI)