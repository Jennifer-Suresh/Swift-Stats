from pathlib import Path

import pandas as pd
import pytest

from swift_stats.qpcr.fast7500_reader import compile_fast7500_folder

EXPECTED_COLUMNS = [
    "Well", "Sample Name", "Detector", "Task", "Reporter", "Ct",
    "Automatic Baseline", "Baseline Start", "Baseline End", "Call",
    "Call Assessment", "Source File", "Date", "Test method",
    "Plate number", "Instrument", "Operator",
]

def test_fast7500_expected_columns(tmp_path: Path) -> None:
    input_folder = Path("examples/qpcr/fast7500/input")
    if not input_folder.exists() or not any(input_folder.iterdir()):
        pytest.skip("7500 Fast example input files are not available.")

    output_file = tmp_path / "fast7500_compiled.xlsx"
    result = compile_fast7500_folder(input_folder, output_file)

    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == EXPECTED_COLUMNS
    assert not result.empty
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_fast7500_undetermined_ct_is_replaced(tmp_path: Path) -> None:
    input_folder = Path("examples/qpcr/fast7500/input")
    if not input_folder.exists() or not any(input_folder.iterdir()):
        pytest.skip("7500 Fast example input files are not available.")

    result = compile_fast7500_folder(
        input_folder, tmp_path / "fast7500_ct_check.xlsx"
    )
    ct_text = result["Ct"].astype(str).str.strip().str.casefold()
    assert not ct_text.eq("undetermined").any()
