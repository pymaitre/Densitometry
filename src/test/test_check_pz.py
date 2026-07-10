"""

Testing check_pz module

"""


from pathlib import Path
import pytest
import pandas as pd
import os
import glob
from Densitometry.main_scripts.check_pz import find_id_dir, main


def test_find_id_dir(patient_directory:Path):
    
        """ Test if find_id_dir runs correctly. """

        id_dirs=find_id_dir(patient_directory)
        
        assert  isinstance(id_dirs,list)
        assert not len(id_dirs)==0



def test_main(patient_directory:Path, reference_dir_out:Path, reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test if the main function check_pz runs correctly. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file) 
    reference_conf_total_ROI_analyses["directory_out"]=Path(reference_dir_out)           

    main(reference_conf_total_ROI_analyses)
    


def test_main_no_dcm_out(reference_dir_out:Path, reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test if there is no directory_dcm_out in the configuration file for check_pz. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=None
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file) 
    reference_conf_total_ROI_analyses["directory_out"]=Path(reference_dir_out)           

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)



def test_main_no_py_file(patient_directory:Path,reference_dir_out:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test if there is no py_patient_path in the configuration file for check_pz. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]=None
    reference_conf_total_ROI_analyses["directory_out"]=Path(reference_dir_out)           

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        
        

def test_main_no_dir_out(patient_directory:Path, reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test if there is no directory_out in the configuration file for check_pz. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["directory_out"]=None       

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        


def test_main_not_valid_dcm_out(reference_dir_out:Path,reference_py_patient_file:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test if the Path to directory_dcm_out is not valid for check_pz. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]="C:\\User\\user\\not_valid_dcm"
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    reference_conf_total_ROI_analyses["directory_out"]=Path(reference_dir_out)       

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)
        


def test_main_not_valid_py(patient_directory:Path,reference_dir_out:Path,reference_conf_total_ROI_analyses:dict):
    
    """ Test if the Path to py_patient_path is not valid for check_pz. """

    
    reference_conf_total_ROI_analyses["directory_dcm_out"]=Path(patient_directory)
    reference_conf_total_ROI_analyses["py_patient_path"]="C:\\User\\user\\not_valid_py_patient_path"
    reference_conf_total_ROI_analyses["directory_out"]=Path(reference_dir_out)       

    
    with pytest.raises(ValueError):
        main(reference_conf_total_ROI_analyses)







