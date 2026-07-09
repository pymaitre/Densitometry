from pathlib import Path
from test_other_functions import rtv_configuration_file
import pytest
import pandas as pd
import os
import glob


def test_find_id_dir(patient_directory:Path)->list:
    
        """
        Find all ID directories
        
        :param directory: input folder
        :type directory: Path
        
        :return: list of ID directories
        :rtype: list
        
        """

        directory=str(patient_directory)
        
        # Use glob to find all items in the directory
        folders = [f for f in glob.glob(directory + "/*") if os.path.isdir(f)]

        #Print names of the folders
        id_dirs = []
        for folder in folders:
            id_dirs.append(os.path.basename(folder))

        return id_dirs



def test_main(patient_directory, reference_dir_out, reference_py_patient_file):

    config = rtv_configuration_file("test_conf_total_ROI", save=False)
    
    #Check if the a parameter in the configuration file is missing 
    #if config["directory_dcm_out"]==None:
    #    raise ValueError("Missing directory_dcm_out")
    #elif config["py_patient_path"]==None:
    #    raise ValueError("Missing py_patient_path")
    
    config["directory_dcm_out"]=Path(patient_directory)
    config["py_patient_path"]=Path(reference_py_patient_file)
    
    
    #Check if the Paths exist
    if not Path(config["directory_dcm_out"]).exists():
        raise ValueError("directory_dcm_out does not exist")
    elif not Path(config["py_patient_path"]).exists():
        raise ValueError("py_patient_path does not exist")
        
    directory_dcm_out = config["directory_dcm_out"]
    py_patient_file = config["py_patient_path"]
    
    df_py = pd.read_excel(py_patient_file)

    id_dirs = test_find_id_dir(directory_dcm_out)
    
    
    list_pz = []
    for pz in df_py.loc[:, "PatientID"]:
        list_pz.append(str(pz))
            
    difference = [nome for nome in id_dirs if nome not in list_pz]

    print(difference)


#if __name__ == "__main__":
#    test_main(patient_directory, reference_dir_out, reference_py_patient_file)
