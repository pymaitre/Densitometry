"""
Module for reading dcm images and obtaining densitometry histograms.
"""

import os
from pathlib import Path
from src.Densitometry.total_ROI_functions import extract_info as info
from src.Densitometry.total_ROI_functions import extract_histo as histo
import pandas as pd
import pydicom
import numpy as np
  

def get_roi_names(rtstruct_path):
    rtstruct = pydicom.dcmread(rtstruct_path)

    roi_names = []
    for roi in rtstruct.StructureSetROISequence:
        roi_names.append(roi.ROIName)

    return roi_names


def find_rt_st(ct_path, rt_kind, list_roi):
    try:
        
        # rt_folder = list(Path(ct_path).parent.glob(f"{rt_kind}*"))
        # TODO: check RTst path by name in conf.
        path_rt_structures = list(Path(ct_path).parent.glob(f"{rt_kind}*/*.dcm"))

        nomi_con_importanza = {}
        for i in range(0, len(list_roi)):
            nomi_con_importanza[list_roi[i]] = len(list_roi)-i
        print("I'm searching contours with this order: ")
        print(nomi_con_importanza)
        
        for path_rt_st in path_rt_structures:
            print("I found the RTst:")
            print(path_rt_st)

            ROI_names = get_roi_names(path_rt_st)
            # print(ROI_names)
            
            for nome in nomi_con_importanza:
                # print('Check nome: ', nome)
                for ROI_name in ROI_names:
                    # print('ROI name: ', ROI_name)
                    if nome in ROI_name:
                        print(f'ROI name {ROI_name} matched with name {nome}.')
                        # CT = dtn.read_dicom_image(ct_path)
                        # print('Letta CT')
                        # rt = dtn.read_dicom_rtstruct(path_rt_st, CT, ROI_name)
                        # print(type(rt), rt)
                        return ROI_name, path_rt_st
                    # else:
                    #     print(f'{ROI_name} is catched.')
                    #     return ROI_name
        
    except Exception as e:
        print('ROI not founded with error: ', e)


