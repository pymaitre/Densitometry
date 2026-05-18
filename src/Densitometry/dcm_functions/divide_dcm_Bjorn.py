"""
Module for: 
- reading dcm header; 
- dividing images (CT, RTst, RTPlan) into subdirectories of ID's one;
"""

import os
import re
from pathlib import Path
import shutil
import pandas as pd
import pydicom
import numpy as np
from datetime import datetime


def divide_dcm(directory_in:Path, directory_out:Path, divide=False, mode=False)->None:
    """
    Move DICOM files from directory_in with unsorted files to sorted files in directory_out.
    
    :param directory_in: folder with unsorted DICOM files
    :type directory_in: Path
    :param directory_out: folder with sorted DICOM files
    :type directory_out: Path
    :param divide: flag to divide DICOM files (default=False) 
    :param divide: Bool
    :param mode: set False uses prog_count while mode=True uses ct_sorted
    :param mode: Bool
    
    :return: None
    """
    
    mod_vec = 'CT'
    counter = [1,1]
    array_dict = []

    for root, dirs, files in os.walk(directory_in):
        files = [f for f in files if not f[0] == '.' if not f == 'metacache.mim']         
        dirs[:] = [d for d in dirs if not d[0] == '.']

        for file in files:
            file_path = os.path.join(root, file)
            
            #Read dcm and extract modality
            dcm = pydicom.dcmread(file_path)
            modality = dcm["Modality"].value
                       
            ID = dcm.PatientID
            UID = dcm.StudyInstanceUID
                       
            key_id = (1 for k in array_dict if k.get('id_num') == ID)           
            occurrences_id = sum(key_id)
            if occurrences_id == 0:
                thisdict = {}
                thisdict['id_num'] = ID
                thisdict['uid'] = [UID]
                thisdict['count_uid'] = 1
                index_uid = 1
                array_dict.append(thisdict)
                
            else:
                index_ID = [index for index, item in enumerate(array_dict) if item.get('id_num') == ID]
                
                #Check ID 
                if len(index_ID) > 1:
                   
                    print('Error! There are more than two elements with the same ID in the array of dictionaries.')
                    break
                occurrences_uid = array_dict[index_ID[0]]['uid'].count(UID)
                
                #Update UID count
                if occurrences_uid == 0:
                    array_dict[index_ID[0]]['uid'].append(UID)
                    index_uid = array_dict[index_ID[0]]['uid'].index(UID) + 1
                    array_dict[index_ID[0]]['count_uid'] += 1
                    
                                       
            
            #Create folders
            ID_dir = Path(directory_out) / ID 
            Path(ID_dir).mkdir(parents=True, exist_ok=True)

            n_imm = Path(ID_dir) / ('CT_'+str(index_uid))
            Path(n_imm).mkdir(parents=True, exist_ok=True)
            
            imm_dir = Path(n_imm) / 'CT'
            Path(imm_dir).mkdir(parents=True, exist_ok=True)             
            RS_dir = Path(n_imm) / 'RTst'
            Path(RS_dir).mkdir(parents=True, exist_ok=True)
            Altro_dir=Path(n_imm) / 'ALTRO'
            Path(Altro_dir).mkdir(parents=True, exist_ok=True)
            
            #Counter
            if not mode:
                temp = prog_count(counter, imm_dir, RS_dir, Altro_dir, modality, file, file_path, index_uid)
                counter = temp
                
            else:
                temp = ct_sorted(counter, imm_dir, RS_dir, Altro_dir, modality, file, file_path, index_uid)
                counter = temp
    #Check
    index_uids = [index for index, item in enumerate(array_dict) if item.get('count_uid') > 1]  
    id_problems = [ array_dict[i]['id_num'] for i in index_uids ]     
    print("The number of different IDs are:"+str(len(array_dict))+".")
    index_counts = np.array([index for index, item in enumerate(array_dict) if item.get('count_uid') > 1])
    if len(index_counts)==0:
        print('All patients have only one RTstruct files.')
    else:
        print('Some patients have more than one RTstruct files: '+ str(id_problems))  
    
    print("All files are inside 'ID', which contains CT_i, RTst and Altro")
    print("CT_i corresponds to different UID instances corresponding to RS_i inside RTst folder.")



