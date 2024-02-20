"""
Module for: 
- reading dcm header; 
- creating a database with header's information;
"""

import os
from pathlib import Path
import pandas as pd
import re
import pydicom
from datetime import datetime


def find_ct_info(directory, directory_out):
    """
    Create a dataframe reading a slice header of all CTs.
    It will contains ID, Name, Age, dimensions of Voxel_spacing, CT_path.

    :param directory: the directory of organized dcm.
    :param directory_out: the directory of analyses.
    :param save: if true, saves the database of dicom information,
                if false, shows them.

    :return df: database of headers information.
    """
    py_patient_file = Path(directory_out) / "py_patient_file.xlsx"

    try:
        df = pd.read_excel(py_patient_file)
        print("The dataframe with all headers information is in: ", py_patient_file)
        # display(df)
    
    except:
        
        print("I am going to analyze the header's informations.")

        data = []
         
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                dcm = pydicom.dcmread(file_path)
                # print(dcm)
                modality = dcm["Modality"].value
                
                if modality == "CT": 
                    try:
                        patient_id = dcm.PatientID
                        name = dcm.PatientName
                        patient_name = re.sub("\^", ", ", str(name))
                        
                        birth_date_str = dcm.PatientBirthDate
                        study_date_str = dcm.StudyDate
                        
                        birth_date = datetime.strptime(birth_date_str, "%Y%m%d")
                        study_date = datetime.strptime(study_date_str, "%Y%m%d")
                        
                        patient_age = (study_date - birth_date).days // 365
                        
                        voxel_spacing_x = dcm.PixelSpacing[0]
                        voxel_spacing_y = dcm.PixelSpacing[1]
                        voxel_spacing_z = dcm.SliceThickness    
                        
                        data.append((patient_id, patient_name, patient_age, voxel_spacing_x, voxel_spacing_y, voxel_spacing_z, root))
                    except Exception as e:
                        print(f"Error reading DICOM file {file}: {str(e)}")
                        print(dcm.StudyDate, dcm[0x10,0x30].value)
                    break
                break
        
        df = pd.DataFrame(data, columns=["PatientID", "PatientName", "PatientAge", "VoxelSpacingX", "VoxelSpacingY", "VoxelSpacingZ", "Path"])
        # print(df["Path"])
    
        with pd.ExcelWriter(py_patient_file) as writer:
            df.to_excel(writer, index=False)
        
        print(f"Dataframe with Dicom header saved in {py_patient_file}")
        
    return df