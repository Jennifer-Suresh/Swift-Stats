from pathlib import Path

import numpy as np
import pytest

from swift_stats.imaging.channel_processing import normalize_channel, overlap_metrics
from swift_stats.imaging.lsm_reader import compile_lsm_folder
from swift_stats.imaging.oir_reader import compile_oir_folder

def test_overlap_metrics_known_masks() -> None:
    first = np.array([[True, True], [False, False]])
    second = np.array([[True, False], [True, False]])

    metrics = overlap_metrics(first, second)

    assert metrics["Channel_A_Positive_Pixels"] == 2
    assert metrics["Channel_B_Positive_Pixels"] == 2
    assert metrics["Overlap_Pixels"] == 1
    assert metrics["Union_Pixels"] == 3
    assert metrics["Overlay_Percentage"] == pytest.approx(100 / 3)

def test_normalize_channel_rejects_blank_image() -> None:
    blank = np.zeros((8, 8), dtype=np.float32)

    result = normalize_channel(blank, "Blank")

    assert result.normalized is None
    assert "zero variance" in result.status.casefold()
    assert result.minimum == pytest.approx(0.0)
    assert result.maximum == pytest.approx(0.0)
    assert result.mean == pytest.approx(0.0)
    assert result.std == pytest.approx(0.0)
    assert result.snr_metric == pytest.approx(0.0)

def test_lsm_reader_rejects_empty_folder(tmp_path: Path) -> None:
    input_folder = tmp_path / "empty_lsm"
    input_folder.mkdir()

    with pytest.raises(FileNotFoundError, match=r"No \.lsm files"):
        compile_lsm_folder(
            input_folder,
            tmp_path / "lsm_output",
            export_excel=False,
            export_powerpoint=False,
        )

def test_oir_reader_rejects_empty_folder(tmp_path: Path) -> None:
    input_folder = tmp_path / "empty_oir"
    input_folder.mkdir()

    with pytest.raises(FileNotFoundError, match=r"No \.oir files"):
        compile_oir_folder(
            input_folder,
            tmp_path / "oir_output",
            export_excel=False,
            export_powerpoint=False,
        )
