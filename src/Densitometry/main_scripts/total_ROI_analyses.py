#requirements: numpy, pandas, openpyxl, SimpleITK, pydicom, platipy
import matplotlib
matplotlib.use("Agg")
import time
from pathlib import Path
import numpy as np
import os
import sys
# path_func = Path(Path(os.getcwd()).parent.parent.parent)
# sys.path.append(str(path_func) )

import argparse
import yaml

from Densitometry.other_functions import rtv_configuration_file

from Densitometry.dcm_functions import analyze_dcm as info_dcm

from Densitometry.total_ROI_functions import analyze_spacing as sp
from Densitometry.total_ROI_functions import analyze_ROI as ROI
from Densitometry.total_ROI_functions import total as tot



def main(conf):
    
    #Time to see how long does it take to extract all densitometric information
    start_time = time.time()
    
    # conf = rtv_configuration_file("conf_total_ROI", save=False)

    directory_dcm_out = Path(conf['directory_dcm_out'])
    Path(directory_dcm_out).mkdir(parents=True, exist_ok=True)
    
    directory_out = Path(conf['directory_out'])
    Path(directory_out).mkdir(parents=True, exist_ok=True)

    image_modality = conf['image_modality']
    df_py = info_dcm.find_ct_info(directory_dcm_out, directory_out, image_modality)
    print("")    
    
    #Parallelization
    flag_parallel=conf["flag_parallel"]
    
    if flag_parallel: 
        
        N_jobs=conf["N_jobs"]
        
        print(f"Parallelization with N_jobs equal to: {N_jobs}")
    
    else: 
        N_jobs=1
        
        print("No parallelization, working with sequential approach")
    
    
    flag_resampling=conf["flag_resampling"]
    flag_new_spacing=conf["flag_new_spacing"]
    
    

    
    #save_sp = conf['save_spacing_histo'] 
    
    
    #Resampling and spacing        
    if flag_resampling:
        
        #If True: new_spacing from the distribution, else: provide the new spacing
        if flag_new_spacing:
            
            save_sp = conf['save_spacing_histo'] 
            new_x, new_y, new_z = sp.read_spacing(df_py, directory_out, save_sp) # NO more necessary ==> you insert the desired voxel_spacing
            print("")
            new_sp = np.array([new_x, new_y, new_z])
            
        else:
            
            new_sp=np.array(conf["new_spacing"])
        
        
        print("The new voxel spacing is: ", new_sp)
        print("")
        

        save_ROI = conf['save_ROI_info']
        rt_kind = conf['rt_kind']
    
    
        # ID_problems = ["70230254", "70366136", "433906"] #bilaterali
        ID_problems = conf['ID_problems']
        
        if save_ROI:
            #if True create db with all patient's ROI and relative counts
            df_ROI, df_counts = ROI.all_ROI(df_py, ID_problems, directory_out, rt_kind)          
            print("")
        else:
            print("You chose to not extract all patients ROIs.") 
            print("")


        list_roi = conf['list_roi']

        all = conf['total_ROI_analyses']
        if all:
            print("Analyzing total histograms is set on: ", all)
            
            show_info_all = conf['show_total_ROI_info']
            save_info_all = conf['save_total_ROI_info']
            
            dir_files_fin = tot.res_and_create_histo(df_py, ID_problems, new_sp, rt_kind, list_roi, directory_out, show_info_all, save_info_all,N_jobs)
            print("")
        
        else:
            print("You preferred to not analyze the histograms.")
            print("")   
        
        #Count the total extraction time
        end_time = time.time()  
        elapsed_time = end_time - start_time 
        print(f"Total execution time: {elapsed_time:.2f} seconds")     
        

    else: 
        
        save_ROI = conf['save_ROI_info']
        rt_kind = conf['rt_kind']
    
    
        # ID_problems = ["70230254", "70366136", "433906"] #bilaterali
        ID_problems = conf['ID_problems']
        
        if save_ROI:
            #if True create db with all patient's ROI and relative counts
            df_ROI, df_counts = ROI.all_ROI(df_py, ID_problems, directory_out, rt_kind) #QUI          
            print("")
        else:
            print("You chose to not extract all patients ROIs.") 
            print("")


        list_roi = conf['list_roi']

        all = conf['total_ROI_analyses']
        if all:
            print("Analyzing total histograms is set on: ", all)
            
            show_info_all = conf['show_total_ROI_info']
            save_info_all = conf['save_total_ROI_info']
            
            dir_files_fin = tot.no_res_and_create_histo(df_py, ID_problems, rt_kind, list_roi, directory_out, show_info_all, save_info_all,N_jobs) #QUI
            print("")
        
        else:
            print("You preferred to not analyze the histograms.")
            print("")   
        
        #Count the total extraction time
        end_time = time.time()  
        elapsed_time = end_time - start_time 
        print(f"Total execution time: {elapsed_time:.2f} seconds")     



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script with configurable YAML file.")
    parser.add_argument(
        '--config', 
        type=Path, 
        # default=Path("/Users") / "dimay_kerby" / "dcm_folder" / "src" / "dcm_folder" / "conf" / "conf_dcm.yml", 
        # default=Path(r"C:\Users\belardo.alfonso\Desktop\GitHub\Densitometry_Alfo\src\Densitometry\conf\conf_total_ROI.yml"),
        default= Path(__file__).parents[1] / "conf" / "conf_total_ROI.yml", 
        help='Path to the configuration file'
    )
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    main(config)





