"""
Module for: 
- reading database of headers DICOM; 
- comparing voxel spacing between patients;
- creating plot about the distribution of each coordinate; 
- establishing a new voxel spacing equal to the most common values.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read_spacing(df_py: pd.DataFrame, directory_out:Path, save_sp:bool)->tuple[float,float,float]:
    """
    Function that calls the database of header dicom where are stored
    all the voxel spacing values of each patient. It establishes the
    new voxel spacing for resampling where is necessary.

    :param df_py: database of headers information.
    :type df_py: pd.DataFrame
    :param directory_out: the directory of analyses.
    :type directory_out: Path
    :param save_sp: if true, saves the histogram plots of each coordinate
                of voxel spacing distribution;
                if false, shows them.
    :type save_sp:bool

    :return: more present (x,y,z) voxel spacing
    :rtype: tuple[float,float,float]

    """
    
    print("Save distribution about voxel spacing is set on: ", save_sp)
    print("")

    bin_size_sp = 0.01
    
    #Extract new_coords
    new_x = histo_spacing(df_py["VoxelSpacingX"], directory_out, "X", bin_size_sp, save_sp)
    new_y = histo_spacing(df_py["VoxelSpacingY"], directory_out, "Y", bin_size_sp, save_sp)
    new_z = histo_spacing(df_py["VoxelSpacingZ"], directory_out, "Z", bin_size_sp, save_sp)

    return new_x, new_y, new_z
    
def histo_spacing(coordinata: pd.Series, directory_out: Path, name: str, n_size: float, save_sp: bool)->float:
    """
    Here are showed or saved the distributions of coordinate
    of the voxel spacing.

    :param coordinata: column of header's database with the list of coordinates.
    :type coordinata: pd.Series
    :param directory_out: the directory of analyses.
    :type directory_out: Path
    :param name: title of histogram and file.
    :type name: str
    :param n_size: bin size of histogram.
    :type n_size: float
    :param save_sp: if true, saves the histogram plots of each coordinate
                of voxel spacing distribution;
                if false, shows them.
    :type save_sp:bool
    
    :return co_mas_in: more present coordinate.
    :rtype co_mas_in: float
    """
  
    
    unique_values_in, unique_counts_in = np.unique(coordinata, return_counts=True)
    max_index_in = np.argmax(unique_counts_in)
    co_mas_in = unique_values_in[max_index_in]
    count_mas_in = unique_counts_in[max_index_in]
    
    if save_sp:
        save_path = directory_out / "Voxel_Analyses"
        Path(save_path).mkdir(parents=True, exist_ok=True)
        
        #Range of the coordinate
        min_co = min(coordinata)
        max_co = max(coordinata)
        print("The number of ", name, " is: ", len(coordinata), "with min: ", min(coordinata), " and max: ", max(coordinata))
        print("The ", name, " more present is: ", co_mas_in, " and has: ", count_mas_in, "counts")

        #Edge
        bin_edges = np.arange(min_co, max_co + 2*n_size, n_size)
        count, co, _ = plt.hist(coordinata, bins=bin_edges, \
                                align='left', color="black", edgecolor="black")
        plt.xlabel('Value of coordinate')
        plt.ylabel('Counts')
        plt.yscale("log")
        plt.title(f'Histogram of {name}')
    
        print(f"The distribution of coordinate {name} is in {save_path}")
        print("")
        plt.savefig(save_path / f'Histogram of {name}.png')
        plt.close()
    
    # else:
        
    #     print(f"I showed the information of coordinate {name}")
    #     print("")
        
        # plt.show()
        # plt.close()

    return co_mas_in


def find_global_scale(df_py: pd.DataFrame,flag_new_spacing:bool)->np.array:
    """
    Create the new voxel spacing given by min_x, min_y and min_z of the given dataset 
    (to be found when flag_new_spacing=="min_global)
    
    :param df_py: input dataframe
    :type df_py: pd.DataFrame
    :param flag_new_spacing: flag to choose the global spacing (min_global, mean_global and max_global)
    :type flag_new_spacing: bool
    
    :return: voxel spacing given by min_x, min_y and min_z (or mean or max)
    :rtype: np.array
    
    """
    if flag_new_spacing=="min_global":
        
        print("I am extracting the global minimum spacing")

        min_x=df_py["VoxelSpacingX"].min()
        min_y=df_py["VoxelSpacingY"].min()
        min_z=df_py["VoxelSpacingZ"].min()
        
    if flag_new_spacing=="mean_global":
        
        print("I am extracting the global mean spacing")

        min_x=df_py["VoxelSpacingX"].mean()
        min_y=df_py["VoxelSpacingY"].mean()
        min_z=df_py["VoxelSpacingZ"].mean()
        
    if flag_new_spacing=="max_global":
        
        print("I am extracting the global maximum spacing")

        min_x=df_py["VoxelSpacingX"].max()
        min_y=df_py["VoxelSpacingY"].max()
        min_z=df_py["VoxelSpacingZ"].max()
    
    new_spacing=np.array([min_x,min_y,min_z])
    
    return new_spacing
    