"""
Test module of check_pz.py
"""

from pathlib import Path
import pytest
import pandas as pd
import os
import glob
from Densitometry.main_scripts.check_pz import find_id_dir, main


def test_find_id_dir(patient_directory:Path):
    
        """ Check if the ID directory is found. """

        id_dirs=find_id_dir(patient_directory)
        
        assert  isinstance(id_dirs,list)
        assert not len(id_dirs)==0



def test_main(patient_directory:Path, reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test the main function of check_pz. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)           

    main(reference_conf_total_ROI_analyses)
    


def test_main_no_dcm_out(reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Do not provide directory_dcm_out in the configuration file. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=None
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)          

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)



def test_main_no_py_file(patient_directory:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Do not provide py_patient_path in the configuration file. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]=None
          

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        
        
def test_main_not_valid_dcm_out(reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Provide an invalid directory_dcm_out path. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]="C:\\User\\user\\not_valid_dcm"
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)     

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        


def test_main_not_valid_py(patient_directory:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Provide an invalid py_patient_path. """
    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]="C:\\User\\user\\not_valid_py_patient_path"    

    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)







