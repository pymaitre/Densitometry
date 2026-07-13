"""
Module for: 
reading dcm header and creating a database with header's information.
"""

import os
from pathlib import Path
import pandas as pd
import re
import pydicom
from datetime import datetime


def find_ct_info(directory:Path, imm_mod:str,py_patient_file:Path)->pd.DataFrame:
    """
    Create a dataframe reading a slice header of all CTs.
    It will contain PatientID, PatientName, PatientAge, dimensions of VoxelSpacing and CT_path.

    :param directory: path to the directory of organized dcm.
    :type directory: Path
    :param imm_mod: modality of image.
    :type imm_mod: str
    :param py_patient_file: Path file with ID_patient and CT path.
    :type py_patient_file: Path

    :return: Database of headers information.
    :rtype: pd.DataFrame
    """
    
    try:
        
        #Check if patient file has been already created
        df = pd.read_excel(py_patient_file)
        print("The dataframe with all headers information is in: ", py_patient_file)
    
    except:
        
        print("I am going to analyze the header's informations.")

        data = []
         
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    if str(file).lower().endswith(".dcm"):
                        file_path = os.path.join(root, file)
                        dcm = pydicom.dcmread(file_path, force=True)
                        modality = dcm["Modality"].value

                        
                        if modality == str(imm_mod): 

                            #Extract name, ID and age
                            patient_id = dcm.PatientID
                            name = dcm.PatientName
                            patient_name = re.sub("\^", ", ", str(name))
                        
                            birth_date_str = dcm.PatientBirthDate
                            study_date_str = dcm.StudyDate
                            
                            if str(birth_date_str) != '':
                                birth_date = datetime.strptime(birth_date_str, "%Y%m%d")
                                study_date = datetime.strptime(study_date_str, "%Y%m%d")
                                
                                patient_age = (study_date - birth_date).days // 365

                            else:
                                patient_age = 'Non_calcolato'
                            
                            
                            voxel_spacing_x = dcm.PixelSpacing[0]
                            voxel_spacing_y = dcm.PixelSpacing[1]
                            voxel_spacing_z = dcm.SliceThickness    
                            
                            print(patient_id)
                            data.append((patient_id, patient_name, patient_age, voxel_spacing_x, voxel_spacing_y, voxel_spacing_z, root))
                            break
                except Exception as e:
                    print(f"Error reading DICOM file {file}: {str(e)}")
                    
        
        
        df = pd.DataFrame(data, columns=["PatientID", "PatientName", "PatientAge", "VoxelSpacingX", "VoxelSpacingY", "VoxelSpacingZ", "Path"])
        
    
        with pd.ExcelWriter(py_patient_file) as writer:
            df.to_excel(writer, index=False)
        
        print(f"Dataframe with Dicom header saved in {py_patient_file}")
        
    return df

