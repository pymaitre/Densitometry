"""
Module for:
- reading Excel files associated with patients' entire region histograms;
- extracting HU and relative counts;
- evaluating statistical features for a specific region of the histogram
  between minimum and maximum HU thresholds and above minimum count thresholds.
"""

import os
import re
from Densitometry.total_ROI_functions import extract_histo as histo
from pathlib import Path
import pandas as pd
import numpy as np


def just_variable() -> tuple[int, int, int]:
    """
    Ask the user to enter the HU range and minimum count threshold.

    :return: minimum HU threshold, maximum HU threshold and minimum count threshold.
    :rtype: tuple[int,int,int]
    """

    HU_min = int(input("Enter the minimum HU threshold for the region of interest: "))
    HU_max = int(input("Enter the maximum HU threshold for the region of interest: "))
    min_counts = int(input("Enter the count threshold for the region of interest: "))
    print("")

    return HU_min, HU_max, min_counts


def justified(
    HU: pd.Series, counts: pd.Series, HU_min: int, HU_max: int, min_counts: int
) -> tuple[pd.Series, pd.Series]:
    """
    Evaluate HU values in the HU range and their relative counts if greater than min_counts.

    :param HU: HU from Excel file, corresponding to the entire region histogram.
    :type HU: pd.Series
    :param counts: counts from Excel file, corresponding to the entire region histogram.
    :type counts: pd.Series
    :param HU_min: minimum HU threshold.
    :type HU_min: int
    :param HU_max: maximum HU threshold.
    :type HU_max: int
    :param min_counts: minimum count threshold.
    :type min_counts: int

    :return: HU values in the HU range and their associated counts above the minimum count threshold.
    :rtype: tuple[pd.Series, pd.Series]
    """

    pairs = {"HU": HU, "Counts": counts}
    df = pd.DataFrame(pairs)

    # HU values within the range
    above_threshold = df[(df["Counts"] > min_counts) & (HU_min < df["HU"]) & (df["HU"] < HU_max)]

    HU_just = above_threshold["HU"]
    counts_just = above_threshold["Counts"]

    return HU_just, counts_just


def histo_just(dir_files_fin: str, directory_out: str, delimiter: tuple[int, int, int]) -> None:
    """
    Perform specific ROI analysis. This function is used for:
    - defining the analysis thresholds;
    - reading Excel files containing the entire region histograms;
    - extracting HU and their corresponding counts;
    - evaluating statistical features for a specific region of the histogram (HU values between HU_min and HU_max and their counts above minimum count threshold);
    - handling patients without a significant region of the histogram.

    :param dir_files_fin: directory of all patients' datasets with HU and counts.
    :type dir_files_fin: str
    :param directory_out: directory of the analyses.
    :type directory_out: str
    :param delimiter: tuple with min_HU, max_HU and min_counts.
    :type delimiter: tuple[int,int,int]

    :return: None
    """

    # if True save all histograms and corresponding Excel file with HU and counts; if false, histograms are plotted.
    save_just = True

    print("The saving variable is on: ", save_just)
    print("")

    HU_min, HU_max, min_counts = delimiter[0], delimiter[1], delimiter[2]

    total_ROI_analysis = Path(directory_out) / "Total_ROI" / "Histo_total_stats.xlsx"
    df_total_ROI = pd.read_excel(total_ROI_analysis)
    print("The dataframe with all total ROI information is in: ", total_ROI_analysis)
    df_total_ROI["PatientID"] = df_total_ROI["PatientID"].astype(str)
    df_total_ROI.set_index("PatientID", inplace=True)

    pz_no_just = []
    more_patient_stats_df_justified = pd.DataFrame()

    diff_files = Path(dir_files_fin).glob("*.xlsx")

    for diff_file in diff_files:
        name = Path(diff_file).name

        ID = re.sub(".xlsx", "", name)
        sp_total_ROI = np.array(
            [
                df_total_ROI.loc[ID, "VoxelSpacingX"],
                df_total_ROI.loc[ID, "VoxelSpacingY"],
                df_total_ROI.loc[ID, "VoxelSpacingZ"],
            ]
        )
        name_total_ROI = str(df_total_ROI.loc[ID, "ROI_name"])

        df = pd.read_excel(diff_file, header=0, names=["HU", "Counts"])

        HU_ROI = df["HU"]
        counts_ROI = df["Counts"]

        # Justified HU and counts
        HU_just, counts_just = justified(HU_ROI, counts_ROI, HU_min, HU_max, min_counts)

        # Store information
        if len(counts_just) != 0:

            dir_histo_just = (
                Path(directory_out)
                / "Specific_Regions"
                / f"Region_{HU_min}_{HU_max}_{min_counts}"
                / f"Histograms"
            )
            Path(dir_histo_just).mkdir(parents=True, exist_ok=True)

            dir_files_just = (
                Path(directory_out)
                / "Specific_Regions"
                / f"Region_{HU_min}_{HU_max}_{min_counts}"
                / f"Files"
            )
            Path(dir_files_just).mkdir(parents=True, exist_ok=True)

            stats_df_just = histo.features_ROI(
                ID,
                HU_just,
                counts_just,
                sp_total_ROI,
                name_total_ROI,
                dir_histo_just,
                dir_files_just,
                save_just,
            )
            more_patient_stats_df_justified = pd.concat(
                [more_patient_stats_df_justified, stats_df_just]
            )

        else:
            print("You caught a patient who has no components in the indicated region.")
            pz_no_just.append(ID)
            print("")

    if len(more_patient_stats_df_justified) != 0:
        if save_just:
            excel_file_just = (
                Path(directory_out)
                / "Specific_Regions"
                / f"Region_{HU_min}_{HU_max}_{min_counts}"
                / f"Stats_specific_{HU_min}_{HU_max}_{min_counts}.xlsx"
            )
            more_patient_stats_df_justified.to_excel(excel_file_just, index=False)
            print(f"Region of interest statistics saved in {excel_file_just}")

        else:
            print("")
            print(
                "I print the database with the densitometric features of the histograms of the region of interest."
            )

    if len(pz_no_just) != 0:
        print("I have problems with patients: ")
        print(pz_no_just)
    else:
        print("")
        print("There are no problems.")
