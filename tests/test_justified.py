"""
Test module for justified.py
"""

import os
import re
import pytest
from Densitometry.total_ROI_functions import extract_histo as histo
from Densitometry.specific_ROI_functions.justified import just_variable, justified, histo_just
from pathlib import Path
import pandas as pd
import numpy as np


def test_just_variable(monkeypatch):
    """Check if the function just_variable behaves correctly."""

    inputs = iter(["-200", "200", "0"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    HU_min, HU_max, min_counts = just_variable()

    assert (HU_min, HU_max, min_counts) == (-200, 200, 0)


@pytest.mark.parametrize("HU_min,HU_max,min_counts", [(-200, 200, 0)])
def test_justified(
    reference_HU_ok: pd.Series,
    reference_counts_ok: pd.Series,
    HU_min: int,
    HU_max: int,
    min_counts: int,
):
    """Verify if the outcome of specific ROI analysis is valid."""

    HU_just, counts_just = justified(
        reference_HU_ok, reference_counts_ok, HU_min, HU_max, min_counts
    )

    assert isinstance(HU_just, pd.Series)
    assert isinstance(counts_just, pd.Series)
    assert len(HU_just) == len(counts_just)
    assert all(HU_just >= HU_min)
    assert all(HU_just <= HU_max)
    assert all(counts_just >= min_counts)
    assert HU_just is not None
    assert counts_just is not None


@pytest.mark.parametrize("delimiter", [[-200, 200, 0]])
def test_histo_just(
    reference_folder_files_ok: str, reference_dir_out: str, delimiter: tuple[int, int, int]
):
    """Perform a specific ROI analysis."""

    histo_just(reference_folder_files_ok, reference_dir_out, delimiter)
