"""
Module for: 
- reading excel files referred to patients entire region histograms;
- looking for HU and relatives counts;
- evaluating statistic features referred to a specific 
  region of the histogram above minimum HU and counts thresholds.
"""

import os
import re
from Densitometry.total_ROI_functions import extract_histo as histo
from pathlib import Path
import pandas as pd


def over_variable()->tuple[int, int]:
    """
    Function for inserting input HU and counts thresholds.

    :return HU_min: minimum HU threshold.
    :return min_counts: minimum counts threshold.
    
    """

    HU_min = int(input("Enter the minimum HU threshold above which to control: "))
    min_counts = int(input("Enter the count threshold for significance beyond the region of interest: "))    
    print("")

    return HU_min, min_counts


def over_HU_counts(HU, counts, HU_min, min_counts):
    """
    Function for evalueting HU and counts above thresholds.

    :param HU: HU from excel file, referred to entire region histogram.
    :param counts: counts from excel file, referred to entire region histogram.
    :param HU_min: minimum HU threshold.
    :param min_counts: minimum counts threshold.

    :return new_x: more present value of coordinate x of voxel spacing
    :return new_y: more present value of coordinate y of voxel spacing
    :return new_z: more present value of coordinate z of voxel spacing
    """
    
    coppie = {'HU': HU, 'Counts': counts}
    df = pd.DataFrame(coppie)
    # display(df)

    above_threshold = df[ ( (df["HU"]> HU_min) & (df["Counts"] > min_counts) ) ]
    
    HU_over = above_threshold["HU"]
    counts_over = above_threshold["Counts"]
    # print(HU_over)

    return HU_over, counts_over


def check_over(dir_files_fin, directory_out, delimiter_over_ROI)->None:
    """
    Here almost functions are called for all patients. Especially:
    - establishing thresholds;
    - reading excel files referred to entire region histograms;
    - looking for HU and relatives counts;
    - evalueting statistic features referred to a specific 
      region of the histogram above minimum HU and minimum
      counts thresholds;
    - considering patients that do not have this significative
      region of the histogram.

    :param dir_files_fin: directory of all patients df with HU and counts.
    :param directory_out: the directory of analyses.
    :param delimiter_over_ROI

    return None
    """

    #save_over: if true save all histograms and relatives excel file with HU and counts; if false, histograms are plotted.
    
    save_over=True       
        
    print("The saving variable is on: ", save_over)
    print("")
    

    # HU_min, min_counts = over_variable()
    HU_min, min_counts = delimiter_over_ROI[0], delimiter_over_ROI[1]
    pz_over = []
    more_patient_stats_df_over = pd.DataFrame()
    
    diff_files = Path(dir_files_fin).glob("*.xlsx")

    for diff_file in diff_files:
        name = Path(diff_file).name
        # print(name)
        ID = re.sub(".xlsx", "", name)
        print("I analyze the patient", ID)
        df = pd.read_excel(diff_file, header=0, names=["HU", "Counts"])

        HU_ROI = df["HU"]
        counts_ROI = df["Counts"]
        # print(HU_ROI, counts_ROI)

        HU_over, counts_over = over_HU_counts(HU_ROI, counts_ROI, HU_min, min_counts)
        # print(HU_over)

        if len(counts_over) != 0:       
            
            print("You caught a patient who has components in the indicated region.")
            pz_over.append(ID)
            print("")  
            
            dir_histo_over = Path(directory_out) / "Over_counts_regions" / f"Region_over_{HU_min}_{min_counts}" / f"Histograms"
            Path(dir_histo_over).mkdir(parents=True, exist_ok=True)
        
            dir_files_over = Path(directory_out) / "Over_counts_regions" / f"Region_over_{HU_min}_{min_counts}" / f"Files"
            Path(dir_files_over).mkdir(parents=True, exist_ok=True)

            stats_df_over = histo.features_ROI(ID, HU_over, counts_over, dir_histo_over, dir_files_over, save_over)
            more_patient_stats_df_over = pd.concat([more_patient_stats_df_over, stats_df_over])

    if len(more_patient_stats_df_over!=0):
        print("Patients with significative counts over threshold are: ")
        print(pz_over)
        
        if save_over:      
            excel_file_over = Path(directory_out) / "Over_counts_regions" / f"Region_over_{HU_min}_{min_counts}" / f"Stats_over_{HU_min}_{min_counts}.xlsx"
            more_patient_stats_df_over.to_excel(excel_file_over, index=False)
            print(f"Region of interest statistics saved in {excel_file_over}")

        else:
            print("")
            print("I print the database with the densitometric features of the histograms of the region of interest.")
            # display(more_patient_stats_df_over)

    else:
        print("There are no patients with components in the indicated region.")       
