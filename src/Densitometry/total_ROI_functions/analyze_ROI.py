"""
Module for:
- reading information from CT scans (eventually show and convert it into an array);
- extracting the ROI names from the RTSTRUCT files;
- creating a dataset with all ROIs for all patients;
- creating a dataset with the counts associated with the identified ROIs.
"""

import os
from pathlib import Path
from Densitometry.total_ROI_functions import extract_info as info
import matplotlib.pyplot as plt
import pandas as pd
import pydicom


def all_ROI(
    df_py: pd.DataFrame, ID_problems: list, directory_out: Path, rt_kind: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Read all ROIs from RTSTRUCT file associated with CT scans.
    This function creates a dataset in which each row stores the PatientID and all the associated ROIs.
    A dataset containing the frequency of each ROI is also created.

    :param df_py: DataFrame with header information.
    :type df_py: pd.DataFrame
    :param ID_problems: list of PatientIDs with known problems.
    :type ID_problems: list
    :param directory_out: directory of the analyses.
    :type directory_out: Path
    :param rt_kind: type of RT.
    :type rt_kind: str

    :return: dataset containing the ROIs for each patient and a dataset with the frequency of each ROI.
    :rtype: tuple[pd.DataFrame, pd.DataFrame]
    """

    # Extract information from the dataset
    try:

        df_ROI = pd.read_excel(Path(directory_out) / "ROI_tot_pz.xlsx")
        print("")
        print("I read the dataframe with all the ROIs of each patient")
        print("")

        df_counts = pd.read_excel(Path(directory_out) / "counts_ROI.xlsx")
        print("")
        print("I read the dataframe with the ROI counts for each patient")
        print("")

    except:
        print("I am going to analyse all patient's ROIs.")

        show_CT_ROI = False
        slice = 0
        df_ROI = pd.DataFrame()

        for pz in range(0, len(df_py)):

            ID = df_py.loc[pz, "PatientID"]
            if str(ID) not in ID_problems:

                ct_path = df_py.loc[pz, "Path"]

                # CT, CT_arr = info.read_and_show_ct(ct_path, show_CT_ROI, slice)
                # rt_folder = (Path(ct_path).parent / "RTst")

                # Analyze RSTRCUCT
                rtstruct_paths = list(Path(ct_path).parents[2].glob(f"**/*{rt_kind}*"))
                for rtstruct_path in rtstruct_paths:
                    if rtstruct_path.is_dir():
                        continue
                    else:
                        print("RTst path is: ", rtstruct_path)
                        print("")

                        contour = []

                        rtstruct = pydicom.dcmread(rtstruct_path)

                        for roi in rtstruct.StructureSetROISequence:
                            contour.append(roi.ROIName)

                        print("ROIs of patient ", ID, " are: ", contour)
                        print("")

                        df_ROI_1pz = pd.DataFrame(
                            [contour],
                            index=[ID],
                        )
                        df_ROI = pd.concat([df_ROI, df_ROI_1pz])

        # Store information
        with pd.ExcelWriter(Path(directory_out) / "ROI_tot_pz.xlsx") as writer:
            df_ROI.to_excel(writer, index=True)
        print("")
        print("Saved the dataframe with all the ROIs of each patient")
        print("")

        series = pd.Series(df_ROI.values.flatten(), name="Counts").dropna()
        unique_values_counts = series.value_counts()

        with pd.ExcelWriter(Path(directory_out) / "counts_ROI.xlsx") as writer:
            unique_values_counts.to_excel(writer, index=True)
        df_counts = pd.read_excel(Path(directory_out) / "counts_ROI.xlsx")
        print("")
        print("Saved the dataframe with the ROI counts of each patient")
        print("")

    return df_ROI, df_counts
