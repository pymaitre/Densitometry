"""

Testing other_function module

"""


import os
import pytest
from Densitometry.other_functions import rtv_configuration_file
import yaml
from pathlib import Path

@pytest.mark.parametrize("save",[(True),(False)])
def test_rtv_configuration_file(reference_path_conf:Path, save: bool, reference_pathout:str)->dict:
    
    """ Test if rtv_configuration_file works correctly. """
    
    name_conf="test_conf.yml"
    
    dictionary=rtv_configuration_file(name_conf,reference_path_conf,save,reference_pathout)
    assert isinstance(dictionary,dict)
    assert dictionary is not None