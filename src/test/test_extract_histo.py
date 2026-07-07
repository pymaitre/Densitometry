"""Module for creating histograms plot and excel files referred to HU and counts in input. 
Statistical features are also estracted.
In case of resampling, histograms about original and resampled ROIs are overlapped. 
"""

import os
import re
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pytest
import pandas as pd
import pytest

REFERENCE_file_ok=pd.read_excel(Path(__file__).parent/"output_test"/"Total_ROI"/"Files_ok"/"1.xlsx")
REFERENCE_directory_out=Path(Path(__file__).parent/"output_test")
REFERENCE_dir_histo=Path(REFERENCE_directory_out) / "Total_ROI" / "Histograms_ok"
REFERENCE_dir_files=Path(REFERENCE_directory_out) / "Total_ROI" / "Files_ok"
REFERENCE_files_nores=pd.read_excel(Path(REFERENCE_directory_out) / "Total_ROI" / "To_be_resampled"/"Files"/"1.xlsx")
REFERENCE_compare_dir=Path(REFERENCE_directory_out) / "Total_ROI" / "To_be_resampled"/"Compare_histo"

@pytest.mark.parametrize("ID,HU_ROI,counts_ROI,sp,ROI_name,dir_histo,dir_files",[("1",REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"],[1,1,3],"GTV-1",REFERENCE_dir_histo,REFERENCE_dir_files)],)
def test_features_ROI(ID:str, HU_ROI:pd.Series, counts_ROI:pd.Series, sp: np.array, ROI_name:str,
                 dir_histo:Path, dir_files:Path, save=False)->pd.DataFrame:
    """
    Function that call histo and file functions

    :param ID: patient's ID.
    :type ID: str
    :param HU_ROI: HU values of the histogram.
    :type HU_ROI: pd.Series
    :param counts_ROI: HU relative counts.
    :type counts_ROI: pd.Series
    :param sp: voxel spacing
    :type sp: np.array
    :param ROI_name: name of the ROI
    :type ROI_name: str
    :param dir_histo: saving directory for histograms.
    :type dir_histo: Path
    :param dir_files: saving directory for excel files.
    :type dir_files: Path
    :param save: if true, histograms, excels files and statistical information
                for all patients are saved in dir_histo and dir_files respectively;
                if false, histograms and statistical information are showed.
    :type save: bool

    :return: statistical features extracted for each patient.
    :rtype: pd.DataFrame
    """

    #Size of the histogram
    n_size=1
    
    #Create histogram
    HU_histo, counts_histo, stats_df = test_make_histo(HU_ROI, counts_ROI, n_size, sp, ROI_name, dir_histo, f"{ID}", save)    
    diff_file = test_make_file(HU_histo, counts_histo, dir_files, f"{ID}", save)

    return stats_df

@pytest.mark.parametrize("HU_ROI_no_nan,counts_ROI_no_nan,n_size,sp,ROI_name,save_path,name",[(REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"],1,[1,1,3],"GTV-1",REFERENCE_dir_histo,"1")],)
def test_make_histo(HU_ROI_no_nan:pd.Series, counts_ROI_no_nan:pd.Series, n_size:int, sp:np.array, ROI_name:str, save_path:Path, name:str, save=False)->tuple[pd.Series,pd.Series,pd.DataFrame]:
    """
    This function has as input HU and counts of the ROI and returns a plot of the histogram.

    :param HU_ROI_no_nan: HU values of the histogram.
    :type HU_ROI_no_nan: pd.Series
    :param counts_ROI_no_nan: HU relative counts.
    :type counts_ROI_no_nan: pd.Series
    :param n_size: bin size for plotting histograms.
    :type n_size: int
    :param save_path: saving directory.
    :type save_path: Path
    :param name: name of the plot.
    :type name: str
    :param save: if true, histogram is saved;
                if false, histogram is showed.
    :type save: bool

    :return: HU values of the histogram for excel file, HU relative counts for excel file and statistical features extracted for each patient.   
    :rtype: tuple[pd.Series,pd.Series,pd.DataFrame]
    """
    
    #Create histogram plot
    min_HU = min(HU_ROI_no_nan)
    max_HU = max(HU_ROI_no_nan)
    min_counts = min(counts_ROI_no_nan)
    max_counts = max(counts_ROI_no_nan)
    
    bin_edges = np.arange(min_HU, max_HU + 2*n_size, n_size)
    count, HU, _ = plt.hist(HU_ROI_no_nan, bins=bin_edges, weights = counts_ROI_no_nan , \
                             align='left', color="black", edgecolor="black")
    plt.xlabel('Hounsfield Unit (HU) values')
    plt.ylabel('Counts')
    plt.title(f'{name}', wrap=True, fontsize=15)
    
    weighted_values = np.repeat(HU_ROI_no_nan, counts_ROI_no_nan)
    test_plot_stat(weighted_values)

    patient_ID = re.sub("Histo_CT_", "", name)
    patient_ID = re.sub(".xlsx", "", patient_ID)
    patient_ID = re.sub("_Justified", "", patient_ID)

    region = save_path.parent.name
    stats_df = test_calculate_and_save_statistics(patient_ID, region, weighted_values, sp, ROI_name)
    
    if save is True:
        print("")
        print("Saving the patient's histogram in ", save_path)
        plt.savefig(save_path / f'{name}.png')
        plt.close()
    else:
        print("The sum of the counts in the ROI is: ", np.sum(counts_ROI_no_nan))
        print(f"HU_min= {min_HU}, HU_max= {max_HU}, counts_min= {min_counts}, counts_max= {max_counts}")
        # plt.show()
        # plt.close()
    
    HU = HU[:-1]
    
    unique_values, unique_counts = np.unique(HU, return_counts=True)
    max_HU_index = np.argmax(unique_values)
    HU_mas = unique_values[max_HU_index]
    count_mas = unique_counts[max_HU_index]

    return HU, count, stats_df

@pytest.mark.parametrize("HU,count,save_path,name",[(REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"],REFERENCE_dir_files,"1")],)
def test_make_file(HU:pd.Series, count:pd.Series, save_path:Path, name:str, save=False)->pd.DataFrame:
    """
    This function has as input histogram values and create the relative dataframe.

    :param HU: HU values of the histogram for excel file.
    :type HU: pd.Series
    :param count: HU relative counts for excel file.
    :type count: pd.Series
    :param save_path: saving directory.
    :type save_path: Path
    :param name: name of the file.
    :type name: str
    :param save: if True, Excel file is saved.
    :type save: bool

    :return: Excel file with HU and relative counts.
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

@pytest.mark.parametrize("data",[(np.repeat(REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"]))],)
def test_plot_stat(data:np.array)->None:
    """
    This function permits to choose which features you want to 
    represent on the plot.

    :param data: array of all HU values, equal to each value for its counts.
    
    :return: None
    """
    
    #Plot the statistical features on the histogram 
    mean = np.mean(data)
    median = np.median(data)
    unique_values, unique_counts = np.unique(data, return_counts=True)
    max_count_index = np.argmax(unique_counts)
    max_count_value = unique_counts[max_count_index]
    max_count_hu = unique_values[max_count_index]
    mode = max_count_hu
    
    plt.axvline(x=mean, color='black', linestyle='dashed', linewidth=1, label=f'Mean:{mean:.2f}')
    plt.axvline(x=mode, color='blue', linestyle='dashed', linewidth=1, label=f'Mode:{mode}')
    plt.axvline(x=median, color='red', linestyle='dashed', linewidth=1, label=f'Median:{median}')

    plt.legend()

@pytest.mark.parametrize("histo_name,region,data,sp,ROI_name",[("1","GTV-1",np.repeat(REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"]),[1,1,3],"GTV-1")],)
def test_calculate_and_save_statistics(histo_name:str, region:str, data:np.array, sp: np.array, ROI_name:str)->pd.DataFrame:
    """
    This function permits to choose which features you want to 
    extract from the histogram.

    :param histo_name: patient you are working on.
    :type histo_name: str
    :param region: name of the region
    :type region: str
    :param data: array of all HU values, equal to each value for its counts.
    :type data: np.array
    :param sp: voxel spacing
    :type sp: np.array
    :param ROI_name: name of the ROI
    :type ROI_name: str


    :return: statistical features extracted for each patient.    
    :rtype: pd.DataFrame   
    """

    
    #Statistical features to be computed
    mini = min(data)
    massi = max(data)
    prova = np.array(data)
    count_massi = len(prova[prova==massi])              
    mean = np.mean(data)
    median = np.median(data)
    unique_values, unique_counts = np.unique(data, return_counts=True)
    max_count_index = np.argmax(unique_counts)
    max_count_value = unique_counts[max_count_index]
    max_count_hu = unique_values[max_count_index]
    mode = max_count_hu
    tot_counts = np.sum(unique_counts)
    volume = tot_counts * (sp[0] * sp[1] * sp[2])
    volume_cc = volume / 1000. 
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
        "VoxelSpacingX" : [sp[0]], 
        "VoxelSpacingY" : [sp[1]], 
        "VoxelSpacingZ" : [sp[2]], 
        f"Tot_counts_{region}": [tot_counts],
        f"Volume_mm3_{region}": [volume],
        f"Volume_cc_{region}": [volume_cc],
        f"Min_{region}": [mini],
        f"Max_{region}": [massi],
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
        f"95th Percentile_{region}": [percentile_95]
    }

    stats_df = pd.DataFrame(stats_data, index=[0])

    return stats_df
    

@pytest.mark.parametrize("HU_ROI_res,counts_ROI_res,HU_ROI,counts_ROI,save_path,ID",[(REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"],REFERENCE_files_nores["HU"],REFERENCE_files_nores["Counts"],REFERENCE_compare_dir,"1")],)
def test_compare_histo_res(HU_ROI_res:pd.Series, counts_ROI_res:pd.Series, HU_ROI:pd.Series, counts_ROI:pd.Series, save_path:Path, ID:str, save=False)->None: 
    """
    This function plots the overlap between the histograms of original and resampled CT
    in semi-log scale.

    :param HU_ROI_res: HU values of the histogram referred to resampled ROI.
    :type HU_ROI_res: pd.Series
    :param counts_ROI_res: HU relative counts referred to resampled ROI.
    :type counts_ROI:res: pd.Series
    :param HU_ROI: HU values of the histogram referred to original ROI.
    :type HU_ROI: pd.Series
    :param counts_ROI: HU relative counts referred to original ROI.
    :type counts_ROI: pd.Series
    :param n_size: bin size for plotting histograms.
    :type n_size: int
    :param save_path: saving directory.
    :type save_path: Path
    :param ID: patient ID.
    :type ID: str
    :param save: if true, histogram is saved;
                if false, histogram is showed.
    :type save: bool
    
    :return: None
    
    """

    #Compare histograms (original and resampled) in semi-log scale
    n_size = 1
    
    fig, ax = plt.subplots(figsize=(8,6))

    test_extract_hist(HU_ROI_res, counts_ROI_res, n_size, 'b', 'Histo_CT_res')
    test_extract_hist(HU_ROI, counts_ROI, n_size, 'k', 'Histo_CT')

    plt.xlabel('Hounsfield Unit (HU) values')
    plt.ylabel('Log Counts')
    plt.title(f"Compare Histograms for PZ {ID}")
    plt.yscale("log")
    plt.legend()
    
    if save:
        
        print("")
        print("Saving the superposition of histograms in semi-logarithmic scale in ", save_path)
        print("")
      
        plt.savefig(save_path /  f"Compare_{ID}.png")
        plt.close()
        # plt.show()
        
    # else:

    #     print("")
    #     print("Showing the overlap of the histograms in semi-logarithmic scale.")
    #     print("")
              
    #     plt.show()
        # plt.close()

@pytest.mark.parametrize("HU,counts,n_size,color,label",[(REFERENCE_file_ok["HU"],REFERENCE_file_ok["Counts"],1,"b","Histo_CT_res")],)
def test_extract_hist(HU:pd.Series, counts:pd.Series, n_size:int, color:str, label:str)->None:
    """
    This function establish the bin size and plots the histogram.

    :param HU_ROI: HU values of the histogram.
    :type HU_ROI: pd.Series
    :param counts_ROI: HU relative counts.
    :type counts_ROI: pd.Series
    :param n_size: bin size for plotting histograms.
    :type n_size: int
    :param color: color of the histogram.
    :type color: str
    :param label: name of the histogram.
    :type label: str
    
    :return: None
    """
    
    bin_edges = np.arange(min(HU), max(HU) + 2*n_size, n_size)
    plt.hist(HU, bins=bin_edges, weights=counts, align='left', color=color, label=label)
