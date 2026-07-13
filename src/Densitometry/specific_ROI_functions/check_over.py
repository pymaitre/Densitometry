"""
Module for: 
- reading Excel files referred to patients entire region histograms;
- looking for HU and relative counts;
- evaluating statistic features referred to a specific region of the histogram above minimum HU and counts thresholds.
"""

import os
import re
from Densitometry.total_ROI_functions import extract_histo as histo
from pathlib import Path
import numpy as np
import pandas as pd


def over_variable()->tuple[int, int]:
    """
    Function for inserting input HU and counts thresholds.

    :return: minimum HU threshold and minimum counts threshold.
    :rtype: tuple[int,int]
    """

    HU_min = int(input("Enter the minimum HU threshold above which to control: "))
    min_counts = int(input("Enter the count threshold for significance beyond the region of interest: "))    
    print("")

    return HU_min, min_counts


def over_HU_counts(HU:pd.Series, counts:pd.Series, HU_min:int, min_counts:int)->tuple[pd.Series,pd.Series]:
    """
    Evaluate HU and counts above thresholds.

    :param HU: HU from Excel file, referred to entire region histogram.
    :type HU: pd.Series
    :param counts: counts from Excel file, referred to entire region histogram.
    :type counts: pd.Series
    :param HU_min: minimum HU threshold.
    :type HU_min: int
    :param min_counts: minimum counts threshold.
    :type min_counts: int

    :return: HU beetween thresholds and the counts above threshold. 
    :rtype: tuple[pd.Series,pd.Series]
    """
    
    coppie = {'HU': HU, 'Counts': counts}
    df = pd.DataFrame(coppie)

    #Counts above the threshold
    above_threshold = df[ ( (df["HU"]> HU_min) & (df["Counts"] > min_counts) ) ]
    
    #Select HU and the associated counts above the threshold
    HU_over = above_threshold["HU"]
    counts_over = above_threshold["Counts"]


    return HU_over, counts_over


def check_over(dir_files_fin: str, directory_out: str, delimiter_over_ROI: tuple[int,int])->None:
    """
    Here almost functions are called for all patients. Especially for:
    - establishing thresholds;
    - reading Excel files referred to entire region histograms;
    - looking for HU and relatives counts;
    - evaluating statistic features referred to a specific 
      region of the histogram above minimum HU and minimum
      counts thresholds;
    - considering patients that do not have this significative
      region of the histogram.

    :param dir_files_fin: directory of all patients df with HU and counts.
    :type dir_files_fin: str
    :param directory_out: the directory of analyses.
    :type directory_out: str
    :param delimiter_over_ROI: tuple with min HU and min counts of threshold for the ROI.
    :type delimiter_over_ROI: tuple[int,int]

    :return: None
    """

    #save_over: if True save all histograms and relative Excel file with HU and counts; if false, histograms are plotted.
    
    save_over=True       
        
    print("The saving variable is on: ", save_over)
    print("")
    
    # Delimiter the ROI
    HU_min, min_counts = delimiter_over_ROI[0], delimiter_over_ROI[1]
    pz_over = []
    more_patient_stats_df_over = pd.DataFrame()
    
    diff_files = Path(dir_files_fin).glob("*.xlsx")
    
    path_sp=directory_out/"Total_ROI"/"Histo_total_stats.xlsx"
    histo_total_stats=pd.read_excel(path_sp)

    histo_total_stats["PatientID"] = histo_total_stats["PatientID"].astype(str)
    histo_total_stats = histo_total_stats.set_index("PatientID")


    #Find the statistic features
    for diff_file in diff_files:
        name = Path(diff_file).name
        
        ID = re.sub(".xlsx", "", name)
        print("I analyze the patient", ID)
        df = pd.read_excel(diff_file, header=0, names=["HU", "Counts"])

        HU_ROI = df["HU"]
        counts_ROI = df["Counts"]
       
        # Evaluate HU and counts above thresholds
        HU_over, counts_over = over_HU_counts(HU_ROI, counts_ROI, HU_min, min_counts)

        if len(counts_over) != 0:       
            
            print("You caught a patient who has components in the indicated region.")
            
            pz_over.append(ID)
            print("")  
            
            
            sp_x=histo_total_stats.loc[ID,"VoxelSpacingX"]
            sp_y=histo_total_stats.loc[ID,"VoxelSpacingY"]
            sp_z=histo_total_stats.loc[ID,"VoxelSpacingZ"]
            
            sp=np.array([sp_x,sp_y,sp_z])
            ROI_name=str(histo_total_stats.loc[ID,"ROI_name"])
            
            #Store information
            dir_histo_over = Path(directory_out) / "Over_counts_regions" / f"Region_over_{HU_min}_{min_counts}" / f"Histograms"
            Path(dir_histo_over).mkdir(parents=True, exist_ok=True)
        
            dir_files_over = Path(directory_out) / "Over_counts_regions" / f"Region_over_{HU_min}_{min_counts}" / f"Files"
            Path(dir_files_over).mkdir(parents=True, exist_ok=True)

            stats_df_over = histo.features_ROI(ID, HU_over, counts_over,sp,ROI_name,dir_histo_over, dir_files_over, save_over)
            more_patient_stats_df_over = pd.concat([more_patient_stats_df_over, stats_df_over])

    if len(more_patient_stats_df_over)!=0:
        print("Patients with significative counts over threshold are: ")
        print(pz_over)
        
        if save_over:      
            excel_file_over = Path(directory_out) / "Over_counts_regions" / f"Region_over_{HU_min}_{min_counts}" / f"Stats_over_{HU_min}_{min_counts}.xlsx"
            more_patient_stats_df_over.to_excel(excel_file_over, index=False)
            print(f"Region of interest statistics saved in {excel_file_over}")

        else:
            print("")
            print("I print the database with the densitometric features of the histograms of the region of interest.")
            

    else:
        print("There are no patients with components in the indicated region.")       
