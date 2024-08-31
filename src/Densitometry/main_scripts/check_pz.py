from pathlib import Path
import pandas as pd
import os
import glob

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


def find_id_dir(directory):
        
        # Usa glob per trovare tutto il contenuto della directory
        folders = [f for f in glob.glob(directory + "/*") if os.path.isdir(f)]

        # Stampa i nomi delle cartelle
        id_dirs = []
        for folder in folders:
            id_dirs.append(os.path.basename(folder))
            # break

        return id_dirs


if __name__ == "__main__":
    main()
