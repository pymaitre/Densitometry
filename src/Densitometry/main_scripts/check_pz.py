from pathlib import Path
from Densitometry.other_functions import rtv_configuration_file
import pandas as pd
import os
import glob


def find_id_dir(directory:Path)->list:
    
        """
        Find all ID directories
        
        :param directory: input folder
        :type directory: Path
        
        :return: list of ID directories
        :rtype: list
        
        """
        
        # Use glob to find all items in the directory
        folders = [f for f in glob.glob(directory + "/*") if os.path.isdir(f)]

        #Print names of the folders
        id_dirs = []
        for folder in folders:
            id_dirs.append(os.path.basename(folder))

        return id_dirs



def main():

    config = rtv_configuration_file("conf_total_ROI", save=False)
    
    directory_dcm_out = config["directory_dcm_out"]
    directory_out = config["path_directory_out"]
    
    py_patient_file = config["py_patient_path"]
    df_py = pd.read_excel(py_patient_file)

    id_dirs = find_id_dir(directory_dcm_out)
    
    
    list_pz = []
    for pz in df_py.loc[:, "PatientID"]:
        list_pz.append(str(pz))
            
    differenza = [nome for nome in id_dirs if nome not in list_pz]

    print(differenza)


if __name__ == "__main__":
    main()
