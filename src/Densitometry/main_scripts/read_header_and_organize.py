
# import sys
# sys.path.append("../..")

from Densitometry.dcm_functions import divide_dcm_Bjorn
from Densitometry.dcm_functions import analyze_dcm
from Densitometry.other_functions import *
from pathlib import Path



def main():
    conf = rtv_configuration_file("conf_dcm", save=False)
    
    directory_dcm_in = Path(conf['directory_dcm_in'])
    directory_dcm_out = Path(conf['directory_dcm_out'])
    Path(directory_dcm_out).mkdir(parents=True, exist_ok=True)
    
    directory_out = Path(conf['directory_out'])
    Path(directory_out).mkdir(parents=True, exist_ok=True)
    
    image_modality = conf['image_modality']
    
    # divide = str(input("Do you need to reorganize files in images? (y/n)"))    
    if "y" in conf['divide_dcm'].lower():
        #if True split Dicom files
        organize_ct = divide_dcm_Bjorn.divide_dcm(directory_dcm_in, directory_dcm_out)
        print("")
    else:
        print("Probably the files dcm organized are in: ", directory_dcm_out, "\n")

    df_py = analyze_dcm.find_ct_info(directory_dcm_out, directory_out, image_modality)
    print("")        


if __name__ == "__main__":
    main()





