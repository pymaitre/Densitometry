from pathlib import Path
import os
import sys
import argparse
import yaml
from Densitometry.other_functions import rtv_configuration_file
from Densitometry.specific_ROI_functions import justified as just
from Densitometry.specific_ROI_functions import check_over as over
from Densitometry.specific_ROI_functions import check_rate as rate


def main(conf):
    if conf['directory_out'] is None:
        raise ValueError("Missing directory_out")
    
    #Check if at least one analysis has been selected
    if (conf["specific_ROI_analyses"] is None and conf["over_ROI_analyses"] is None and conf["rate_ROI_analyses"] is None):
        raise ValueError("No analysis has been selected")
    
    directory_out = Path(conf['directory_out'])
    Path(directory_out).mkdir(parents=True, exist_ok=True)  

    dir_files_fin = Path(directory_out) / "Total_ROI" / "Files_ok"
    
    if len( list(dir_files_fin.glob('*.xlsx')) ) != 0:        
        
        just_or_not = conf['specific_ROI_analyses']
        if just_or_not:
            print("Analyzing histograms about specific region is set on: ", just_or_not)
            print("")
    
            delimiter_specific_ROI = conf['specific_ROI_delimiter']
            
            #Check if MaxHU>=MinHU
            if delimiter_specific_ROI[1]<delimiter_specific_ROI[0]:
                raise ValueError("MaxHU is smaller than MinHU")

            just.histo_just(dir_files_fin, directory_out, delimiter_specific_ROI)
            print("") 
                
        else:
            print("You preferred to not analyze the histograms about specific region.")
    
    
        check_over = conf['over_ROI_analyses']
        if check_over:
            print("Analyzing patients searching significative above specific region is set on: ", check_over)
            print("")

            delimiter_over_ROI = conf['over_ROI_delimiter'] 
            over.check_over(dir_files_fin, directory_out, delimiter_over_ROI)
            print("") 
            
        else:
            print("You preferred not to specifically analyze the histograms above the threshold.")
    
    
        check_rate = conf['rate_ROI_analyses']
        if check_rate:
            print("Analyzing patients searching significative outside specific region is set on: ", check_rate)
            print("")

            rate_over_ROI = conf['rate_ROI_delimiter']  
             
            #Check if MaxHU>=MinHU
            if rate_over_ROI[1]<rate_over_ROI[0]:
                raise ValueError("MaxHU is lower than MinHU")  
            
            rate.check_rate(dir_files_fin, directory_out, rate_over_ROI)
            print("")    
                
        else:
            print("You preferred not to specifically analyze the histograms outside the HU thresholds.")
    
    else:
        print(f"You are looking at files in: \n{dir_files_fin}.")
        print("This folder is empty now.")
        print("You have to save all ROI's histogram files before analyze specific regions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script with configurable YAML file.")
    parser.add_argument(
        '--config', 
        type=Path, 
        default= Path(__file__).parents[1] / "conf" / "conf_ROI_analyses.yml", 
        help='Path to the configuration file'
    )
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    main(config)





