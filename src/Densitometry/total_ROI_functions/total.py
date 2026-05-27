"""
Module for reading dcm images and obtaining densitometry histograms.
"""

import os
from pathlib import Path
from Densitometry.total_ROI_functions import extract_info as info
from Densitometry.total_ROI_functions import extract_histo as histo
import pandas as pd
import pydicom
from joblib import Parallel, delayed
import numpy as np
import gc
import matplotlib
matplotlib.use("Agg")
  

def get_roi_names(rtstruct_path:Path)->list:
    """
    Generate a list with names of the ROI
    
    :param rtstruct_path: Path to RTSTRUCT file.
    :type rtstruct_path: Path
    
    :return: list with names of the ROI.
    :rtype: list
    """

    #RTSTRUCT
    rtstruct = pydicom.dcmread(rtstruct_path)

    #ROI names
    roi_names = []
    for roi in rtstruct.StructureSetROISequence:
        roi_names.append(roi.ROIName)

    return roi_names

def is_roi_empty(rtst_file:Path, roi_name:str)->bool:
    """
    Check whether the ROI is empty
    
    :param rtst_file: path to RTSTRUCT file
    :type rtst_file: Path
    :param roi_name: name of the ROI
    :type roi_name: str
    
    :return: True if empty, False otherwise
    :rtype: bool
    
    """

    ds = pydicom.dcmread(rtst_file)
    for roi in ds.StructureSetROISequence:
        if roi_name == roi.ROIName:
            roi_number = roi.ROINumber
            break
    
    # Search for ROI Contour Sequence
    if 'ROIContourSequence' in ds:
        for roi_contour in ds.ROIContourSequence:
            # Search for Contour Sequence
            if str(roi_number) == str(roi_contour.ReferencedROINumber):
                if 'ContourSequence' in roi_contour:
                    for contour in roi_contour.ContourSequence:
                        # Check if Contour Data is empty
                        if 'ContourData' in contour and len(contour.ContourData) > 0:
                            return False  # ROI not empty
                else:
                    print(f'ContourSequence not in ROIContourSequence: probably {roi_name} is empty.')
                    break
            else:
                # print(roi_contour.ReferencedROINumber)
                # print(roi_contour.ContourSequence)
                continue
    
    return True  # ROI is empty
    
def find_rt_st(ct_path:Path, rt_kind:str, ID, list_roi:list)->tuple[str, Path] | None:
    """
    This function checks the correspondence in ROI names and returns a tuple with the name of the ROI and the path 
    to RTSTRUCT file.
    
    :param ct_path: Path to CT.
    :type ct_path: Path
    :param rt_kind: type of RT.
    :type rt_kind: str
    :param list_roi: list of ROIs.
    :type list_roi: list
    
    :return: name of the ROI and path to RTSTRUCT (otherwise None)
    :rtype: tuple[str, Path]

    """
    
    try:

        path_rt_structures = [path_rt_st for path_rt_st in list(Path(ct_path).parents[2].glob(f"**/*{rt_kind}*")) if path_rt_st.is_dir() == False]
        
        nomi_con_importanza = {}
        for i in range(0, len(list_roi)):
            nomi_con_importanza[list_roi[i]] = len(list_roi)-i
        print("I'm searching contours with this order: ")
        print(nomi_con_importanza)
        
        for path_rt_st in path_rt_structures:
            print("I found the RTst:")
            print(path_rt_st)

            #List of ROI names
            ROI_names = get_roi_names(path_rt_st)
            
            #Check the same name
            for nome in nomi_con_importanza:

                for ROI_name in ROI_names:

                    if nome in ROI_name:
                        print(f'ROI name {ROI_name} matched with name {nome}.')
                        if is_roi_empty(path_rt_st, ROI_name):
                            continue
                        else:
                            return ROI_name, path_rt_st
       
    except Exception as e:
        print('ROI not founded with error: ', e)
        

