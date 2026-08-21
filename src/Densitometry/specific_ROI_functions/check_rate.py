"""
Module for:
- reading Excel files associated with patients' entire region histograms;
- extracting HU and relative counts;
- evaluating statistical features for a specific region of the histogram outside the specified HU range and for which
  the rate between the counts outside and inside this HU region is greater than the specified rate threshold.
"""

import os
import re
from pathlib import Path
import numpy as np
from Densitometry.total_ROI_functions import extract_histo as histo
import pandas as pd


def rate_variable() -> tuple[int, int, float]:
    """
    Ask the user to enter the HU and count thresholds.

    :return: minimum HU threshold, maximum HU threshold and rate threshold between counts outside and inside the (HU_min, HU_max) region.
    :rtype: tuple[int,int,float]
    """

    HU_min = int(input("Enter the minimum HU threshold above which to check: "))
    HU_max = int(input("Enter the maximum HU threshold beyond which to check: "))
    rate = float(
        input(
            f"Enter the threshold as a percentage of the count rate between inside and outside ({HU_min},{HU_max}): "
        )
    )
    print("")

    return HU_min, HU_max, rate


def analyze_rate(
    HU: pd.Series, counts: pd.Series, HU_min: int, HU_max: int
) -> tuple[float, pd.Series, pd.Series]:
    """
    Evaluate HU and counts considering the thresholds for rate ROI analysis.

    :param HU: HU from Excel file, corresponding to entire region histogram.
    :type HU: pd.Series
    :param counts: counts from Excel file, corresponding to entire region histogram.
    :type counts: pd.Series
    :param HU_min: minimum HU threshold.
    :type HU_min: int
    :param HU_max: maximum HU threshold.
    :type HU_max: int

    :return: rate between the counts inside and outside the selected HU range, HU values outside the selected range and their associated counts.
    :rtype: tuple[float, pd.Series, pd.Series]
    """

    pairs = {"HU": HU, "Counts": counts}
    df = pd.DataFrame(pairs)

    # Rates
    under_threshold = df[(df["HU"] >= HU_min) & (df["HU"] <= HU_max)]
    above_threshold = pd.concat([df[(df["HU"] < HU_min)], df[(df["HU"] > HU_max)]])

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


def check_rate(
    dir_files_fin: str | Path, directory_out: str | Path, rate_over_ROI: tuple[int, int, float]
) -> None:
    """
    Perform rate ROI analysis. This function is used for:
    - defining the analysis thresholds;
    - reading Excel files containing the entire region histograms;
    - extracting HU values and their corresponding counts;
    - obtaining statistical features for a specific
      region of the histogram (according to the rate analysis thresholds);
    - handling patients without a significant region of the histogram.

    :param dir_files_fin: directory of all patients' datasets with HU and counts.
    :type dir_files_fin: str | Path
    :param directory_out: directory of the analyses.
    :type directory_out: str | Path
    :param rate_over_ROI: tuple containing min_HU, max_HU and rate threshold for the ROI considered.
    :type rate_over_ROI: tuple[int,int,float]

    :return: None
    """

    # if True save all histograms and corresponding Excel file with HU and counts; if False, histograms are plotted.
    save_rate = True

    print("The saving variable is set on: ", save_rate)
    print("")

    HU_min, HU_max, rate = rate_over_ROI[0], rate_over_ROI[1], rate_over_ROI[2]
    pz_rate = []
    more_patient_stats_df_rate = pd.DataFrame()

    diff_files = Path(dir_files_fin).glob("*.xlsx")

    path_sp = directory_out / "Total_ROI" / "Histo_total_stats.xlsx"
    histo_total_stats = pd.read_excel(path_sp)
    histo_total_stats["PatientID"] = histo_total_stats["PatientID"].astype(str)
    histo_total_stats = histo_total_stats.set_index("PatientID")

    for diff_file in diff_files:
        name = Path(diff_file).name

        ID = re.sub(".xlsx", "", name)
        print("I analyze the patient: ", ID)
        df = pd.read_excel(diff_file, header=0, names=["HU", "Counts"])

        HU_ROI = df["HU"]
        counts_ROI = df["Counts"]

        # Study the rate
        diff, HU_rate, counts_rate = analyze_rate(HU_ROI, counts_ROI, HU_min, HU_max)

        if diff > (rate / 100.0):

            # Store information
            print(
                "You have caught a patient who has significant components in the indicated region."
            )
            pz_rate.append(ID)
            print("")

            sp_x = histo_total_stats.loc[ID, "VoxelSpacingX"]
            sp_y = histo_total_stats.loc[ID, "VoxelSpacingY"]
            sp_z = histo_total_stats.loc[ID, "VoxelSpacingZ"]

            sp = np.array([sp_x, sp_y, sp_z])
            ROI_name = str(histo_total_stats.loc[ID, "ROI_name"])

            dir_histo_rate = (
                Path(directory_out)
                / "Over_rate_regions"
                / f"Region_over_{HU_min}_{HU_max}_{rate}"
                / f"Histograms"
            )
            Path(dir_histo_rate).mkdir(parents=True, exist_ok=True)

            dir_files_rate = (
                Path(directory_out)
                / "Over_rate_regions"
                / f"Region_over_{HU_min}_{HU_max}_{rate}"
                / f"Files"
            )
            Path(dir_files_rate).mkdir(parents=True, exist_ok=True)

            stats_df_rate = histo.features_ROI(
                ID, HU_rate, counts_rate, sp, ROI_name, dir_histo_rate, dir_files_rate, save_rate
            )
            more_patient_stats_df_rate = pd.concat([more_patient_stats_df_rate, stats_df_rate])

    if len(more_patient_stats_df_rate) != 0:
        print("")
        print("Patients with significant rate between inside and outside the region are: ")
        print(pz_rate)

        if save_rate:
            excel_file_rate = (
                Path(directory_out)
                / "Over_rate_regions"
                / f"Region_over_{HU_min}_{HU_max}_{rate}"
                / f"Stats_over_{HU_min}_{HU_max}_{rate}.xlsx"
            )
            more_patient_stats_df_rate.to_excel(excel_file_rate, index=False)
            print(f"Region of interest statistics saved in {excel_file_rate}")

        else:
            print("")
            print(
                "I print the database with the densitometric features of the histograms of the region of interest."
            )

    else:
        print("There are no patients with components in the indicated region.")
