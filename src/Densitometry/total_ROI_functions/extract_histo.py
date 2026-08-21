"""
Module for:
- creating histogram plots and Excel files based on input HU values and counts.
- extracting statistical features from histograms.
In case of resampling, plots with overlapping histograms associated with the original and resampled images are generated.
"""

import os
import re
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd


def features_ROI(
    ID: str,
    HU_ROI: pd.Series,
    counts_ROI: pd.Series,
    sp: np.ndarray,
    ROI_name: str,
    dir_histo: Path,
    dir_files: Path,
    save=False,
) -> pd.DataFrame:
    """

    Extract the statistical features from the histogram of a given ROI.

    :param ID: patient ID.
    :type ID: str
    :param HU_ROI: HU values of the histogram.
    :type HU_ROI: pd.Series
    :param counts_ROI: counts associated with the HU values.
    :type counts_ROI: pd.Series
    :param sp: voxel spacing.
    :type sp: np.ndarray
    :param ROI_name: name of the ROI.
    :type ROI_name: str
    :param dir_histo: path to the directory for histogram plots.
    :type dir_histo: Path
    :param dir_files: path to the directory for histogram values Excel files.
    :type dir_files: Path
    :param save: if True, histogram plots and the corresponding Excel files are saved in dir_histo and dir_files respectively;
                 if False, some information is printed.
    :type save: bool

    :return: dataset with statistical features extracted from the ROI histogram.
    :rtype: pd.DataFrame
    """

    # Size of the histogram
    n_size = 1

    # Create histogram
    HU_histo, counts_histo, stats_df = make_histo(
        HU_ROI, counts_ROI, n_size, sp, ROI_name, dir_histo, f"{ID}", save
    )
    diff_file = make_file(HU_histo, counts_histo, dir_files, f"{ID}", save)

    return stats_df


