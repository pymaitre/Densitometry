"""
Test module for ROI_analyses.py
"""


from pathlib import Path
import os
import sys
import argparse
import yaml
import pytest
from Densitometry.other_functions import rtv_configuration_file
from Densitometry.specific_ROI_functions import justified as just
from Densitometry.specific_ROI_functions import check_over as over
from Densitometry.specific_ROI_functions import check_rate as rate
from Densitometry.main_scripts.ROI_analyses import main,analysis_check
from utils_for_testing import modify_configuration_file
from typing import Any

@pytest.mark.parametrize("specific_flag,over_flag,rate_flag,expected",[(None,False,True,(False,False,True)),
                                                                       (True,None,True,(True,False,True)),
                                                                       (True,False,None,(True,False,False)),
                                                                       ("Yes",False,True,(False,False,True)),
                                                                       (True,"No",True,(True,False,True)),
                                                                       (True,False,"Yes",(True,False,False))]) 
def test_analysis_check(reference_conf_ROI_analyses:dict,specific_flag:Any,over_flag:Any,rate_flag:Any,expected:tuple):
    """ Check if analysis_check function correctly modifies if a flag is None or not a boolean."""
    
    ref_conf=modify_configuration_file(reference_conf_ROI_analyses,["specific_ROI_analyses","over_ROI_analyses","rate_ROI_analyses"],[specific_flag,over_flag,rate_flag])
    conf=analysis_check(ref_conf)
    
    assert isinstance(conf["specific_ROI_analyses"], bool)
    assert isinstance(conf["over_ROI_analyses"], bool)
    assert isinstance(conf["rate_ROI_analyses"], bool)
    assert conf["specific_ROI_analyses"]==expected[0]
    assert conf["over_ROI_analyses"]==expected[1]
    assert conf["rate_ROI_analyses"]==expected[2]


def test_analysis_check_no_analyses(reference_conf_ROI_analyses:dict):
    """ Check if the function raises ValueError when no analysis has been selected."""
    
    
    ref_conf=modify_configuration_file(reference_conf_ROI_analyses,["specific_ROI_analyses","over_ROI_analyses","rate_ROI_analyses"],[False,False,False])
    
    with pytest.raises(ValueError):
        conf=analysis_check(ref_conf)

@pytest.mark.parametrize("specific_flag,over_flag,rate_flag,delimiter_specific,delimiter_rate",[(True,False,False,[100,-100,0],[-100,100,0]),(False,False,True,[-100,100,0],[100,-100,0])]) 
def test_analysis_check_invalid_delimiters(reference_conf_ROI_analyses:dict,specific_flag:bool,over_flag:bool,rate_flag:bool,delimiter_specific:list,delimiter_rate:list):
    
    """ Check if the function raises ValueError when invalid delimiters are provided."""
    
    ref_conf=modify_configuration_file(reference_conf_ROI_analyses,["specific_ROI_analyses","over_ROI_analyses","rate_ROI_analyses","specific_ROI_delimiter","rate_ROI_delimiter"],[specific_flag,over_flag,rate_flag,delimiter_specific,delimiter_rate])
    with pytest.raises(ValueError):
        conf=analysis_check(ref_conf)


def test_main(reference_conf_ROI_analyses:dict, reference_dir_out:Path):
    
    """ Test the main function of ROI_analysis. """
    
    reference_conf=modify_configuration_file(reference_conf_ROI_analyses,"directory_out",reference_dir_out)

    main(reference_conf)
    

def test_main_no_dir_out(reference_conf_ROI_analyses:dict):
    
    """ Do not provide directory_out in the configuration file. """

    reference_conf=modify_configuration_file(reference_conf_ROI_analyses,"directory_out",None)        

    with pytest.raises(ValueError):
        main(reference_conf)
        
                
def test_main_empty_dir_files_fin(reference_conf_ROI_analyses:Path,reference_dir_out_empty:Path):
    
    """ Provide an empty directory_out. """
    
    conf=modify_configuration_file(reference_conf_ROI_analyses,"directory_out",reference_dir_out_empty) 
    main(conf)