"""
Module for: 
- reading excel files referred to patients entire region histograms;
- looking for HU and relatives counts;
- evalueting statistic features referred to a specific 
  region of the histogram beetween minimum and maximum 
  HU and above minimum counts thresholds.
"""

import os
import re
from src.Densitometry.total_ROI_functions import extract_histo as histo
from pathlib import Path
import pandas as pd
import numpy as np


def just_variable():
    """
    Function for inserting input HU and counts thresholds.

    :return HU_min: minimum HU threshold.
    :return HU_max: maximum HU threshold.
    :return min_counts: minimum counts threshold.
    """

    
    HU_min = int(input("Enter the minimum HU threshold for the region of interest: "))
    HU_max = int(input("Enter the maximum HU threshold for the region of interest: "))
    min_counts = int(input("Enter the counts threshold for the region of interest: "))    
    print("")

    return HU_min, HU_max, min_counts


def justified(HU, counts, HU_min, HU_max, min_counts):
    """
    Function for evalueting HU and counts above thresholds.

    :param HU: HU from excel file, referred to entire region histogram.
    :param counts: counts from excel file, referred to entire region histogram.
    :param HU_min: minimum HU threshold.
    :param HU_max: maximum HU threshold.
    :param min_counts: minimum counts threshold.

    :return HU_just: HU beetween thresholds.
    :return counts_just: counts above threshold.    
    """
    
    coppie = {'HU': HU, 'Counts': counts}
    df = pd.DataFrame(coppie)
    # display(df)

    above_threshold = df[(df["Counts"] > min_counts) & (HU_min < df["HU"]) & \
                            (df["HU"]< HU_max)]
    
    HU_just = above_threshold["HU"]
    counts_just = above_threshold["Counts"]

    return HU_just, counts_just


def histo_just(dir_files_fin, directory_out, delimiter):
    """
    Here almost functions are called for all patients. Especially:
    - establishing thresholds;
    - reading excel files referred to entire region histograms;
    - looking for HU and relatives counts;
    - evalueting statistic features referred to a specific 
      region of the histogram beetween minimum and maximum 
      HU and above minimum counts thresholds;
    - considering patients that do not have this significative
      region of the histogram.

    :param dir_files_fin: directory of all patients df with HU and counts.
    :param directory_out: the directory of analyses.
    :param save_just: if true save all histograms and relatives 
                    excel file with HU and counts;
                    if false, histograms are plotted.
    """

    save_just=True
    
    print("The saving variable is on: ", save_just)
    print("")
    
    # HU_min, HU_max, min_counts = just_variable()
    HU_min, HU_max, min_counts = delimiter[0], delimiter[1], delimiter[2]

    total_ROI_analysis = Path(directory_out) / "Total_ROI" / "Histo_total_stats.xlsx"
    df_total_ROI = pd.read_excel(total_ROI_analysis)
    print("The dataframe with all total ROI information is in: ", total_ROI_analysis)
    df_total_ROI.set_index("PatientID", inplace=True)
    
    pz_no_just = []
    more_patient_stats_df_justified = pd.DataFrame()
    
    diff_files = Path(dir_files_fin).glob("*.xlsx")

    for diff_file in diff_files:
        name = Path(diff_file).name
        # print(name)
        ID = re.sub(".xlsx", "", name)
        sp_total_ROI = np.array([df_total_ROI.loc[ID,"VoxelSpacingX"], df_total_ROI.loc[ID,"VoxelSpacingY"], df_total_ROI.loc[ID,"VoxelSpacingZ"]])
        name_total_ROI = str(df_total_ROI.loc[ID,"ROI_name"])

        df = pd.read_excel(diff_file, header=0, names=["HU", "Counts"])

        HU_ROI = df["HU"]
        counts_ROI = df["Counts"]

        HU_just, counts_just = justified(HU_ROI, counts_ROI, HU_min, HU_max, min_counts)

        if len(counts_just) != 0:       
            
            dir_histo_just = Path(directory_out) / "Specific_Regions" / f"Region_{HU_min}_{HU_max}_{min_counts}" / f"Histograms"
            Path(dir_histo_just).mkdir(parents=True, exist_ok=True)
        
            dir_files_just = Path(directory_out) / "Specific_Regions" / f"Region_{HU_min}_{HU_max}_{min_counts}" / f"Files"
            Path(dir_files_just).mkdir(parents=True, exist_ok=True)

            stats_df_just = histo.features_ROI(ID, HU_just, counts_just, sp_total_ROI, name_total_ROI, dir_histo_just, dir_files_just, save_just)
            more_patient_stats_df_justified = pd.concat([more_patient_stats_df_justified, stats_df_just])

        else:
            print("You caught a patient who has no components in the indicated region.")
            pz_no_just.append(ID)
            print("")

    if len(more_patient_stats_df_justified!=0):
        if save_just:      
            excel_file_just = (Path(directory_out) / "Specific_Regions" / 
                               f"Region_{HU_min}_{HU_max}_{min_counts}" / f"Stats_specific_{HU_min}_{HU_max}_{min_counts}.xlsx")
            more_patient_stats_df_justified.to_excel(excel_file_just, index=False)
            print(f"Region of interest statistics saved in {excel_file_just}")
    
        else:
            print("")
            print("I print the database with the densitometric features of the histograms of the region of interest.")
            # display(more_patient_stats_df_justified)

    if len(pz_no_just)!=0:
        print("I have problems with patients: ")
        print(pz_no_just)
    else:
        print("")
        print("There are no problems.")
    