def prog_count(counter:np.array, ID_dir:Path, RS_dir:Path, Altro_dir:Path, modality:str, file, file_path:Path, index)->np.array:
    """
    Count each type of file using a 2D counter
    
    :param counter: 2D array that counts CT (or MR) files and RTSTRUCT (or RTDOSE or RTPLAN or RAW)
    :type counter: np.array
    :param ID_dir: input ID directory
    :type ID_dir: Path
    :param RS_dir: input RTSTRUCT directory
    :type RS_dir: Path
    :param Altro_dir: input directory with other files
    :type Altro_dir: Path
    :param modality: name of the modality
    :type modality: str
    :param file_path: path of the file
    :type file_path: Path
    
    :return: array with counts
    :rtype: np.array
    
    """
    #CT
    if modality == "CT":
        temp = "CT_"+str(counter[0])+".dcm"
        folder = ID_dir / temp
        shutil.copy(file_path, folder)
        counter[0]+=1
    #MR
    if modality == "MR":
        temp = "MR_"+str(counter[0])+".dcm"
        folder = ID_dir / temp
        shutil.copy(file_path, folder)
        counter[0]+=1 
    #RTSTRUCT
    if modality == "RTSTRUCT":
        temp = "RS_"+str(counter[1])+".dcm"
        folder = RS_dir / temp
        shutil.copy(file_path, folder)
        counter[1]+=1
                    
    #RTDOSE
    if modality == "RTDOSE":
        temp = "RD_"+str(counter[1])
        folder = Altro_dir/ temp            
        shutil.copy(file_path, folder)
        counter[1]+=1
                   
    #RTPLAN
    if modality == "RTPLAN":
        temp = "RP_"+str(counter[1])
        folder = Altro_dir/ temp
        shutil.copy(file_path, folder)
        counter[1]+=1
                   
    #RAW              
    if modality == "RAW":  
        temp = "RAW_"+str(counter[1])
        folder = Altro_dir/ temp
        shutil.copy(file_path, folder)
        counter[1]+=1
                                     
    return counter

def ct_sorted(counter:np.array, imm_dir:Path, RS_dir:Path, Altro_dir:Path, modality:str, file, file_path:Path, index:str)->np.array:
    
    """
    Copy and sort in a CT files and count each type of file using a 2D counter
    
    :param counter: 2D array that counts CT (or MR) files and RTSTRUCT (or RTDOSE or RTPLAN or RAW)
    :type counter: np.array
    :param imm_dir: input CT directory
    :type imm_dir: Path
    :param RS_dir: input RTSTRUCT directory
    :type RS_dir: Path
    :param Altro_dir: input directory with other files
    :type Altro_dir: Path
    :param modality: name of the modality
    :type modality: str
    :param file_path: path of the file
    :type file_path: Path
    :param index: index for RTSTRUCT
    :type index: str
    
    :return: array with counts
    :rtype: np.array
    
    """
    
    #CT
    if modality == "CT":
        dcm = pydicom.dcmread(file_path)
        temp = "CT_"+str(dcm.InstanceNumber)
        folder = imm_dir / temp
        shutil.copy(file_path, folder)      
    #MR
    if modality == "MR":
        dcm = pydicom.dcmread(file_path)
        temp = "MR_"+str(dcm.InstanceNumber)
        folder = imm_dir / temp
        shutil.copy(file_path, folder)      

    #RTSTRUCT
    if modality == "RTSTRUCT":
        temp = "RS_"+str(index)
        folder = RS_dir / temp
        shutil.copy(file_path, folder)
                    
    #RTDOSE
    if modality == "RTDOSE":
        temp = "RD_"+str(counter[1])
        folder = Altro_dir/ temp            
        shutil.copy(file_path, folder)
        counter[1]+=1
                   
    #RTPLAN
    if modality == "RTPLAN":
        temp = "RP_"+str(counter[1])
        folder = Altro_dir/ temp
        shutil.copy(file_path, folder)
        counter[1]+=1
                   
    #RAW                    
    if modality == "RAW":  
        temp = "RAW_"+str(counter[1])
        folder = Altro_dir/ temp
        shutil.copy(file_path, folder)
        counter[1]+=1
                                     
    return counter 