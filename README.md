Densitometry
============

Overview
------------

**Densitometry** is used for DICOM analysis, extraction of ROI's densitometry histograms and the associated features.
The code relies on resmip for the reading the DICOM images and for the resampling procedure, determinant when CT scans show large difference in terms of voxel spacing. 
Moreover, the code is implemented to run using a sequential or parallel approach.


Modules
-------------

The current folder has two subfolders: **src** and **tutorials**. 
The folder **src** contains other two folders: **Densitometry** and **test**. The former represents the main core of the code, while the latter stores some codes that can be used for testing the code. On the other hand **tutorials** contains some additional Jupyter notebooks.

Focusing on **Densitometry**, the following subfolders can be found: 

1. **conf**: collects the configuration files (in YAML format);
2. **dcm_functions**: used to read DICOM headers and to create a database with header information;
3. **main_scripts**: collects the main scripts;
4. **merge_file_functions**: used to read databases and to modify them in case of merging or dropping rows;
5. **specific_ROI_functions**: used for evaluating statistic features referred to a specific region;
6. **total_ROI_functions**: used to extract the desired dosimetric data.

The file *other_functions.py* contains a function used to read the YAML files. 

Installation and requirements
-------------------------------

Firstly, it is necessary to clone the directory: 
```python
git clone https://github.com/TommasoGiovanniVolonteri/Densitometry
```

To run the code it is necessary to have installed at least **Python 3.10**. 
Then create a virtual environment and install [Poetry](https://python-poetry.org/) and the requirements in the [TOML](pyproject.toml) as follows: 

```python
pip install poetry
poetry install
```

For further details regarding both the installation procedure and settings, see [Installation procedure](*docs\source\installation_procedure.rst*) and [setting](docs\source\setting.rst) in [**source**](docs\source). 

Acknowledgements
------------------

