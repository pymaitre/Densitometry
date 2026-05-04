"""
Module for: 
- reading excel files referred to patients entire region histograms;
- looking for HU and relatives counts;
- evalueting statistic features referred to a specific 
  region of the histogram below minimum and above maximum 
  HU thresholds and above rate threshold beetween counts of
  the part outside and inside this region of HU.
"""

import os
import re
from pathlib import Path
from Densitometry.total_ROI_functions import extract_histo as histo
import pandas as pd


def rate_variable()->tuple[int,int,float]:
    """
    Function for inserting input HU and counts thresholds.

    :return HU_min: minimum HU threshold.
    :return HU_max: maximum HU threshold.
    :return rate: rate thresholds beetween counts outside 
                and counts inside the region of (HU_min, HU_max).

    """

    HU_min = int(input("Enter the minimum HU threshold above which to check: "))
    HU_max = int(input("Enter the maximum HU threshold beyond which to control: "))
    rate = float(input(f"Enter the threshold as a percentage of the count rate between inside and outside ({HU_min},{HU_max}): "))    
    print("")

    return HU_min, HU_max, rate


def analyze_rate(HU, counts, HU_min, HU_max):
    """
    Function for evalueting HU and counts above thresholds.

    :param HU: HU from excel file, referred to entire region histogram.
    :param counts: counts from excel file, referred to entire region histogram.
    :param HU_min: minimum HU threshold.
    :param HU_max: maximum HU threshold.

    :return diff: rate beetween parts of the histograms inside
                and outside the HU thresholds
    :return HU_rate: HU outside the region.
    :return counts_rate: counts outside the region.    
    """
    
    coppie = {'HU': HU, 'Counts': counts}
    df = pd.DataFrame(coppie)
    # display(df)

    under_threshold = df[ (df["HU"] >= HU_min) & (df["HU"] <= HU_max)]
    above_threshold = pd.concat( [df[ (df["HU"] < HU_min) ], df[ (df["HU"] > HU_max) ]])
    
    counts_in = under_threshold["Counts"].sum()
    counts_over = above_threshold["Counts"].sum()    
    diff = counts_over / counts_in
    
    print("The sum of the counts in the region of interest is: ", counts_in)
    print("The sum of the counts outside the region of interest is: ", counts_over)
    print("The rate between them is: ", diff)
    print("")

    HU_rate = above_threshold["HU"]
    counts_rate = above_threshold["Counts"]
    
    return diff, HU_rate, counts_rate
    

def check_rate(dir_files_fin, directory_out, rate_over_ROI):
    """
    Here almost functions are called for all patients. Especially:
    - establishing thresholds;
    - reading excel files referred to entire region histograms;
    - looking for HU and relatives counts;
    - evalueting statistic features referred to a specific 
      region of the histogram above minimum and maximum 
      HU and minimum counts thresholds;
    - considering patients that do not have this significative
      region of the histogram.

    :param dir_files_fin: directory of all patients df with HU and counts.
    :param directory_out: the directory of analyses.
    :param rate_over_ROI
    """

    #if true save all histograms and relatives excel file with HU and counts; if false, histograms are plotted.
    save_rate=True        
        
    print("The saving variable is set on: ", save_rate)
    print("")


    # HU_min, HU_max, rate = rate_variable()
    HU_min, HU_max, rate = rate_over_ROI[0], rate_over_ROI[1]
    pz_rate = []
    more_patient_stats_df_rate = pd.DataFrame()
    
    diff_files = Path(dir_files_fin).glob("*.xlsx")

    for diff_file in diff_files:
        name = Path(diff_file).name
        # print(name)
        ID = re.sub(".xlsx", "", name)
        print("I analyze the patient: ", ID)
        df = pd.read_excel(diff_file, header=0, names=["HU", "Counts"])

        HU_ROI = df["HU"]
        counts_ROI = df["Counts"]
        # print(HU_ROI, counts_ROI)

        diff, HU_rate, counts_rate = analyze_rate(HU_ROI, counts_ROI, HU_min, HU_max)
        # print(HU_over)

        if diff > (rate/100.):       
            
            print("You have caught a patient who has significant components in the indicated region.")
            pz_rate.append(ID)
            print("")  
            
            dir_histo_rate = Path(directory_out) / "Over_rate_regions" / f"Region_over_{HU_min}_{HU_max}_{rate}" / f"Histograms"
            Path(dir_histo_rate).mkdir(parents=True, exist_ok=True)
        
            dir_files_rate = Path(directory_out) / "Over_rate_regions" / f"Region_over_{HU_min}_{HU_max}_{rate}" / f"Files"
            Path(dir_files_rate).mkdir(parents=True, exist_ok=True)

            stats_df_rate = histo.features_ROI(ID, HU_rate, counts_rate, dir_histo_rate, dir_files_rate, save_rate)
            more_patient_stats_df_rate = pd.concat([more_patient_stats_df_rate, stats_df_rate])

    if len(more_patient_stats_df_rate!=0):
        print("")
        print("Patients with significative rate beetween inside and outside the region are: ")
        print(pz_rate)
        
        if save_rate:      
            excel_file_rate = Path(directory_out) / "Over_rate_regions" / f"Region_over_{HU_min}_{HU_max}_{rate}" / f"Stats_over_{HU_min}_{HU_max}_{rate}.xlsx"
            more_patient_stats_df_rate.to_excel(excel_file_rate, index=False)
            print(f"Region of interest statistics saved in {excel_file_rate}")

        else:
            print("")
            print("I print the database with the densitometric features of the histograms of the region of interest.")
            # display(more_patient_stats_df_rate)

    else:
        print("There are no patients with components in the indicated region.")   