def res_and_create_histo(df_py, ID_problems, new_sp, rt_kind, list_roi, directory_out, show_info_all, save_info_all):
    """
    Here almost functions are called for all patients. Especially:
    - CT and RTst are possibly showed; 
    - specific ROI is found;
    - if original CT voxel spacing is equal to the most common spacing,
      this function creates the histogram and relative dataframe of the ROI;
    - if not, histogram and df are created of the original image are obtained,
      CT and RTst are resampled and histogram and df are created;
    - comparison between original and resampled histo is obtained;
    - a database with all patients features is created too.

    :param df_py: database of headers information.
    :param ID_problems: input list of patient's ID with problems.
    :param new_sp: new voxel spacing for resampling.
    :param directory_out: the directory of analyses.
    :param show_info_all: if true show CT and ROI info.
    :param save_info_all: if true save all histograms and relatives 
                    excel file with HU and counts;
                    if false, histograms are plotted.

    :return dir_files_fin: directory of all patients df with HU and counts.
    """

    print("The showing variable is set on: ", show_info_all)
    print("The saving variable is set on: ", save_info_all)  
    
    dir_histo_fin = Path(directory_out) / "Total_ROI" / "Histograms_ok"
    Path(dir_histo_fin).mkdir(parents=True, exist_ok=True)

    dir_files_fin = Path(directory_out) / "Total_ROI" / "Files_ok"
    Path(dir_files_fin).mkdir(parents=True, exist_ok=True)

    more_patient_stats_df_total = pd.DataFrame()
    ID_problems = []
    # pz_problems = pd.DataFrame()
    pz_problems = []
    ID_with_problems = pd.DataFrame()
    
        
    for pz in range(0 , len(df_py)):
        ID = df_py.loc[pz,"PatientID"]
        
        if str(ID) not in ID_problems:

            try:
                ct_path = df_py.loc[pz, "Path"]
                ROI_founded, ROI_path = find_rt_st(ct_path, rt_kind, list_roi)
                
                old_sp = np.array([df_py.loc[pz,"VoxelSpacingX"], df_py.loc[pz,"VoxelSpacingY"], df_py.loc[pz,"VoxelSpacingZ"]])

                if (old_sp[0]==new_sp[0] and 
                    old_sp[1]==new_sp[1] and 
                    old_sp[2]==new_sp[2]):
                    
                    print("")    
                    print("PZ", ID , " ok")
                    
                    HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all, 
                                                     save_info_all, directory_out, ID, slice=40)
                    
                    stats_df = histo.features_ROI(ID, HU_ROI, counts_ROI, new_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
                                    
                    more_patient_stats_df_total = pd.concat([more_patient_stats_df_total, stats_df])
    
                else:
                    print("")    
                    print("PZ", ID , " has to be resampled")
    
                    dir_histo_res = Path(directory_out) / "Total_ROI" / "To_be_resampled" / "Histograms"
                    Path(dir_histo_res).mkdir(parents=True, exist_ok=True)
                
                    dir_files_res = Path(directory_out) / "Total_ROI" / "To_be_resampled" / "Files"
                    Path(dir_files_res).mkdir(parents=True, exist_ok=True)
                
                    dir_compare_ct_res = Path(directory_out) / "Total_ROI" / "To_be_resampled" / "Compare_histo"
                    Path(dir_compare_ct_res).mkdir(parents=True, exist_ok=True)
            
                    HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all, 
                                                     save_info_all, directory_out, ID, slice=40)
                    histo.features_ROI(ID, HU_ROI, counts_ROI, old_sp, ROI_founded, dir_histo_res, dir_files_res, save_info_all)
                                
            
                    print("")    
                    print("ANALYZING THE RESAMPLED IMAGE!")
                    print("")
            
                    HU_ROI_res, counts_ROI_res = info.ROI_res(ct_path, ROI_path, new_sp, ROI_founded, 
                                                              show_info_all, save_info_all, directory_out, ID, slice=100)
                    
                    stats_df = histo.features_ROI(ID, HU_ROI_res, counts_ROI_res, new_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
                                   
                    compare = histo.compare_histo_res(HU_ROI_res, counts_ROI_res, HU_ROI, counts_ROI, 
                                                      dir_compare_ct_res, ID, save_info_all)
    
                    more_patient_stats_df_total = pd.concat([more_patient_stats_df_total, stats_df])

            except Exception as e:
                # else:
                print(f"Patient {ID} has problems with ROI.")
                print(f"{e}")
                ID_problems.append(ID)
                # pz_problems = pd.concat([ID, f"{e}"], axis=1)
                pz_problems.append([ID, str(e)])
                df_problems = pd.DataFrame(pz_problems, columns=['File Path', 'Errore'], index=False)
                ID_with_problems = pd.concat([ID_with_problems, df_problems]) 
                
        else:
            print("You caught a patient within the problem's ones.")
            ID_problems.append(ID)
            pz_problems.append([ID, "You knew there was an error"])
            ID_with_problems = pd.concat([ID_with_problems, pz_problems])
            print("")

    if len(more_patient_stats_df_total!=0):
        # if save_all:
        excel_file_tot = Path(directory_out) / "Total_ROI" / "Histo_total_stats.xlsx"
        more_patient_stats_df_total.to_excel(excel_file_tot, index=False)
        print(f"All ROI's densitometric features are in {excel_file_tot}")
    
        # else:
        #     print("")
        #     print("Saving the database with the densitometric features of the histograms of the entire region.")
            # display(more_patient_stats_df_total)

    if len(ID_problems)!=0:
        excel_ID_problems = Path(directory_out) / "ID_with_problems.xlsx"
        print("I have problems with patients: ")
        print(ID_problems)
        ID_with_problems.to_excel(excel_ID_problems)
    else:
        print("\nThere are no problems")
        
    return dir_files_fin