from pathlib import Path
import os
import sys
import argparse
import yaml
import pytest
from test_other_functions import rtv_configuration_file
from Densitometry.specific_ROI_functions import justified as just
from Densitometry.specific_ROI_functions import check_over as over
from Densitometry.specific_ROI_functions import check_rate as rate


def test_main(reference_conf_ROI_analyses,reference_dir_out):
    
    #Check Path
    #if reference_conf_ROI_analyses['directory_out']==None: 
    #    raise ValueError("Missing directory out in the configuration file")
    
    if (reference_conf_ROI_analyses["specific_ROI_analyses"] is None and reference_conf_ROI_analyses["over_ROI_analyses"] is None and reference_conf_ROI_analyses["rate_ROI_analyses"] is None):
        raise ValueError("No analysis has been selected")

    
    reference_conf_ROI_analyses['directory_out']=reference_dir_out
    
    
    directory_out = Path(reference_conf_ROI_analyses['directory_out'])
    
    
    Path(directory_out).mkdir(parents=True, exist_ok=True)  

    dir_files_fin = Path(directory_out) / "Total_ROI" / "Files_ok"
    
    if len( list(dir_files_fin.glob('*.xlsx')) ) != 0:        
        
        just_or_not = reference_conf_ROI_analyses['specific_ROI_analyses']
        if just_or_not:
            print("Analyzing histograms about specific region is set on: ", just_or_not)
            print("")
    
            delimiter_specific_ROI = reference_conf_ROI_analyses['specific_ROI_delimiter']
            
            #Check if MaxHU>=MinHU
            if delimiter_specific_ROI[1]<delimiter_specific_ROI[0]:
                raise ValueError("MaxHU is smaller than MinHU") 
            

            just.histo_just(dir_files_fin, directory_out, delimiter_specific_ROI)
            print("") 
                
        else:
            print("You preferred to not analyze the histograms about specific region.")
    
    
        check_over = reference_conf_ROI_analyses['over_ROI_analyses']
        if check_over:
            print("Analyzing patients searching significative above specific region is set on: ", check_over)
            print("")

            delimiter_over_ROI = reference_conf_ROI_analyses['over_ROI_delimiter'] 
            over.check_over(dir_files_fin, directory_out, delimiter_over_ROI)
            print("") 
            
        else:
            print("You preferred not to specifically analyze the histograms above the threshold.")
    
    
        check_rate = reference_conf_ROI_analyses['rate_ROI_analyses']
        if check_rate:
            print("Analyzing patients searching significative outside specific region is set on: ", check_rate)
            print("")

            rate_over_ROI = reference_conf_ROI_analyses['rate_ROI_delimiter']    
            
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







