Setting: Total ROI analyses
============================

After having followed the instructions described in `installation_procedure`, it comes a brief description of
how files should be organized and how to run the code used to extract the densitometric information. 
Differently from `setting_ROI_analyses`, it does not take into account specific ROI delimeters.

File organization
---------------------
In order to use the code, patient files should be organized in a proper way.
Consider an institute folder (**Institute**) which contains patient-associated folders, as described below:

.. code-block:: text

    Institute
       |___Patient_1
       |___Patient_2
       .
       .
       .
       |___Patient_N

each Patient (**Patient_i**) folder has to be organized as follows: 

.. code-block:: text

    Patient_i
       |___CT
            |___CT_1
                |___CT
                |___RTDOSE
                |___RTst

where:

* **CT folder** (the one inside CT_1) stores the CT DICOM files;
* **RTDOSE folder** contains the RTDOSE and RTPlan files;
* **RTst folder** contains the RTStruct and MV files.

             
Configuration file
---------------------

After having organized the files as described above, it is necessary to describe the YAML configuration file *conf_total_ROI.yml* (in **conf** subfolder).
It contains the following parameters to be manually set:

* **directory_dcm_out**: input institute folder
* **directory_out**: output folder where information are stored
* **image_modality**: modality of the image (e.g. "CT")
* **save_spacing_histo**: save spacing histogram  
* **save_ROI_info**: save ROI information
* **total_ROI_analyses**: perform total ROI analyses
* **show_total_ROI_info**: show information of from total ROI analyses
* **save_total_ROI_info**: save information from total ROI analyses
* **py_patient_file_name**: name of the py_patient file 
* **flag_resampling**: True for resampling, False otherwise
* **flag_new_spacing**: Flag that can take values: min_global, mean_global, max_global, frequency or manual (see below)
* **new_spacing**: 3D array with the desired new spacing (considered when flag_new_spacing=="manual")
* **flag_parallel**: True for parallel processing, False for sequential processing
* **N_jobs**: number of jobs for parallel execution (considered only when flag_parallel==True, if flag_parallel==False N_jobs is set equal to 1 automatically)
* **resampler**: resampler used during CT resampling (e.g. sitkBSpline, sitkLinear)
* **ID_problems**: list of patient IDs with known problems
* **rt_kind**: type of RT file (e.g. "MV-RQ")
* **list_roi**: list of ROIs 

An example of configuration file is below reported:

.. code-block:: text

    directory_dcm_out : "C:\\Users\\user_1\\Desktop\\Institute"

    directory_out : "C:\\Users\\user_1\\Desktop\\output_folder"

    image_modality : "CT"

    save_spacing_histo :  True  

    save_ROI_info : True 
    
    total_ROI_analyses :  True 

    show_total_ROI_info : False  

    save_total_ROI_info :  True 

    py_patient_file_name: "py_patient.xlsx"

    flag_resampling: True 

    flag_new_spacing: "manual"

    new_spacing: [1,1,3] 

    flag_parallel: False 

    N_jobs: 3 

    resampler: sitkBSpline

    ID_problems : [ID_1,ID_2]

    rt_kind : 'MV_RQ'

    list_roi : ['Heart']   


Choice of flag_new_spacing
--------------------

This flag is used to manage the choice of the voxel spacing for the resampling. 
It is taken into account only when flag_resampling==True. 
The following values can be set: 

* *"min_global"*: the new spacing is set as (min_x, min_y, min_z) of the given dataset
* *"mean_global"*: the new spacing is set as (mean_x, mean_y, mean_z) of the given dataset
* *"max_global"*: the new spacing is set as (max_x, max_y, max_z) of the given dataset
* *"frequency"*: the new spacing is set as the most frequent (x, y, z) in the given dataset
* *"manual"*: set manually (in *conf_total_ROI.yml*) the desired voxel spacing 


Run the code
---------------------
At last, you can run the code. Be sure resmip_env is active (if not, activate it), move to the folder 
**src** and then run from the terminal: 

.. code-block:: bash

    python -m Densitometry.main_scripts.total_ROI_analyses

When the code stops running, all the computed densitometric data are stored in the path provided in **directory_out**. 


Output
---------------------
The output of the data extraction is stored in the folder associated with the path **directory_out**.
More precisely, the results are organized as follows:

.. code-block:: text

    directory_out
        |_________ Total_ROI
        |_________ Voxel_Analyses
        |_________ counts_ROI.xlsx
        |_________ py_patient_file.xlsx
        |_________ ROI_tot_pz.xlsx




**Total_ROI** is a folder which contains the densitometry extraction information 
(before and after the resampling) and the relative plots (e.g. DVHs).

**Voxel_Analyses** is generated only when flag_resampling==True and flag_new_spacing=="frequency. 
It stores the distributions of the spacings of the given dataset.

*counts_ROI.xlsx* reports the found ROIs and their presence. 

*py_patient_file.xlsx* stores the patients' age (if present in CT files), the original voxel spacing 
and the path where the CT files are stored. 

*ROI_tot_pz.xlsx* reports the ROIs of each patient.

