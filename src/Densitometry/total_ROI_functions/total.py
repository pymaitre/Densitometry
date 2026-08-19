"""
Module for:
reading DICOM images and obtaining densitometric histograms.
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
    Return a list of ROI names.
    
    :param rtstruct_path: path to the RTSTRUCT file.
    :type rtstruct_path: Path
    
    :return: list of ROI names.
    :rtype: list
    """

    #RTSTRUCT
    rtstruct = pydicom.dcmread(rtstruct_path)

    #ROI names
    roi_names = []
    for roi in rtstruct.StructureSetROISequence:
        roi_names.append(roi.ROIName)

    roi_names.sort()
    return roi_names

def is_roi_empty(rtst_file:Path, roi_name:str)->bool:
    """
    Check whether the ROI is empty.
    
    :param rtst_file: path to the RTSTRUCT file.
    :type rtst_file: Path
    :param roi_name: name of the ROI.
    :type roi_name: str
    
    :return: True if the ROI is empty, False otherwise.
    :rtype: bool
    """
    
    roi_number=None

    ds = pydicom.dcmread(rtst_file)
    for roi in ds.StructureSetROISequence:
        if roi_name == roi.ROIName:
            roi_number = roi.ROINumber
            break
    if roi_number is None:
        raise ValueError(f"ROI '{roi_name}' not found in Structure Set")

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
    
def find_rt_st(ct_path:Path, rt_kind:str, list_roi:list)->tuple[str, Path] | None:
    """
    Return a matching ROI name in the available RTSTRUCT file and the Path to the file itself.
    
    :param ct_path: path to the CT directory.
    :type ct_path: Path
    :param rt_kind: type of RT.
    :type rt_kind: str
    :param list_roi: list of ROI names.
    :type list_roi: list
    
    :return: tuple containing the matching ROI name and the path to the RTSTRUCT file.
    :rtype: tuple[str, Path] | None
    """
    
    try:

        path_rt_structures = [path_rt_st for path_rt_st in list(Path(ct_path).parents[2].glob(f"**/*{rt_kind}*")) if path_rt_st.is_dir() == False]
        
        names_with_importance = {}
        for i in range(0, len(list_roi)):
            names_with_importance[list_roi[i]] = len(list_roi)-i
        print("I'm searching contours with this order: ")
        print(names_with_importance)
        
        for path_rt_st in path_rt_structures:
            print("I found the RTst:")
            print(path_rt_st)

            #List of ROI names
            ROI_names = get_roi_names(path_rt_st)
            
            #Check the same name
            for name in names_with_importance:

                for ROI_name in ROI_names:

                    if name in ROI_name:
                        print(f'ROI name {ROI_name} matched with name {name}.')
                        if is_roi_empty(path_rt_st, ROI_name):
                            continue
                        else:
                            return ROI_name, path_rt_st
       
    except Exception as e:
        print('ROI not found with error: ', e)
        

