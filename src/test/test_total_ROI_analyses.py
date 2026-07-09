import matplotlib
matplotlib.use("Agg")
import time
import SimpleITK as sitk
from pathlib import Path
import numpy as np
import pytest
import os
import sys
import argparse
import yaml
from Densitometry.other_functions import rtv_configuration_file
from Densitometry.dcm_functions import analyze_dcm as info_dcm
from Densitometry.total_ROI_functions import analyze_spacing as sp
from Densitometry.total_ROI_functions import analyze_ROI as ROI
from Densitometry.total_ROI_functions import total as tot



def test_main(reference_conf_total_ROI_analyses,patient_directory,reference_dir_out,reference_py_patient_file):
    
    start_time = time.time()
    
    #Read the configuration file
    
    # conf = rtv_configuration_file("conf_total_ROI", save=False)
    
    #Check missing Paths
    #if reference_conf_total_ROI_analyses['directory_dcm_out']==None: 
    #    raise ValueError("Missing directory_dcm_out")
    #elif reference_conf_total_ROI_analyses['directory_out']==None:
    #    raise ValueError("Missing directory_out")
    #elif reference_conf_total_ROI_analyses["py_patient_path"]==None:
    #    raise ValueError("Missing py_patient_path")
    
    reference_conf_total_ROI_analyses['directory_dcm_out']=Path(patient_directory)
    reference_conf_total_ROI_analyses['directory_out']=Path(reference_dir_out)
    reference_conf_total_ROI_analyses["py_patient_path"]=Path(reference_py_patient_file)
    
    directory_dcm_out = Path(reference_conf_total_ROI_analyses['directory_dcm_out'])
    Path(directory_dcm_out).mkdir(parents=True, exist_ok=True)
    
    directory_out = Path(reference_conf_total_ROI_analyses['directory_out'])
    Path(directory_out).mkdir(parents=True, exist_ok=True)
    
    py_patient_file=str(reference_conf_total_ROI_analyses["py_patient_path"])

    image_modality = reference_conf_total_ROI_analyses['image_modality']
    df_py = info_dcm.find_ct_info(directory_dcm_out, directory_out, image_modality,py_patient_file=py_patient_file)
    
    print("")    
    
    #Parallelization
    flag_parallel=reference_conf_total_ROI_analyses["flag_parallel"]
    
    if type(flag_parallel) is not bool:
        raise ValueError("Not valid flag parallel")
    
    if flag_parallel: 
        
        N_jobs=reference_conf_total_ROI_analyses["N_jobs"]
        
        if N_jobs<1 or (type(N_jobs) is not int):
            raise ValueError("Not valid N_jobs")
        
        print(f"Parallelization with N_jobs equal to: {N_jobs}")
    
    else: 
        N_jobs=1
        
        print("No parallelization, working with sequential approach")
    
    
    flag_resampling=reference_conf_total_ROI_analyses["flag_resampling"]
    
    if type(flag_resampling) is not bool:
        raise ValueError("Not valid flag_resampling")

    
    #save_sp = conf['save_spacing_histo'] 
    
    
    save_ROI = reference_conf_total_ROI_analyses['save_ROI_info']
    
    if type(save_ROI) is not bool: 
        raise ValueError("Not valid save_ROI")
    
    rt_kind = reference_conf_total_ROI_analyses['rt_kind']

    ID_problems = reference_conf_total_ROI_analyses['ID_problems']
    
    if save_ROI:
        #If True create db with all patient's ROI and relative counts
        df_ROI, df_counts = ROI.all_ROI(df_py, ID_problems, directory_out, rt_kind)          
        print("")
    else:
        print("You chose to not extract all patients ROIs.") 
        print("")


    list_roi = reference_conf_total_ROI_analyses['roi_name']
    
    if len(list_roi)==0:
        raise ValueError("Missing roi_name")
        

    all = reference_conf_total_ROI_analyses['total_ROI_analyses']
    
    if type(all) is not bool:
        raise ValueError("Not valid total_ROI_analyses")
    
    show_info_all = reference_conf_total_ROI_analyses['show_total_ROI_info']
    save_info_all = reference_conf_total_ROI_analyses['save_total_ROI_info']
          
    if type(show_info_all) is not bool:
        raise ValueError("Not valid show_info_all")
    elif type(save_info_all) is not bool:
        raise ValueError("Not valid save_info_all")

    #Resampling and spacing        
    if flag_resampling:
        
        flag_new_spacing=reference_conf_total_ROI_analyses["flag_new_spacing"]
        
        #Set the resampler
        resampler = getattr(sitk, reference_conf_total_ROI_analyses["resampler"])
        
        #Set new_sp from global values
        if flag_new_spacing=="min_global" or flag_new_spacing=="mean_global" or flag_new_spacing=="max_global":
            
            new_sp=sp.find_global_scale(df_py,flag_new_spacing)
            print("")
            
        #Set new_sp = the most frequent spacing
        elif flag_new_spacing=="frequency":
            
            save_sp = reference_conf_total_ROI_analyses['save_spacing_histo'] 
            new_x, new_y, new_z = sp.read_spacing(df_py, directory_out, save_sp) 
            new_sp = np.array([new_x, new_y, new_z])
            
        #Set new_sp in conf_total_ROI     
        elif flag_new_spacing=="manual":
            
            new_sp=np.array(reference_conf_total_ROI_analyses["new_spacing"])
        else:
            raise ValueError("Not valid flag_new_spacing")
        
        print("The new voxel spacing is: ", new_sp)
        print("")
        
        if all:
            print("Analyzing total histograms is set on: ", all)
            dir_files_fin = tot.res_and_create_histo(df_py, ID_problems, new_sp, rt_kind, list_roi, directory_out, show_info_all, save_info_all,N_jobs,resampler)
            print("")
        
        else:
            print("You preferred to not analyze the histograms.")
            print("")   
        
    else: 
    
        if all:
            print("Analyzing total histograms is set on: ", all)
            dir_files_fin = tot.no_res_and_create_histo(df_py, ID_problems, rt_kind, list_roi, directory_out, show_info_all, save_info_all,N_jobs) 
            print("")
        
        else:
            print("You preferred to not analyze the histograms.")
            print("")   
        
        
    #Execution time
    end_time = time.time()  
    elapsed_time = end_time - start_time 
    print(f"Total execution time: {elapsed_time:.2f} seconds")     







