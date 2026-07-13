Densitometry
============

Overview
------------

**Densitometry** is used for DICOM analysis, extraction of densitometry histograms of ROIs and the associated features.
The code relies on [resmip](https://github.com/pymaitre/resmip.git) for the reading the DICOM images and for the resampling procedure, determinant when CT scans show large difference in terms of VoxelSpacing. 
Moreover, the code is implemented to run using a sequential or parallel approach.


Modules
-------------

The current folder has two subfolders: **src** and **tutorials**. 
The folder **src** contains two directories: **Densitometry**, used for the extraction of densitometric data, and **tests**, used for testing. 
On the other hand **tutorials** contains some additional Jupyter notebooks, implemented for tutorial and illustrative purposes.

The core of the code is **Densitometry**, which structure is below reported: 

1. **conf**: collects the configuration files (in YAML format);
2. **dcm_functions**: used to read DICOM headers and to create a database with header information;
3. **main_scripts**: collects the main scripts;
5. **specific_ROI_functions**: used for evaluating statistical features considering a provided delimiter;
6. **total_ROI_functions**: used to extract the desired dosimetric data.

The file *other_functions.py* contains a function used to read the YAML files. 

Installation and requirements
-------------------------------

Firstly, it is necessary to clone the directory: 
```python
git clone https://github.com/pymaitre/Densitometry
```

To run the code it is necessary to have installed at least **Python 3.10**. 
Then create a virtual environment and install [Poetry](https://python-poetry.org/) and the requirements in the [TOML](pyproject.toml) as follows: 

```python
pip install poetry
poetry install
```

For further details regarding both the installation procedure, see [installation procedure](docs/source/installation_procedure.rst) in [**source**](docs/source). 


Main scripts
-----------------

The subfolder **main_scripts** contains three different codes.
1. *check_pz.py*: used to print the list of patient IDs;
2. *ROI_analyses.py*: used to extract densitometric features considering a specific delimiter (see [setting_ROI_analyses](docs/source/setting_ROI_analyses.rst) for further details);
3. *total_ROI_analyses.py*: used to extract densitometric of the given ROI (see [setting_total_ROI_analyses](docs/source/setting_total_ROI_analyses.rst) for further details).


Contributions
-----------------
Contributions are welcomed. 
If interested in support the improvement of this library please follow these steps:
1. Clone the repository;
2. Create a branch from the  {code}`main` and add the modifications;
3. Use {code}`pytest` to check if your modifications are well implemented;
4. Open a pull request, describing the added modifications.

Please check also the issue tracker to see the open issues and future requests.


Acknowledgements
------------------
This repository has been implemented by: **Tommaso Giovanni Volonteri**, **Alfonso Belardo** and **Gabriele Palazzo**.


