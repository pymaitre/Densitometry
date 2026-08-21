"""
Test module for check_rate.py
"""

import os
import re
from pathlib import Path
import numpy as np
import pytest
from Densitometry.specific_ROI_functions.check_rate import rate_variable, analyze_rate, check_rate
import pandas as pd


def test_rate_variable(monkeypatch):
    """Check if the function rate_variable behaves correctly."""

    inputs = iter(["200", "400", "1"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    HU_min, HU_max, rate = rate_variable()

    assert (HU_min, HU_max, rate) == (200, 400, 1)


@pytest.mark.parametrize("HU_min,HU_max", [(200, 400)])
def test_analyze_rate(
    reference_HU_ok: pd.Series, reference_counts_ok: pd.Series, HU_min: int, HU_max: int
):
    """Verify if the outcome of rate analysis is valid."""

    diff, HU_rate, counts_rate = analyze_rate(reference_HU_ok, reference_counts_ok, HU_min, HU_max)

    assert isinstance(HU_rate, pd.Series)
    assert isinstance(counts_rate, pd.Series)
    assert isinstance(diff, float)
    assert len(HU_rate) == len(counts_rate)
    assert diff is not None
    assert HU_rate is not None
    assert counts_rate is not None


@pytest.mark.parametrize("rate_over_ROI", [[200, 400, 1]])
def test_check_rate(
    reference_folder_files_ok: Path, reference_dir_out: Path, rate_over_ROI: tuple[int, int, float]
):
    """Perform a rate analysis."""

    check_rate(reference_folder_files_ok, reference_dir_out, rate_over_ROI)
