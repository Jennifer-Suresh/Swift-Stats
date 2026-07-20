from pathlib import Path

import pandas as pd
import pytest

from swift_stats.qpcr.combined_qpcr_reader import compile_mixed_qpcr

EXPECTED_COLUMNS = [
    "Well", "Sample Name", "Target Name", "Task", "Reporter", "Ct",
    "Date", "Test method", "Plate number", "Instrument", "Operator",
    "Source File",
]

def test_combined_reader_expected_columns(tmp_path: Path) -> None:
    fast7500_folder = Path("examples/qpcr/fast7500/input")
    qs5_folder = Path("examples/qpcr/qs5/input")

    if not fast7500_folder.exists() or not any(fast7500_folder.iterdir()):
        pytest.skip("7500 Fast example input files are not available.")
    if not qs5_folder.exists() or not any(qs5_folder.iterdir()):
        pytest.skip("QS5 example input files are not available.")

    output_file = tmp_path / "combined_qpcr.xlsx"
    result = compile_mixed_qpcr(fast7500_folder, qs5_folder, output_file)

    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == EXPECTED_COLUMNS
    assert not result.empty
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_combined_reader_contains_both_platforms(tmp_path: Path) -> None:
    fast7500_folder = Path("examples/qpcr/fast7500/input")
    qs5_folder = Path("examples/qpcr/qs5/input")

    if not fast7500_folder.exists() or not any(fast7500_folder.iterdir()):
        pytest.skip("7500 Fast example input files are not available.")
    if not qs5_folder.exists() or not any(qs5_folder.iterdir()):
        pytest.skip("QS5 example input files are not available.")

    result = compile_mixed_qpcr(
        fast7500_folder, qs5_folder, tmp_path / "combined_platform_check.xlsx"
    )
    source_names = result["Source File"].astype(str).str.casefold()
    assert source_names.str.contains("7500").any()
    assert source_names.str.contains("qs5").any()