def parallel_fun(pz:int, input_parallel_dictionary:dict)->tuple[pd.DataFrame,list]:
    """
    Obtain the statistical features from the HU distribution of the ROI. 
    If there are problems, the patient ID is appended to a list. 
    This function operates at patient level and can be used for a parallel execution. 
    It is applied when image resampling is performed.
        
    :param pz: input row index of the dataset.
    :type pz: int
    :param input_parallel_dictionary: input dictionary for the parallel function.
    :type input_parallel_dictionary: dict

    :return: dataframe with statistical information and list of patient IDs and the corresponding problems.
    :rtype: tuple[pd.DataFrame, list]
    
    """
    #Extract information from dictionary
    
    dir_histo_fin=Path(input_parallel_dictionary["directory_histo_fin"])
    dir_files_fin=Path(input_parallel_dictionary["directory_files_fin"])
    df_py=pd.DataFrame(input_parallel_dictionary["dataset"])
    ID_problems=list(input_parallel_dictionary["ID_problems"])
    new_sp=np.array(input_parallel_dictionary["new_sp"])
    rt_kind=str(input_parallel_dictionary["rt_kind"])
    list_roi=list(input_parallel_dictionary["list_roi"])
    directory_out=Path(input_parallel_dictionary["directory_out"])
    show_info_all=bool(input_parallel_dictionary["show_info_all"])
    save_info_all=bool(input_parallel_dictionary["save_info_all"])
    resampler=input_parallel_dictionary["resampler"]
    
    #Check if pz is acceptable
    if not pz<len(df_py):
        raise ValueError(f"{pz} index not valid")
  
    #ID patient
    ID = df_py.loc[pz,"PatientID"]
    
    if str(ID) not in ID_problems:

        try:
            ct_path = df_py.loc[pz, "Path"]
            ROI_founded, ROI_path = find_rt_st(ct_path, rt_kind, list_roi)
            
            #Old spacing
            old_sp = np.array([df_py.loc[pz,"VoxelSpacingX"], df_py.loc[pz,"VoxelSpacingY"], df_py.loc[pz,"VoxelSpacingZ"]])


            if np.all(old_sp == new_sp):
                
                print("")    
                print("PZ", ID , " ok")
                
                HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all,slice=40)
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
        
                HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all,slice=40)
                
                histo.features_ROI(ID, HU_ROI, counts_ROI, old_sp, ROI_founded, dir_histo_res, dir_files_res, save_info_all)
                            
        
                print("")    
                print("ANALYZING THE RESAMPLED IMAGE!")
                print("")
        
                HU_ROI_res, counts_ROI_res = info.ROI_res(ct_path, ROI_path, new_sp, ROI_founded, 
                                                            show_info_all, resampler,slice=100)
                #Extract information
                stats_df = histo.features_ROI(ID, HU_ROI_res, counts_ROI_res, new_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
                                
                compare = histo.compare_histo_res(HU_ROI_res, counts_ROI_res, HU_ROI, counts_ROI, 
                                                    dir_compare_ct_res, ID, save_info_all)

                return stats_df,None

        except Exception as e:
            
            #If Patient has problems with ROI
            print(f"Patient {ID} has problems with ROI.")
            print(f"{e}")
            

            return None, [ID, str(e)]
            
    else:
        print("You caught a patient within the problem's ones.")
        print("")
        
        return None,[ID, "You knew there was an error"]
   

def res_and_create_histo(df_py:pd.DataFrame, ID_problems:list, new_sp:np.array, rt_kind:str, list_roi:list, 
                         directory_out:Path, show_info_all:bool, save_info_all:bool,N_jobs:int,resampler:int)->Path:
    """
    Extract the statistical features from the HU distribution of the selected ROI. 
    The following workflow is performed:
    - CT image and ROI are optionally displayed; 
    - the specified ROI is identified;
    - image resampling is performed and the datasets and histograms of both the original and resampled image are obtained;
    - original and resampled histograms are compared;
    - a DataFrame with the features of all patients is created.

    :param df_py: dataset of header information.
    :type df_py: pd.DataFrame
    :param ID_problems: list of patient IDs with known problems.
    :type ID_problems: list
    :param new_sp: new voxel spacing used for resampling.
    :type new_sp: np.array
    :param rt_kind: type of RT.
    :type rt_kind: str
    :param list_roi: list of ROI names.
    :type list_roi: list
    :param directory_out: output directory for the analyses.
    :type directory_out: Path
    :param show_info_all: if True, CT and ROI information are displayed.
    :type show_info_all: bool
    :param save_info_all: if True, all histograms and corresponding Excel files containing HU values and counts are saved;
                          if False, histograms are plotted.
    :type save_info_all: bool
    :param N_jobs: number of jobs used for parallelization.
    :type N_jobs: int
    :param resampler: resampling interpolation method.
    :type resampler: int

    :return: path to the output directory containing datasets with HU values and their counts for all patients.
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

    #Create the input dictionary for the parallel function
    input_parallel_dictionary={
        "directory_histo_fin": dir_histo_fin,
        "directory_files_fin": dir_files_fin,
        "dataset": df_py,
        "ID_problems": ID_problems,
        "new_sp": new_sp,
        "rt_kind": rt_kind,
        "list_roi": list_roi,
        "directory_out": directory_out,
        "show_info_all": show_info_all,
        "save_info_all": save_info_all,
        "resampler": resampler
        }
    
    #Parallel function
    results = Parallel(n_jobs=N_jobs,timeout=None)(
        delayed(parallel_fun)(
            pz, input_parallel_dictionary
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
            
            
    
    if len(more_patient_stats_df_total)!=0:
        
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


def no_res_parallel_fun(pz:int, input_dictionary_parallel:dict)->tuple[pd.DataFrame,list]:
    """
    Obtain the statistical features from the HU distribution of the ROI. 
    If there are problems, the patient ID is appended to a list. 
    This function operates at patient level and can be used for a parallel execution. 
    It is applied when resampling is not performed.
    
    :param pz: input row index of the dataset.
    :type pz: int
    :param input_dictionary_parallel: input dictionary for the parallel function.
    :type input_dictionary_parallel: dict
    
    :return: dataframe with statistical information and list of patient IDs with the corresponding problems.
    :rtype: tuple[pd.DataFrame,list]
    
    """

    #Extract information from the dictionary
                      
    dir_histo_fin=Path(input_dictionary_parallel["directory_histo_fin"])
    dir_files_fin=Path(input_dictionary_parallel["directory_files_fin"])
    df_py=pd.DataFrame(input_dictionary_parallel["dataset"])
    ID_problems=list(input_dictionary_parallel["ID_problems"])
    rt_kind=str(input_dictionary_parallel["rt_kind"])
    list_roi=list(input_dictionary_parallel["list_roi"])
    directory_out=Path(input_dictionary_parallel["directory_out"])
    show_info_all=bool(input_dictionary_parallel["show_info_all"])
    save_info_all=bool(input_dictionary_parallel["save_info_all"])
    
        
    #Check if pz is acceptable
    if not pz<len(df_py):
        raise ValueError(f"{pz} index not valid")
                      
    #ID patient
    ID = df_py.loc[pz,"PatientID"]
    
    if str(ID) not in ID_problems:

        try:
            ct_path = df_py.loc[pz, "Path"]
            ROI_founded, ROI_path = find_rt_st(ct_path, rt_kind, list_roi)
            
            #Old spacing
            old_sp = np.array([df_py.loc[pz,"VoxelSpacingX"], df_py.loc[pz,"VoxelSpacingY"], df_py.loc[pz,"VoxelSpacingZ"]])

            print("")    
            print("PZ", ID , " ok")
            
            HU_ROI, counts_ROI = info.ROI_ok(ct_path, ROI_path, ROI_founded, show_info_all,slice=40)
            
            #Extract information
            stats_df = histo.features_ROI(ID, HU_ROI, counts_ROI, old_sp, ROI_founded, dir_histo_fin, dir_files_fin, save_info_all)
            
         
            return stats_df,None

        except Exception as e:
            
            #If Patient has problems
            print(f"Patient {ID} has problems with ROI.")
            print(f"{e}")
            
  
            return None, [ID, str(e)]
            
    else:

        print("You caught a patient within the problem's ones.")
        print("")
        

        return None,[ID, "You knew there was an error"]

   

def no_res_and_create_histo(df_py:pd.DataFrame, ID_problems:list, rt_kind:str, list_roi:list, 
                         directory_out:Path, show_info_all:bool, save_info_all:bool,N_jobs:int)->Path:
    """
    Extract statistical features from the HU distribution of the selected ROI. 
    The following workflow is performed:
    - CT and ROI are optionally displayed; 
    - the specified ROI is found;
    - datasets and histograms of the original image are obtained;
    - a dataset containing the features of all patients is generated.

    :param df_py: dataset of header information.
    :type df_py: pd.DataFrame
    :param ID_problems: input list of patient IDs with known problems.
    :type ID_problems: list
    :param rt_kind: type of RT.
    :type rt_kind: str
    :param list_roi: list of the ROI names.
    :type list_roi: list
    :param directory_out: output directory for the analyses.
    :type directory_out: Path
    :param show_info_all: if True CT and ROI information are displayed.
    :type show_info_all: bool
    :param save_info_all: if True save all histograms and corresponding Excel files containing HU values and counts;
                          if False, histograms are plotted.
    :type save_info_all: bool
    :param N_jobs: number of jobs used for parallelization.
    :type N_jobs: int

    :return: path to the output directory containing datasets with HU values and their counts for all patients.
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

    #Create the input dictionary for the parallel function
    input_parallel_dictionary={
        "directory_histo_fin": dir_histo_fin,
        "directory_files_fin": dir_files_fin,
        "dataset": df_py,
        "ID_problems": ID_problems,
        "rt_kind": rt_kind,
        "list_roi": list_roi,
        "directory_out": directory_out,
        "show_info_all": show_info_all,
        "save_info_all": save_info_all,
    }

    
    #Parallel function
    results = Parallel(n_jobs=N_jobs,timeout=None)(
        delayed(no_res_parallel_fun)(
            pz, input_parallel_dictionary
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
            
    
    if len(more_patient_stats_df_total)!=0:
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
