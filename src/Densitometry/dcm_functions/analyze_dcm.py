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


def find_ct_info(directory:Path, directory_out:str, imm_mod:str)->pd.DataFrame:
    """
    Create a dataframe reading a slice header of all CTs.
    It will contains ID, Name, Age, dimensions of Voxel_spacing and CT_path.

    :param directory: the directory of organized dcm.
    :type directory: str
    :param directory_out: the directory of analyses.
    :type directory_out: str
    :param imm_mod: modality of image
    :type imm_mod: str

    :return: Database of headers information.
    :rtype: pd.DataFrame

    """
    
    #Patient file
    py_patient_file = Path(directory_out) / "py_patient_file.xlsx"

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

                        #Check if the modality is the same
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
                            
                            #Extract the Voxel spacing
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


def find_ct_info_input(directory:Path, directory_out:str, excel_name:str)->pd.DataFrame:
    """
    Create a dataframe reading a slice header of all CTs.
    It will contains ID, Name, Age, Modality, Path and number of files
    
    :param directory: the directory of organized dcm
    :type directory: Path
    :param directory_out: the directory of analyses
    :type directory_out: str
    :param excel_name: name of the dataset
    :type excel_name: str

    :return: database of headers information
    :rtype: pd.DataFrame
    
    """
    
    #File of the patient
    py_patient_file = Path(directory_out) / f"{excel_name}.xlsx"

    try:
        #File already exists
        df = pd.read_excel(py_patient_file)
        print("The dataframe with all headers information is in: ", py_patient_file)
        
    
    except:
        
        print("I am going to analyze the header's informations.")

        data = []
         
        #Check for DICOM files
        for root, dirs, files in os.walk(directory):
            n_files = len(list(Path(root).glob('*.dcm')))
            for file in files:
                file_path = os.path.join(root, file)
                if str(file).lower().endswith(".dcm"):
                    try:
                        dcm = pydicom.dcmread(file_path)
                        
                        #Modality
                        modality = dcm["Modality"].value
                
                        try:
                            #ID, Name and age
                            patient_id = dcm.PatientID
                            name = dcm.PatientName
                            patient_name = re.sub("\^", ", ", str(name))
                        
                            birth_date_str = dcm.PatientBirthDate
                            study_date_str = dcm.StudyDate
                            
                            birth_date = datetime.strptime(birth_date_str, "%Y%m%d")
                            study_date = datetime.strptime(study_date_str, "%Y%m%d")
                            
                            patient_age = (study_date - birth_date).days // 365
                               
                                                    
                            data.append((patient_id, patient_name, patient_age, modality, root, n_files))

                        except Exception as e:
                            print(f"Error reading DICOM file {file}: {str(e)}")
                        break            
                    except Exception as f:
                        print(f"Error reading DICOM file {file}: {str(f)}")
                
            
        
        
        #Generate the datase
        df = pd.DataFrame(data, columns=["PatientID", "PatientName", "PatientAge", "Modality", "Path", "n°_files"])
        df.sort_values(by=['PatientID'], inplace=True)
        
        
        
        #Save the dataset
        with pd.ExcelWriter(py_patient_file) as writer:
            df.to_excel(writer, index=False)
        
        print(f"Dataframe with Dicom header saved in {py_patient_file}")
        
    return df