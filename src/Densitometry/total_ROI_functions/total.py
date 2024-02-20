"""
Module for reading dcm images and obtaining densitometry histograms.
"""

import os
from pathlib import Path
from src.Densitometry.total_ROI_functions import extract_info as info
from src.Densitometry.total_ROI_functions import extract_histo as histo
import pandas as pd
  

def res_and_create_histo(df_py, ID_problems, new_sp, directory_out, show_info_all, save_info_all):
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

    print("The saving variable is set on: ", save_info_all)

    specific_ROI = [False, '']
    specific = str(input("\nDo you need a specific ROI? (y/n)"))
    if "y" in specific.lower():
        specific_ROI[0] = True
        specific_ROI[1] = str(input("What ROI do you need?"))
        
    
    dir_histo_fin = Path(directory_out) / "Total_ROI" / "Histograms_ok"
    Path(dir_histo_fin).mkdir(parents=True, exist_ok=True)

    dir_files_fin = Path(directory_out) / "Total_ROI" / "Files_ok"
    Path(dir_files_fin).mkdir(parents=True, exist_ok=True)

    more_patient_stats_df_total = pd.DataFrame()
    pz_problems = []
    
    # show_CT_ROI = str(input("\nDo you want to see a CT slice and it's ROI?"))
    # if "y" in show_CT_ROI:
    #     show_CT_ROI=True
    #     print("Show ROI is set on: ", show_CT_ROI)
    #     print("")
    #     slice = int(input("Select the slice you want to see: "))
    # else:
    #     show_CT_ROI=False
    #     print("Show df ROI is set on: ", show_CT_ROI)
    #     print("")
    #     slice=0
        
    for pz in range(0 , len(df_py)):
        ID = df_py.loc[pz,"PatientID"]
        
        if str(ID) not in ID_problems:

            CT, CT_arr, rt_path, rt, ROI_founded = info.CT_and_ROI(df_py, pz, specific_ROI, show_info_all, slice)
            if specific_ROI[0]:
                ROI_founded = specific_ROI[1]
                
            if ROI_founded is not None:
                print(f"ROI founded: {ROI_founded}")
                
                if (df_py.loc[pz,"VoxelSpacingX"]==new_sp[0] and 
                    df_py.loc[pz,"VoxelSpacingY"]==new_sp[1] and 
                    df_py.loc[pz,"VoxelSpacingZ"]==new_sp[2]):
                    
                    print("")    
                    print("PZ", ID , " ok")
    
                    HU_ROI, counts_ROI = info.ROI_ok(rt, ROI_founded, CT_arr, show_info_all, slice)
                    
                    stats_df = histo.features_ROI(ID, HU_ROI, counts_ROI, dir_histo_fin, dir_files_fin, save_info_all)
                                    
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
            
                    HU_ROI, counts_ROI = info.ROI_ok(rt, ROI_founded, CT_arr, show_info_all, slice) 
                    histo.features_ROI(ID, HU_ROI, counts_ROI, dir_histo_res, dir_files_res, save_info_all)
                                
            
                    print("")    
                    print("ANALYZING THE RESAMPLED IMAGE!")
                    print("")
            
                    HU_ROI_res, counts_ROI_res = info.ROI_res(CT, new_sp, rt_path, ROI_founded, show_info_all, slice)
                    
                    stats_df = histo.features_ROI(ID, HU_ROI_res, counts_ROI_res, dir_histo_fin, dir_files_fin, save_info_all)
                                   
                    compare = histo.compare_histo_res(HU_ROI_res, counts_ROI_res, HU_ROI, counts_ROI, 
                                                      dir_compare_ct_res, ID, save_info_all)
    
                    more_patient_stats_df_total = pd.concat([more_patient_stats_df_total, stats_df])

            else:
                print("")
                print(f"Patient {ID} has problems with ROI.")
                pz_problems.append(ID) 
                
        else:
            print("You caught a patient within the problem's ones.")
            pz_problems.append(ID)
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

    if len(pz_problems)!=0:
        print("I have problems with patients: ")
        print(pz_problems)
    else:
        print("\nThere are no problems")
        
    return dir_files_fin