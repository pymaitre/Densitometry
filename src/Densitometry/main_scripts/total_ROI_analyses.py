#requirements: numpy, pandas, openpyxl, SimpleITK, pydicom, platipy
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
    # conf = rtv_configuration_file("conf_total_ROI", save=False)

    directory_dcm_out = Path(conf['directory_dcm_out'])
    Path(directory_dcm_out).mkdir(parents=True, exist_ok=True)
    
    directory_out = Path(conf['directory_out'])
    Path(directory_out).mkdir(parents=True, exist_ok=True)

    image_modality = conf['image_modality']
    df_py = info_dcm.find_ct_info(directory_dcm_out, directory_out, image_modality)
    print("")            

    
    save_sp = conf['save_spacing_histo']   
    #if save=True create voxel spacing distribution for each dimension
    new_x, new_y, new_z = sp.read_spacing(df_py, directory_out, save_sp)
    print("")
    
    new_sp = np.array([new_x, new_y, new_z])
    print("The most common voxel spacing is: ", new_sp)
    print("")
    

    save_ROI = conf['save_ROI_info']
    rt_kind = conf['rt_kind']
   
    if save_ROI:
        #if True create db with all patient's ROI and relative counts
        df_ROI, df_counts = ROI.all_ROI(df_py, directory_out, rt_kind)          
        print("")
    else:
        print("You chose to not extract all patients ROIs.") 
        print("")


    # ID_problems = ["70230254", "70366136", "433906"] #bilaterali
    ID_problems = conf['ID_problems']
    list_roi = conf['list_roi']

    all = conf['total_ROI_analyses']
    if all:
        print("Analyzing total histograms is set on: ", all)
        
        show_info_all = conf['show_total_ROI_info']
        save_info_all = conf['save_total_ROI_info']
        
        dir_files_fin = tot.res_and_create_histo(df_py, ID_problems, new_sp, rt_kind, list_roi, directory_out, show_info_all, save_info_all)
        print("")
    
    else:
        print("You preferred to not analyze the histograms.")
        print("")        



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





