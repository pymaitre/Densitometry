"""
Module for: 
- reading and showing CT converting it into an array;
- reading all the ROIs from the relative RTst;
- creating a database with all ROIs for patients;
- creating a database with counts of ROIs found.
"""

import os
from pathlib import Path
from Densitometry.total_ROI_functions import extract_info as info
import matplotlib.pyplot as plt
import pandas as pd
import pydicom


def all_ROI(df_py, directory_out, rt_kind):
    """
    Read all ROIs from RTst linked to CT (in directory named by ID).
    This function create a dataframe where each row has PatientID
    and all his ROIs.
    A dataframe with all ROIs and their counts is also created.

    :param df_py: database of headers information.
    :param directory_out: the directory of analyses.
    :param save: if true, saves the database of ROI for each patient
                and the other one of their counts;
                if false, shows them.

    :return df_ROI: database of ROI for each patient.
    :return df_counts: database of ROI's counts.
    """
    
    try:
        df_ROI = pd.read_excel(Path(directory_out) / "ROI_tot_pz.xlsx")
        print("")
        print("I read the dataframe with all the ROIs of each patient")
        print("")    

        # display(df_ROI)
        # display(df_ROI.loc[0,:].dropna())

        df_counts = pd.read_excel(Path(directory_out) / "counts_ROI.xlsx")
        print("")
        print("I read the dataframe with the ROI counts for each patient")
        print("")  

        # display(df_counts)
    
    except:
        print("I am going to analyse all patient's ROIs.")

        show_CT_ROI=False
        slice=0
        df_ROI = pd.DataFrame()
    
        for pz in range(0, len(df_py)):
            ID =  df_py.loc[pz,"PatientID"]
            ct_path = df_py.loc[pz, "Path"]
            
            # CT, CT_arr = info.read_and_show_ct(ct_path, show_CT_ROI, slice)    
            # rt_folder = (Path(ct_path).parent / "RTst")
            # TODO: check RTst path by name in conf.  
            rtstruct_path = list(Path(ct_path).parents[1].glob(f"**/*{rt_kind}*.dcm"))[0]
            # rt_path = ct_path.parent.glob("RS*")
            # print("La RTst si trova in: ", rt_path)
            # rt = info.dtn.read_dicom_rtstruct(rt_path, CT)    
            # print(rt)
    
            contour=[]
            
            rtstruct = pydicom.dcmread(rtstruct_path)

            for roi in rtstruct.StructureSetROISequence:
                contour.append(roi.ROIName)
                
            print("ROIs of patient ", ID , " are: ", contour)
            print("")
            
            df_ROI_1pz = pd.DataFrame(
                [contour],
                index=[ID],
            )
            df_ROI = pd.concat([df_ROI, df_ROI_1pz])
                    
        # print(df_ROI)
        
        with pd.ExcelWriter(Path(directory_out) / "ROI_tot_pz.xlsx") as writer:
            df_ROI.to_excel(writer, index=True)
        print("")
        print("Saved the dataframe with all the ROIs of each patient")
        print("")    
    
        series = pd.Series(df_ROI.values.flatten(), name='Counts').dropna()
        unique_values_counts = series.value_counts()
        # display(unique_values_counts)
        
        with pd.ExcelWriter(Path(directory_out) / "counts_ROI.xlsx") as writer:
            unique_values_counts.to_excel(writer, index=True)
        df_counts = pd.read_excel(Path(directory_out) / "counts_ROI.xlsx")
        print("")
        print("Saved the dataframe with the ROI counts of each patient")
        print("")    


    return df_ROI, df_counts