def make_histo(
    HU_ROI_no_nan: pd.Series,
    counts_ROI_no_nan: pd.Series,
    n_size: int,
    sp: np.ndarray,
    ROI_name: str,
    save_path: Path,
    name: str,
    save=False,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Generate a histogram plot using HU values and their corresponding counts for the given ROI.

    :param HU_ROI_no_nan: HU values of the histogram.
    :type HU_ROI_no_nan: pd.Series
    :param counts_ROI_no_nan: counts associated with the HU values.
    :type counts_ROI_no_nan: pd.Series
    :param n_size: bin size for plotting histograms.
    :type n_size: int
    :param sp: voxel spacing.
    :type sp: np.ndarray
    :param ROI_name: name of the ROI.
    :type ROI_name: str
    :param save_path: path to the directory where plot is saved.
    :type save_path: Path
    :param name: name of the plot.
    :type name: str
    :param save: if True, histogram is saved;
                 if False, some information is printed.
    :type save: bool

    :return: HU values, their counts and a dataframe with statistical features of the ROI.
    :rtype: tuple[np.ndarray,np.ndarray,pd.DataFrame]
    """

    # Create histogram plot
    min_HU = min(HU_ROI_no_nan)
    max_HU = max(HU_ROI_no_nan)
    min_counts = min(counts_ROI_no_nan)
    max_counts = max(counts_ROI_no_nan)

    bin_edges = np.arange(min_HU, max_HU + 2 * n_size, n_size)
    count, HU, _ = plt.hist(
        HU_ROI_no_nan,
        bins=bin_edges,
        weights=counts_ROI_no_nan,
        align="left",
        color="black",
        edgecolor="black",
    )
    plt.xlabel("Hounsfield Unit (HU) values")
    plt.ylabel("Counts")
    plt.title(f"{name}", wrap=True, fontsize=15)

    weighted_values = np.repeat(HU_ROI_no_nan, counts_ROI_no_nan)
    plot_stat(weighted_values)

    patient_ID = re.sub("Histo_CT_", "", name)
    patient_ID = re.sub(".xlsx", "", patient_ID)
    patient_ID = re.sub("_Justified", "", patient_ID)

    region = save_path.parent.name
    stats_df = calculate_and_save_statistics(patient_ID, region, weighted_values, sp, ROI_name)

    if save is True:
        print("")
        print("Saving the patient's histogram in ", save_path)
        plt.savefig(save_path / f"{name}.png")
        plt.close()
    else:
        print("The sum of the counts in the ROI is: ", np.sum(counts_ROI_no_nan))
        print(
            f"HU_min= {min_HU}, HU_max= {max_HU}, counts_min= {min_counts}, counts_max= {max_counts}"
        )
        # plt.show()
        # plt.close()

    HU = HU[:-1]

    unique_values, unique_counts = np.unique(HU, return_counts=True)
    max_HU_index = np.argmax(unique_values)
    HU_mas = unique_values[max_HU_index]
    count_mas = unique_counts[max_HU_index]

    return HU, count, stats_df


def make_file(
    HU: pd.Series, count: pd.Series, save_path: Path, name: str, save=False
) -> pd.DataFrame:
    """
    Generate a dataset with the histogram values and the corresponding counts.

    :param HU: HU values of the histogram.
    :type HU: pd.Series
    :param count: counts associated with each HU value.
    :type count: pd.Series
    :param save_path: path to the directory where Excel files are saved.
    :type save_path: Path
    :param name: name of the Excel file.
    :type name: str
    :param save: if True, Excel file is saved;
                 if False, the dataframe is not saved.
    :type save: bool

    :return: dataframe with HU and their corresponding counts.
    :rtype: pd.DataFrame
    """

    HU_file = pd.Series(HU, name="HU")

    counts_file = pd.Series(count, name="Counts")
    df = pd.concat([HU_file, counts_file], axis=1)

    if save:
        print("")
        print("Saving the dataframe in ", save_path)
        print("")
        df.to_excel(save_path / f"{name}.xlsx", index=False)

    return df


def plot_stat(data: np.ndarray) -> None:
    """
    Add statistical features to the current histogram plot.

    The function computes the mean, median and mode of the HU values and adds them on the plot.

    :param data: array containing HU values repeated according to their frequency.
    :type data: np.ndarray

    :return: None
    """

    # Plot the statistical features on the histogram
    mean = np.mean(data)
    median = np.median(data)
    unique_values, unique_counts = np.unique(data, return_counts=True)
    max_count_index = np.argmax(unique_counts)
    max_count_value = unique_counts[max_count_index]
    max_count_hu = unique_values[max_count_index]
    mode = max_count_hu

    plt.axvline(x=mean, color="black", linestyle="dashed", linewidth=1, label=f"Mean:{mean:.2f}")
    plt.axvline(x=mode, color="blue", linestyle="dashed", linewidth=1, label=f"Mode:{mode}")
    plt.axvline(x=median, color="red", linestyle="dashed", linewidth=1, label=f"Median:{median}")

    plt.legend()


def calculate_and_save_statistics(
    histo_name: str, region: str, data: np.ndarray, sp: np.ndarray, ROI_name: str
) -> pd.DataFrame:
    """
    Extract statistical features from the histogram.

    :param histo_name: patient's name you are working on.
    :type histo_name: str
    :param region: name of the region.
    :type region: str
    :param data: array containing HU values repeated according to their frequency.
    :type data: np.ndarray
    :param sp: image voxel spacing.
    :type sp: np.ndarray
    :param ROI_name: name of the ROI.
    :type ROI_name: str


    :return: statistical features extracted from the histogram of each patient.
    :rtype: pd.DataFrame
    """

    # Statistical features to be computed
    minimum = min(data)
    maximum = max(data)
    data_array = np.array(data)
    count_massi = len(data_array[data_array == maximum])
    mean = np.mean(data)
    median = np.median(data)
    unique_values, unique_counts = np.unique(data, return_counts=True)
    max_count_index = np.argmax(unique_counts)
    max_count_value = unique_counts[max_count_index]
    max_count_hu = unique_values[max_count_index]
    mode = max_count_hu
    tot_counts = np.sum(unique_counts)
    volume = tot_counts * (sp[0] * sp[1] * sp[2])
    volume_cc = volume / 1000.0
    std_dev = np.std(data)
    skewness = stats.skew(data)
    kurtosis = stats.kurtosis(data)
    percentile_10 = np.percentile(data, 10)
    percentile_90 = np.percentile(data, 90)
    percentile_95 = np.percentile(data, 95)
    percentile_25 = np.percentile(data, 25)
    percentile_75 = np.percentile(data, 75)

    stats_data = {
        "PatientID": [histo_name],
        "ROI_name": [str(ROI_name)],
        "VoxelSpacingX": [sp[0]],
        "VoxelSpacingY": [sp[1]],
        "VoxelSpacingZ": [sp[2]],
        f"Tot_counts_{region}": [tot_counts],
        f"Volume_mm3_{region}": [volume],
        f"Volume_cc_{region}": [volume_cc],
        f"Min_{region}": [minimum],
        f"Max_{region}": [maximum],
        f"Mean_{region}": [mean],
        f"Mode_{region}": [mode],
        f"Count_Max_{region}": [max_count_value],
        f"Median_{region}": [median],
        f"Std Dev_{region}": [std_dev],
        f"Skewness_{region}": [skewness],
        f"Kurtosis_{region}": [kurtosis],
        f"10th Percentile_{region}": [percentile_10],
        f"25th Percentile_{region}": [percentile_25],
        f"75th Percentile_{region}": [percentile_75],
        f"90th Percentile_{region}": [percentile_90],
        f"95th Percentile_{region}": [percentile_95],
    }

    stats_df = pd.DataFrame(stats_data, index=[0])

    return stats_df


def compare_histo_res(
    HU_ROI_res: pd.Series,
    counts_ROI_res: pd.Series,
    HU_ROI: pd.Series,
    counts_ROI: pd.Series,
    save_path: Path,
    ID: str,
    save=False,
) -> None:
    """
    Generate the plots of the overlap between the histograms of original and resampled CT in semi-log scale.

    :param HU_ROI_res: HU values of the histogram referred to resampled ROI.
    :type HU_ROI_res: pd.Series
    :param counts_ROI_res: HU relative counts referred to resampled ROI.
    :type counts_ROI_res: pd.Series
    :param HU_ROI: HU values of the histogram referred to original ROI.
    :type HU_ROI: pd.Series
    :param counts_ROI: HU relative counts referred to original ROI.
    :type counts_ROI: pd.Series
    :param save_path: path to the directory where the plot will be saved.
    :type save_path: Path
    :param ID: patient ID.
    :type ID: str
    :param save: if True, histogram is saved;
                 if False, no plot is saved.
    :type save: bool

    :return: None
    """

    # Compare histograms (original and resampled) in semi-log scale
    n_size = 1

    fig, ax = plt.subplots(figsize=(8, 6))

    extract_hist(HU_ROI_res, counts_ROI_res, n_size, "b", "Histo_CT_res")
    extract_hist(HU_ROI, counts_ROI, n_size, "k", "Histo_CT")

    plt.xlabel("Hounsfield Unit (HU) values")
    plt.ylabel("Log Counts")
    plt.title(f"Compare Histograms for PZ {ID}")
    plt.yscale("log")
    plt.legend()

    if save:

        print("")
        print("Saving the superposition of histograms in semi-logarithmic scale in ", save_path)
        print("")

        plt.savefig(save_path / f"Compare_{ID}.png")
        plt.close()
        # plt.show()

    # else:

    #     print("")
    #     print("Showing the overlap of the histograms in semi-logarithmic scale.")
    #     print("")

    #     plt.show()
    # plt.close()


def extract_hist(HU: pd.Series, counts: pd.Series, n_size: int, color: str, label: str) -> None:
    """
    Establish the bin size and generate the histogram plot.

    :param HU: HU values of the histogram.
    :type HU: pd.Series
    :param counts: HU relative counts.
    :type counts: pd.Series
    :param n_size: bin size for plotting histograms.
    :type n_size: int
    :param color: color of the histogram.
    :type color: str
    :param label: name of the histogram.
    :type label: str

    :return: None
    """

    bin_edges = np.arange(min(HU), max(HU) + 2 * n_size, n_size)
    plt.hist(HU, bins=bin_edges, weights=counts, align="left", color=color, label=label)
