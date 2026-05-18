from pathlib import Path
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
    
    directory_dcm_out = r"\\IHSR.dom\OSRFileServices\Ric.FisicaSanitaria\AAAshared\dataset\segmentazione\breast_Fodor22_from2017\no_boost\ANONYMIZED_Dx\ANONYMIZED_Breast_Monica_Dx"
    directory_out = r"\\IHSR.dom\OSRFileServices\Ric.FisicaSanitaria\Belardo\Breast\Analyses\breast_Fodor22_from2017\no_boost\ANONYMIZED_Dx\ANONYMIZED_Breast_Monica_Dx"
    py_patient_file = Path(directory_out) / "py_patient_file.xlsx"
    df_py = pd.read_excel(py_patient_file)

    id_dirs = find_id_dir(directory_dcm_out)
    
    
    list_pz = []
    for pz in df_py.loc[:, "PatientID"]:
        list_pz.append(str(pz))
            
    differenza = [nome for nome in id_dirs if nome not in list_pz]

    print(differenza)


if __name__ == "__main__":
    main()
