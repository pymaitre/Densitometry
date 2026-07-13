Installation procedure
======================

Densitometry is a repository used to extract the densitometric variables for a given set of patients.

This file is a guide for the installation of both the code and the necessary requirements. 
The installation flow is divided in the following four steps: 

1. `Clone the repository`
2. `Creation of a virtual environment`
3. `Installation of Poetry`
4. `Installation of the requirements`




.. _Clone the repository:
Clone the repository
---------------------------------
The first step in the installation procedure consists in cloning the repository. 
From the terminal run: 

.. code-block:: bash

    git clone https://github.com/pymaitre/Densitometry

    cd Densitometry

The last line is used to set the current directory to Densitometry.

.. _Creation of a virtual environment:
Creation of a virtual environment
---------------------------------
After having cloned the repository, it comes the creation of a virtual environment.
To do so, it is firstly necessary to have installed at least **Python 3.10**.
To check the current version of Python you can use:

.. code-block:: bash

    python --version

Next, you have to run from the terminal:

.. code-block:: bash

    python -m venv .venv

where .venv will be the virtual environment used during all the workflow.


Be sure that after having created the environment, .venv is active (if not, activate it)


.. _Installation of Poetry:
Installation of Poetry
-----------------------------------
After having created the virtual environment, `Poetry <https://python-poetry.org/>`_ can be installed as follows:

.. code-block:: bash

    pip install poetry

.. _Installation of the requirements:
Installation of the requirements
-----------------------------------
When Poetry has been installed, you can just import the requirements in the TOML file as follows: 

.. code-block:: bash

    poetry install

To check whether the installation has been successful, run from the terminal:

.. code-block:: bash

    pip show densitometry


After completing this flow, follow the **setting_total_ROI_analyses** and **setting_ROI_analyses** guides, which explain how files should be organized and how to extract the densitometric features.