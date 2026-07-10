"""

Module for: 
reading database of headers DICOM; 
comparing voxel spacing between patients;
creating plot about the distribution of each coordinate; 
establishing a new voxel spacing equal to the most common values.

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
    :type save_sp: bool

    :return: more present (x,y,z) voxel spacing.
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
    
def histo_spacing(coordinate: pd.Series, directory_out: Path, name: str, n_size: float, save_sp: bool)->float:
    """
    Here are showed or saved the distributions of coordinate
    of the voxel spacing.

    :param coordinate: column of header's database with the list of coordinates.
    :type coordinate: pd.Series
    :param directory_out: the directory of analyses.
    :type directory_out: Path
    :param name: title of histogram and file.
    :type name: str
    :param n_size: bin size of histogram.
    :type n_size: float
    :param save_sp: if True, saves the histogram plots of each coordinate
                of voxel spacing distribution;
                if False, shows them.
    :type save_sp: bool
    
    :return: more present coordinate.
    :rtype: float
    """
  
    
    unique_values_in, unique_counts_in = np.unique(coordinate, return_counts=True)
    max_index_in = np.argmax(unique_counts_in)
    co_mas_in = unique_values_in[max_index_in]
    count_mas_in = unique_counts_in[max_index_in]
    
    if save_sp:
        save_path = directory_out / "Voxel_Analyses"
        Path(save_path).mkdir(parents=True, exist_ok=True)
        
        #Range of the coordinate
        min_co = min(coordinate)
        max_co = max(coordinate)
        print("The number of ", name, " is: ", len(coordinate), "with min: ", min(coordinate), " and max: ", max(coordinate))
        print("The ", name, " more present is: ", co_mas_in, " and has: ", count_mas_in, "counts")

        #Edge
        bin_edges = np.arange(min_co, max_co + 2*n_size, n_size)
        count, co, _ = plt.hist(coordinate, bins=bin_edges, \
                                align='left', color="black", edgecolor="black")
        plt.xlabel('Value of coordinate')
        plt.ylabel('Counts')
        plt.yscale("log")
        plt.title(f'Histogram of {name}')
    
        print(f"The distribution of coordinate {name} is in {save_path}")
        print("")
        plt.savefig(save_path / f'Histogram of {name}.png')
        plt.close()
    
    return co_mas_in


def find_global_scale(df_py: pd.DataFrame,new_spacing_approach:str)->np.array:
    """
    Create the new voxel spacing using one of the following criteria: (min_x, min_y and min_z), (mean_x,mean_y,mean_z) or (max_x,max_y,max_z) of the given dataset.
    
    :param df_py: input dataframe.
    :type df_py: pd.DataFrame
    :param new_spacing_approach: flag to choose the global spacing (min_global, mean_global and max_global).
    :type new_spacing_approach: str
    
    :return: voxel spacing given by min_x, min_y and min_z (or mean or max).
    :rtype: np.array
    
    """
    
    #Find min global scaling
    if new_spacing_approach=="min_global":
        
        print("I am extracting the global minimum spacing")

        new_x=df_py["VoxelSpacingX"].min()
        new_y=df_py["VoxelSpacingY"].min()
        new_z=df_py["VoxelSpacingZ"].min()

        new_spacing=np.array([new_x,new_y,new_z])

        return new_spacing
        
    #Find mean global scaling
    elif new_spacing_approach=="mean_global":
        
        print("I am extracting the global mean spacing")

        new_x=df_py["VoxelSpacingX"].mean()
        new_y=df_py["VoxelSpacingY"].mean()
        new_z=df_py["VoxelSpacingZ"].mean()

        new_spacing=np.array([new_x,new_y,new_z])

        return new_spacing
    
    #Find max global scaling
    elif new_spacing_approach=="max_global":
        
        print("I am extracting the global maximum spacing")

        new_x=df_py["VoxelSpacingX"].max()
        new_y=df_py["VoxelSpacingY"].max()
        new_z=df_py["VoxelSpacingZ"].max()
        
        new_spacing=np.array([new_x,new_y,new_z])
    
        return new_spacing
        
    else:
        raise ValueError(f"Invalid new spacing approach: {new_spacing_approach}")
    
