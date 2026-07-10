"""

Testing ROI_analyses

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
from Densitometry.main_scripts.ROI_analyses import main

def test_main(reference_conf_ROI_analyses:dict, reference_dir_out:Path):
    
    """ Test if the main ROI_analysis runs correctly. """

    reference_conf_ROI_analyses["directory_out"] = reference_dir_out

    main(reference_conf_ROI_analyses)
    


def test_main_no_dir_out(reference_conf_ROI_analyses:dict):
    
    """ Test if there is no directory_out in the configuration file for ROI_analyses. """

    
    reference_conf_ROI_analyses["directory_out"]=None         

    with pytest.raises(ValueError):
        main(reference_conf_ROI_analyses)
        

def test_main_no_analyses(reference_conf_ROI_analyses:dict,reference_dir_out:Path):
    
    """ Test if there is no analysis has been selected for ROI_analyses. """

    reference_conf_ROI_analyses["directory_out"]=reference_dir_out
    reference_conf_ROI_analyses["specific_ROI_analyses"]=None   
    reference_conf_ROI_analyses["over_ROI_analyses"]=None 
    reference_conf_ROI_analyses["rate_ROI_analyses"]=None  

    with pytest.raises(ValueError):
        main(reference_conf_ROI_analyses)
        
@pytest.mark.parametrize("delimiter",[([100,-100,0])]) 
def test_main_valid_just(reference_conf_ROI_analyses:dict,reference_dir_out:Path,delimiter:tuple):
    
    """ Test if the specific ROI_analysis is valid. """

    reference_conf_ROI_analyses["directory_out"]=reference_dir_out
    reference_conf_ROI_analyses["specific_ROI_analyses"]=True
    reference_conf_ROI_analyses["specific_ROI_delimiter"]=delimiter
    
    with pytest.raises(ValueError):
        main(reference_conf_ROI_analyses)
        
@pytest.mark.parametrize("delimiter",[([100,-100,0])])       
def test_main_valid_rate(reference_conf_ROI_analyses:dict,reference_dir_out:Path,delimiter:tuple):
    
    """ Test if the specific rate_analysis is valid. """

    reference_conf_ROI_analyses["directory_out"]=reference_dir_out
    reference_conf_ROI_analyses["specific_ROI_analyses"]=False
    reference_conf_ROI_analyses["over_ROI_analyses"]=False
    reference_conf_ROI_analyses["rate_ROI_analyses"]=True
    reference_conf_ROI_analyses["rate_ROI_delimiter"]=delimiter
    
    with pytest.raises(ValueError):
        main(reference_conf_ROI_analyses)
        
        
def test_main_no_test(reference_conf_ROI_analyses:dict,reference_dir_out:Path):
    
    """ Test if no analysis is performed. """

    reference_conf_ROI_analyses["directory_out"]=reference_dir_out
    reference_conf_ROI_analyses["specific_ROI_analyses"]=False
    reference_conf_ROI_analyses["over_ROI_analyses"]=False
    reference_conf_ROI_analyses["rate_ROI_analyses"]=False
    
    main(reference_conf_ROI_analyses)
        
def test_main_empty_dir_files_fin(reference_conf_ROI_analyses:Path,reference_dir_out_empty:Path):
    """ Test if the directory_out is empty. """
    
    reference_conf_ROI_analyses["directory_out"]=reference_dir_out_empty
    main(reference_conf_ROI_analyses)