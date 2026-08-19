"""
Test module of check_pz.py
"""

from pathlib import Path
import pytest
import pandas as pd
import os
import glob
from Densitometry.main_scripts.check_pz import find_id_dir, main
from utils_for_testing import modify_configuration_file


def test_find_id_dir(patient_directory: Path):
    """Check if the ID directory is found."""

    id_dirs = find_id_dir(patient_directory)

    assert isinstance(id_dirs, list)
    assert not len(id_dirs) == 0


def test_main(
    patient_directory: Path,
    reference_py_patient_file: Path,
    reference_conf_total_ROI_analyses: Path,
):
    """Test the main function of check_pz."""

    reference_conf = modify_configuration_file(
        reference_conf_total_ROI_analyses,
        ["directory_dcm_out", "py_patient_path"],
        [Path(patient_directory), Path(reference_py_patient_file)],
    )

    main(reference_conf)


def test_main_no_dcm_out(reference_py_patient_file: Path, reference_conf_total_ROI_analyses: Path):
    """Do not provide directory_dcm_out in the configuration file."""

    reference_conf = modify_configuration_file(
        reference_conf_total_ROI_analyses,
        ["directory_dcm_out", "py_patient_path"],
        [None, Path(reference_py_patient_file)],
    )

    with pytest.raises(ValueError):
        main(reference_conf)


def test_main_no_py_file(patient_directory: Path, reference_conf_total_ROI_analyses: dict):
    """Do not provide py_patient_path in the configuration file."""

    reference_conf = modify_configuration_file(
        reference_conf_total_ROI_analyses,
        ["directory_dcm_out", "py_patient_path"],
        [Path(patient_directory), None],
    )

    with pytest.raises(ValueError):
        main(reference_conf)


def test_main_not_valid_dcm_out(
    reference_py_patient_file: Path, reference_conf_total_ROI_analyses: dict
):
    """Provide an invalid directory_dcm_out path."""

    reference_conf = modify_configuration_file(
        reference_conf_total_ROI_analyses,
        ["directory_dcm_out", "py_patient_path"],
        [Path("C:\\User\\user\\not_valid_dcm"), Path(reference_py_patient_file)],
    )

    with pytest.raises(ValueError):
        main(reference_conf)


def test_main_not_valid_py(patient_directory: Path, reference_conf_total_ROI_analyses: dict):
    """Provide an invalid py_patient_path."""

    reference_conf = modify_configuration_file(
        reference_conf_total_ROI_analyses,
        ["directory_dcm_out", "py_patient_path"],
        [Path(patient_directory), Path("C:\\User\\user\\not_valid_py_patient_path")],
    )

    with pytest.raises(ValueError):
        main(reference_conf)
