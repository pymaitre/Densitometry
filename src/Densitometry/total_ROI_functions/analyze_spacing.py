"""
Module for: 
- reading a dataset of DICOM header information; 
- analyzing the voxel spacing distribution across patients;
- creating plots of the voxel spacing distribution along each coordinate; 
- defining a new voxel spacing, according to different criteria.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read_spacing(df_py: pd.DataFrame, directory_out:Path, save_sp:bool)->tuple[float,float,float]:
    """
    Analyze the distribution of voxel spacing values in the given dataset. 
    It returns the most frequent voxel spacing value along each axis, 
    which can be used as the new voxel spacing in case of image resampling.

    :param df_py: dataframe of header information.
    :type df_py: pd.DataFrame
    :param directory_out: directory of the analyses.
    :type directory_out: Path
    :param save_sp: if True, the histogram plots of the voxel spacing distribution along each axis are saved;
                    if False, they are displayed.
    :type save_sp: bool

    :return: the most frequent voxel spacing values along the x, y and z axes.
    :rtype: tuple[float,float,float]
    """
    
    print("Save distribution about VoxelSpacing is set on: ", save_sp)
    print("")

    bin_size_sp = 0.01
    
    #Extract new_coords
    new_x = histo_spacing(df_py["VoxelSpacingX"], directory_out, "X", bin_size_sp, save_sp)
    new_y = histo_spacing(df_py["VoxelSpacingY"], directory_out, "Y", bin_size_sp, save_sp)
    new_z = histo_spacing(df_py["VoxelSpacingZ"], directory_out, "Z", bin_size_sp, save_sp)

    return new_x, new_y, new_z
    
def histo_spacing(coordinate: pd.Series, directory_out: Path, name: str, n_size: float, save_sp: bool)->float:
    """
    Show or save the distribution of the voxel spacing along the given axis.

    :param coordinate: column of the dataset header with the list of coordinates.
    :type coordinate: pd.Series
    :param directory_out: output directory.
    :type directory_out: Path
    :param name: name of the coordinate used for the histogram.
    :type name: str
    :param n_size: bin size for the histogram.
    :type n_size: float
    :param save_sp: if True, the histogram plot of the voxel spacing distribution along the given axis is saved.
    :type save_sp: bool
    
    :return: the most frequent value of the voxel spacing along the given axis.
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


def find_global_scale(df_py: pd.DataFrame,new_spacing_approach:str)->np.ndarray:
    """
    Define the new voxel spacing for image resampling using one of the following criteria: 
    - min_global: minimum voxel spacing along each axis;
    - mean_global: mean voxel spacing along each axis;
    - max_global: maximum voxel spacing along each axis.
    
    :param df_py: input DataFrame.
    :type df_py: pd.DataFrame
    :param new_spacing_approach: parameter specifying the criterion (min_global, mean_global or max_global).
    :type new_spacing_approach: str
    
    :return: new voxel spacing based on the chosen criterion.
    :rtype: np.ndarray
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
    
