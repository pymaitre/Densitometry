import matplotlib
matplotlib.use("Agg")
import time
import SimpleITK as sitk
from pathlib import Path
import numpy as np
import os
import sys
import argparse
import yaml
from Densitometry.other_functions import rtv_configuration_file
from Densitometry.dcm_functions import analyze_dcm as info_dcm
from Densitometry.total_ROI_functions import analyze_spacing as sp
from Densitometry.total_ROI_functions import analyze_ROI as ROI
from Densitometry.total_ROI_functions import total as tot



def main(conf):
    
    start_time = time.time()
    
    #Read the configuration file
    
    if conf['directory_dcm_out'] is None:
        raise ValueError("Missing directory_dcm_out")
    if conf['directory_out'] is None:
        raise ValueError("Missing directory_out")
    if conf['py_patient_path'] is None:
        raise ValueError("Missing py_patient_path")

    directory_dcm_out = Path(conf['directory_dcm_out'])
    Path(directory_dcm_out).mkdir(parents=True, exist_ok=True)
    
    directory_out = Path(conf['directory_out'])
    Path(directory_out).mkdir(parents=True, exist_ok=True)
    
    py_patient_file=str(conf["py_patient_path"])

    image_modality = conf['image_modality']
    df_py = info_dcm.find_ct_info(directory_dcm_out, image_modality,py_patient_file=py_patient_file)
    
    print("")    
    
    #Parallelization
    flag_parallel=conf["flag_parallel"]
    
    if not isinstance(flag_parallel, bool):
        raise ValueError("Not valid flag parallel")
    
    
    if flag_parallel: 
        
        N_jobs=conf["N_jobs"]
        
        if N_jobs<1 or not isinstance(N_jobs, int):
            raise ValueError("Not valid N_jobs")
        
        print(f"Parallelization with N_jobs equal to: {N_jobs}")
    
    else: 
        N_jobs=1
        
        print("No parallelization, working with sequential approach")
    
    
    flag_resampling=conf["flag_resampling"]
    
    if isinstance(flag_resampling, bool):
        raise ValueError("Not valid flag_resampling")
    
    #save_sp = conf['save_spacing_histo'] 
    
    save_ROI = conf['save_ROI_info']
    
    if not isinstance(save_ROI,bool): 
        raise ValueError("Not valid save_ROI")
    
    rt_kind = conf['rt_kind']

    ID_problems = conf['ID_problems']
    
    if save_ROI:
        #If True create db with all patient's ROI and relative counts
        df_ROI, df_counts = ROI.all_ROI(df_py, ID_problems, directory_out, rt_kind)          
        print("")
    else:
        print("You chose to not extract all patients ROIs.") 
        print("")
        
    list_roi = conf['list_roi']
    
    if len(list_roi)==0:
        raise ValueError("Empty list_roi")

    all = conf['total_ROI_analyses']
    if type(all) is not bool:
            raise ValueError("Not valid total_ROI_analyses")
    
    show_info_all = conf['show_total_ROI_info']
    save_info_all = conf['save_total_ROI_info']
    
    if type(show_info_all) is not bool:
        raise ValueError("Not valid show_info_all")
    elif type(save_info_all) is not bool:
        raise ValueError("Not valid save_info_all")

    #Resampling and spacing        
    if flag_resampling:
        
        flag_new_spacing=conf["flag_new_spacing"]
        
        #Set the resampler
        resampler = getattr(sitk, conf["resampler"])
        
        #Set new_sp from global values
        if flag_new_spacing=="min_global" or flag_new_spacing=="mean_global" or flag_new_spacing=="max_global":
            
            new_sp=sp.find_global_scale(df_py,flag_new_spacing)
            print("")
            
        #Set new_sp = the most frequent spacing
        elif flag_new_spacing=="frequency":
            
            save_sp = conf['save_spacing_histo'] 
            new_x, new_y, new_z = sp.read_spacing(df_py, directory_out, save_sp) 
            new_sp = np.array([new_x, new_y, new_z])
            
        #Set new_sp in conf_total_ROI     
        elif flag_new_spacing=="manual":
            
            new_sp=np.array(conf["new_spacing"])
        
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



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script with configurable YAML file.")
    parser.add_argument(
        '--config', 
        type=Path, 
        default= Path(__file__).parents[1] / "conf" / "conf_total_ROI.yml", 
        help='Path to the configuration file'
    )
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    main(config)





