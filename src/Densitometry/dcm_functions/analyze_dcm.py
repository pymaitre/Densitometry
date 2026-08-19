"""
Module for: 
reading DICOM header and creating a database containing header information.
"""

import os
from pathlib import Path
import pandas as pd
import re
import pydicom
from datetime import datetime


def find_ct_info(directory:Path, imm_mod:str,py_patient_file:Path)->pd.DataFrame:
    """
    Create a DataFrame reading the header of a slice from each CT scan.
    It will contain PatientID, PatientName, PatientAge,  voxel spacing dimensions and CT_path.

    :param directory: path to the directory of organized DICOM files.
    :type directory: Path
    :param imm_mod: modality of image.
    :type imm_mod: str
    :param py_patient_file: Path to the file with patient IDs and CT paths.
    :type py_patient_file: Path

    :return: DataFrame of header information.
    :rtype: pd.DataFrame
    """
    
    try:
        
        #Check if patient file has been already created
        df = pd.read_excel(py_patient_file)
        print("The DataFrame with all header information is in: ", py_patient_file)
    
    except:
        
        print("I am going to analyze the header information.")

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
                                patient_age = 'Not_computed'
                            
                            
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
        
        print(f"DataFrame with DICOM header saved in {py_patient_file}")
        
    return df

