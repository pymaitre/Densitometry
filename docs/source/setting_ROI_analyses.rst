Setting: ROI analyses
============================

After having followed the instructions described in `installation_procedure`, it comes a brief description of
how files should be organized and how to run the code used to extract the densitometric information.
Differently from Total ROI analyses , it takes into account specific ROI delimeters and performs specific-ROI analyses.

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
After having organized the files as described above, it is necessary to describe the YAML configuration file *conf_ROI_analyses.yml* (in **conf** subfolder).
It contains the following parameters to be manually set:

* **directory_out**: output directory 
* **specific_ROI_analyses**: flag to perform specific ROI analysis (True or False)
* **specific_ROI_delimiter**: HU_min, HU_max, min_counts for specific ROI delimiter analysis
* **over_ROI_analyses**: flag to perform over ROI analysis (True or False) 
* **over_ROI_delimiter**: HU_min over whose analyse and min_counts for this region for the over ROI delimiter analysis
* **rate_ROI_analyses**: flag to perform rate ROI analysis (True or False) 
* **rate_ROI_delimiter**: HU_min and HU_max and rate_counts beetween inside and outside for this region for the rate ROI delimiter analysis.

An example of configuration file is below reported:

.. code-block:: text

    directory_out : "C:\\Users\\user\\Desktop\\directory_out"

    specific_ROI_analyses : True 
    
    specific_ROI_delimiter : [-200, 200, 0] 

    over_ROI_analyses : True 
    
    over_ROI_delimiter : [200, 10] 
    
    rate_ROI_analyses : True 

    rate_ROI_delimiter : [200, 400, 1]  


**directory_out** is the one obtained at the end of Total ROI analyses.


Run the code
---------------------
At last, you can run the code. Be sure .venv is active (if not, activate it), move to the folder 
**src** and then run from the terminal: 

.. code-block:: bash

    python -m Densitometry.main_scripts.ROI_analyses

When the code stops running, all the computed densitometric data are stored in the path provided in **directory_out**. 

Output
---------------------
Three different analyses can be performed:
* specific analysis: extraction of infomation, considering the range [HU_min, HU_max] with counts greater than min_counts.
* over analysis: extraction of infomation, considering HU greater than HU_min with at least min_counts.
* rate analysis: extraction of information, considering the range [HU_min, HU_max] and rate_counts beetween inside and outside for this region.

At the end of the extraction, a proper folder is generated in **directory_out** (with the same structure for each analysis).
The resulting directory stores information obtained at the end of each run, such as plots of the histograms and some statistics.  
An example of results from the specific analysis is below reported:

.. code-block:: text

    Specific_Regions
        |_________ Region_-200_200_0
                        |_________ Files
                        |_________ Histograms
                        |_________ Stats_specific_-200_200_0.xlsx

where 
**Files** is a folder which contains the HU and counts resulting from the specific analysis.

**Histograms** stores the resulting histograms.

*Stats_specific_-200_200_0.xlsx* reports the statistics from the specific analysis. 