def parallel_fun(pz:int, dir_histo_fin:Path, dir_files_fin:Path, df_py:pd.DataFrame, ID_problems:list,
                 new_sp:np.array, rt_kind:str, list_roi:list, directory_out:Path,
                 show_info_all:bool, save_info_all:bool,resampler)->tuple[pd.DataFrame,list]:
    """
    This function is used to obtain the statistical features extracted or append the ID in a list (if there is a problem). 
    This function is implemented at patient-level and used for the parallelization.
    
    :param pz: patient number in list.
    :type pz: int
    :param dir_histo_fin: directory to save information.
    :type dir_histo_fin: Path
    :param dir_files_fin: directory to save information.
    :type dir_files_fin: Path
    :param df_py: input DataFrame.
    :type df_py: pd.DataFrame
    :param ID_problems: list of IDs with problem.
    :type ID_problems: list
    :param new_sp: array with new spatial configuration.
    :type new_sp: np.array
    :param rt_kind: type of RT.
    :type rt_kind: str
    :param list_roi: list of ROIs.
    :type list_roi: list
    :param directory_out: where to save all the information.
    :type directory_out: Path
    :param show_info_all: flag to show information.
    :type show_info_all: bool
    :param save_info_all: flag to save information.
    :type save_info_all: bool
    
    :return: DataFrame with statistical information and a list with ID and problem of the patient
    :rtype: tuple[pd.DataFrame, list]
    
    """
    #ID patient
    ID = df_py.loc[pz,"PatientID"]
    
    if str(ID) not in ID_problems:

        try:
            ct_path = df_py.loc[pz, "Path"]
            ROI_founded, ROI_path = find_rt_st(ct_path, rt_kind, ID, list_roi)
            
            #Old spacing
            old_sp = np.array([df_py.loc[pz,"VoxelSpacingX"], df_py.loc[pz,"VoxelSpacingY"], df_py.loc[pz,"VoxelSpacingZ"]])


            if np.all(old_sp == new_sp):
                
                print("")    
                print("PZ", ID , " ok")
                
                HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all, 
                                                    save_info_all, directory_out, ID, slice=40)
                #Extract information
                stats_df = histo.features_ROI(ID, HU_ROI, counts_ROI, new_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
                         
                return stats_df,None

            else:
                
                print("")    
                print("PZ", ID , " has to be resampled")

                #Store information
                dir_histo_res = Path(directory_out) / "Total_ROI" / "To_be_resampled" / "Histograms"
                Path(dir_histo_res).mkdir(parents=True, exist_ok=True)
            
                dir_files_res = Path(directory_out) / "Total_ROI" / "To_be_resampled" / "Files"
                Path(dir_files_res).mkdir(parents=True, exist_ok=True)
            
                dir_compare_ct_res = Path(directory_out) / "Total_ROI" / "To_be_resampled" / "Compare_histo"
                Path(dir_compare_ct_res).mkdir(parents=True, exist_ok=True)
        
                HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all, 
                                                    save_info_all, directory_out, ID, slice=40)
                histo.features_ROI(ID, HU_ROI, counts_ROI, old_sp, ROI_founded, dir_histo_res, dir_files_res, save_info_all)
                            
        
                print("")    
                print("ANALYZING THE RESAMPLED IMAGE!")
                print("")
        
                HU_ROI_res, counts_ROI_res = info.ROI_res(ct_path, ROI_path, new_sp, ROI_founded, 
                                                            show_info_all, save_info_all, directory_out, ID, resampler,slice=100)
                #Extract information
                stats_df = histo.features_ROI(ID, HU_ROI_res, counts_ROI_res, new_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
                                
                compare = histo.compare_histo_res(HU_ROI_res, counts_ROI_res, HU_ROI, counts_ROI, 
                                                    dir_compare_ct_res, ID, save_info_all)

                return stats_df,None

        except Exception as e:
            
            #If Patient has problems with ROI
            print(f"Patient {ID} has problems with ROI.")
            print(f"{e}")
            

            return None, (ID, str(e))
            
    else:
        print("You caught a patient within the problem's ones.")
        print("")
        
        return None,[ID, "You knew there was an error"]
   

def res_and_create_histo(df_py:pd.DataFrame, ID_problems:list, new_sp:np.array, rt_kind:str, list_roi:list, 
                         directory_out:Path, show_info_all:bool, save_info_all:bool,N_jobs:int,resampler)->Path:
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
    :type df_py: pd.DataFrame
    :param ID_problems: input list of patient's ID with problems.
    :type ID_problems: list
    :param new_sp: new voxel spacing for resampling.
    :type new_sp: np.array
    :param directory_out: the directory of analyses.
    :type directory_out: Path
    :param show_info_all: if true show CT and ROI info.
    :type show_info_all: bool
    :param save_info_all: if true save all histograms and relatives 
                    excel file with HU and counts;
                    if false, histograms are plotted.
    :type save_info_all: bool
    :param n_jobs: number of jobs for parallelization.
    :type n_jobs: int

    :return: directory of all patients df with HU and counts.
    :rtype: Path
    """

    print("The showing variable is set on: ", show_info_all)
    print("The saving variable is set on: ", save_info_all)  
    
    dir_histo_fin = Path(directory_out) / "Total_ROI" / "Histograms_ok"
    Path(dir_histo_fin).mkdir(parents=True, exist_ok=True)

    dir_files_fin = Path(directory_out) / "Total_ROI" / "Files_ok"
    Path(dir_files_fin).mkdir(parents=True, exist_ok=True)

    more_patient_stats_df_total = pd.DataFrame()
    pz_problems = []
    

    #Parallel function
    results = Parallel(n_jobs=N_jobs,timeout=None)(
        delayed(parallel_fun)(
            pz, dir_histo_fin, dir_files_fin, df_py, ID_problems,
            new_sp, rt_kind, list_roi, directory_out, show_info_all, save_info_all,resampler
        )
        for pz in range(len(df_py))
    )
    
    #Store results
    stats_list = [r[0] for r in results if r[0] is not None]
    pz_problems = [r[1] for r in results if r[1] is not None]

    more_patient_stats_df_total = pd.DataFrame()
    for r in stats_list:
        more_patient_stats_df_total = pd.concat([more_patient_stats_df_total, r])
    
    for _, err in results:
        if err is not None:
            ID_problems.append(err[0])
            
            
    
    if len(more_patient_stats_df_total!=0):
        
        #Save information
        excel_file_tot = Path(directory_out) / "Total_ROI" / "Histo_total_stats.xlsx"
        more_patient_stats_df_total.to_excel(excel_file_tot, index=False)
        print(f"All ROI's densitometric features are in {excel_file_tot}")
    
        # else:
        #     print("")
        #     print("Saving the database with the densitometric features of the histograms of the entire region.")
        #     display(more_patient_stats_df_total)

    #If you have problems with patients
    if len(ID_problems)!=0:
        excel_ID_problems = Path(directory_out) / "ID_with_problems.xlsx"
        print("I have problems with patients: ")
        print(ID_problems)
        df_problems = pd.DataFrame(pz_problems, columns=['ID', 'Errore'])
        df_problems.to_excel(excel_ID_problems, index=False)
    else:
        print("\nThere are no problems")
        
    return dir_files_fin


def no_res_parallel_fun(pz:int, dir_histo_fin:Path, dir_files_fin:Path, df_py:pd.DataFrame, ID_problems:list,
                    rt_kind:str, list_roi:list, directory_out:Path, show_info_all:bool, save_info_all:bool)->tuple[pd.DataFrame,list]:
    """
    This function is used to obtain the statistical features extracted or append the ID in a list (if there is a problem). 
    This function is implemented at patient-level and used for the parallelization.
    
    :param pz: patient number in list.
    :type pz: int
    :param dir_histo_fin: directory to save information.
    :type dir_histo_fin: Path
    :param dir_files_fin: directory to save information.
    :type dir_files_fin: Path
    :param df_py: input DataFrame.
    :type df_py: pd.DataFrame
    :param ID_problems: list of IDs with problem.
    :type ID_problems: list
    :param new_sp: aray with new spatial configuration.
    :type new_sp: np.array
    :param rt_kind: type of RT.
    :type rt_kind: str
    :param list_roi: list of ROIs.
    :type list_roi: list
    :param directory_out: where to save all the information.
    :type directory_out: Path
    :param show_info_all: flag to show information.
    :type show_info_all: bool
    :param save_info_all: flag to save information.
    :type save_info_all: bool
    
    :return: DataFrame with statistical information and ID and problem of the patient
    :rtype: tuple[pd.DataFrame,list]
    
    """
    #ID patient
    ID = df_py.loc[pz,"PatientID"]
    
    if str(ID) not in ID_problems:

        try:
            ct_path = df_py.loc[pz, "Path"]
            ROI_founded, ROI_path = find_rt_st(ct_path, rt_kind, ID, list_roi)
            
            #Old spacing
            old_sp = np.array([df_py.loc[pz,"VoxelSpacingX"], df_py.loc[pz,"VoxelSpacingY"], df_py.loc[pz,"VoxelSpacingZ"]])

            print("")    
            print("PZ", ID , " ok")
            
            HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all, 
                                                save_info_all, directory_out, ID, slice=40)
            #Extract information
            stats_df = histo.features_ROI(ID, HU_ROI, counts_ROI, old_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
            
         
            return stats_df,None

        except Exception as e:
            
            #If Patient has problems
            print(f"Patient {ID} has problems with ROI.")
            print(f"{e}")
            
  
            return None, (ID, str(e))
            
    else:

        print("You caught a patient within the problem's ones.")
        print("")
        

        return None,[ID, "You knew there was an error"]

   

def no_res_and_create_histo(df_py:pd.DataFrame, ID_problems:list, rt_kind:str, list_roi:list, 
                         directory_out:Path, show_info_all:bool, save_info_all:bool,N_jobs:int)->Path:
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
    :type df_py: pd.DataFrame
    :param ID_problems: input list of patient's ID with problems.
    :type ID_problems: list
    :param new_sp: new voxel spacing for resampling.
    :type new_sp: np.array
    :param directory_out: the directory of analyses.
    :type directory_out: Path
    :param show_info_all: if true show CT and ROI info.
    :type show_info_all: bool
    :param save_info_all: if true save all histograms and relatives 
                    excel file with HU and counts;
                    if false, histograms are plotted.
    :type save_info_all: bool

    :return: directory of all patients df with HU and counts.
    :rtype: Path
    """

    print("The showing variable is set on: ", show_info_all)
    print("The saving variable is set on: ", save_info_all)  
    
    dir_histo_fin = Path(directory_out) / "Total_ROI" / "Histograms_ok"
    Path(dir_histo_fin).mkdir(parents=True, exist_ok=True)

    dir_files_fin = Path(directory_out) / "Total_ROI" / "Files_ok"
    Path(dir_files_fin).mkdir(parents=True, exist_ok=True)

    more_patient_stats_df_total = pd.DataFrame()
    pz_problems = []

    
    #Parallel function
    results = Parallel(n_jobs=N_jobs,timeout=None)(
        delayed(no_res_parallel_fun)(
            pz, dir_histo_fin, dir_files_fin, df_py, ID_problems, rt_kind, list_roi, directory_out, show_info_all, save_info_all
        )
        for pz in range(len(df_py))
    )
    
    #Store results
    stats_list = [r[0] for r in results if r[0] is not None]
    pz_problems = [r[1] for r in results if r[1] is not None]

    more_patient_stats_df_total = pd.DataFrame()
    for r in stats_list:
        more_patient_stats_df_total = pd.concat([more_patient_stats_df_total, r])
    
    for _, err in results:
        if err is not None:
            ID_problems.append(err[0])
            
    
    if len(more_patient_stats_df_total!=0):
        # if save_all:
        excel_file_tot = Path(directory_out) / "Total_ROI" / "Histo_total_stats.xlsx"
        more_patient_stats_df_total.to_excel(excel_file_tot, index=False)
        print(f"All ROI's densitometric features are in {excel_file_tot}")
    
        # else:
        #     print("")
        #     print("Saving the database with the densitometric features of the histograms of the entire region.")
            # display(more_patient_stats_df_total)

    #If you have problems with Patients
    if len(ID_problems)!=0:
        excel_ID_problems = Path(directory_out) / "ID_with_problems.xlsx"
        print("I have problems with patients: ")
        print(ID_problems)
        df_problems = pd.DataFrame(pz_problems, columns=['ID', 'Errore'])
        df_problems.to_excel(excel_ID_problems, index=False)
    else:
        print("\nThere are no problems")
        
    return dir_files_fin