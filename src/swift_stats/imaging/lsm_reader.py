from __future__ import annotations

import logging
from pathlib import Path
from typing import Mapping

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import tifffile

from .channel_processing import (
    create_qc_powerpoint,
    max_project_channels,
    normalize_channel,
    overlap_metrics,
    save_reports,
)

LOGGER = logging.getLogger(__name__)

DEFAULT_LSM_CHANNELS = {"mCherry": 0, "GFP": 1, "DAPI": 2}


def _lsm_channel_names(tif: tifffile.TiffFile) -> list[str]:
    """Best-effort extraction of Zeiss LSM channel names."""
    metadata = getattr(tif, "lsm_metadata", None) or {}
    colors = metadata.get("ChannelColors", {})
    channels = colors.get("Channel", [])

    names: list[str] = []
    for channel in channels:
        if isinstance(channel, dict):
            names.append(str(channel.get("Name", "")).strip())
        else:
            names.append("")
    return names


def _map_lsm_channels(names: list[str], fallback: Mapping[str, int]) -> dict[str, int]:
    mapping = dict(fallback)
    for index, raw_name in enumerate(names):
        name = raw_name.lower()
        if any(term in name for term in ("dapi", "hoechst", "blue")):
            mapping["DAPI"] = index
        elif any(term in name for term in ("gfp", "green")):
            mapping["GFP"] = index
        elif any(term in name for term in ("mcherry", "m-cherry", "cherry", "red")):
            mapping["mCherry"] = index
    return mapping


def _pure_colormap(name: str, hex_color: str):
    cmap = mcolors.LinearSegmentedColormap.from_list(name, ["black", hex_color])
    cmap.set_under("black")
    cmap.set_bad("black")
    return cmap


def compile_lsm_folder(
    input_folder: Path,
    output_folder: Path,
    *,
    channels: Mapping[str, int] | None = None,
    threshold: float = 0.1,
    snr_threshold: float = 2.5,
    lower_sigma: float = 1.2,
    channel_axis: int | None = None,
    export_excel: bool = True,
    export_powerpoint: bool = True,
) -> dict[str, Path]:
    """Process all .lsm files and generate plots, tabular metrics, and a QC deck."""
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    plots_folder = output_folder / "plots"
    data_folder = output_folder / "data"
    plots_folder.mkdir(parents=True, exist_ok=True)
    data_folder.mkdir(parents=True, exist_ok=True)

    files = sorted(input_folder.glob("*.lsm"))
    if not files:
        raise FileNotFoundError(f"No .lsm files found in: {input_folder}")

    fallback = dict(DEFAULT_LSM_CHANNELS)
    if channels:
        fallback.update(channels)

    cmap_red = _pure_colormap("PureRed", "#FF0000")
    cmap_green = _pure_colormap("PureGreen", "#00FF00")
    cmap_blue = _pure_colormap("PureBlue", "#0000FF")

    records: list[dict] = []
    generated_plots: list[Path] = []

    for file_path in files:
        record: dict = {
            "Filename": file_path.name,
            "File_Type": "LSM",
            "Status": "Failed",
            "Notes": "",
        }

        try:
            with tifffile.TiffFile(file_path) as tif:
                raw = tif.asarray()
                channel_names = _lsm_channel_names(tif)

            projected = max_project_channels(raw, channel_axis)
            mapping = _map_lsm_channels(channel_names, fallback)

            required_max = max(mapping.values())
            if projected.shape[0] <= required_max:
                raise ValueError(
                    f"Projected image has {projected.shape[0]} channels, "
                    f"but channel index {required_max} was requested."
                )

            mcherry = normalize_channel(
                projected[mapping["mCherry"]], "mCherry",
                snr_threshold=snr_threshold, lower_sigma=lower_sigma
            )
            gfp = normalize_channel(
                projected[mapping["GFP"]], "GFP",
                snr_threshold=snr_threshold, lower_sigma=lower_sigma
            )
            dapi = normalize_channel(
                projected[mapping["DAPI"]], "DAPI",
                snr_threshold=snr_threshold, lower_sigma=lower_sigma
            )

            failures = [result.status for result in (mcherry, gfp, dapi) if result.normalized is None]
            if failures:
                record.update(Status="Skipped", Notes="; ".join(failures))
                records.append(record)
                LOGGER.warning("Skipped %s: %s", file_path.name, record["Notes"])
                continue

            assert mcherry.normalized is not None
            assert gfp.normalized is not None
            assert dapi.normalized is not None

            metrics = overlap_metrics(
                mcherry.normalized > threshold,
                gfp.normalized > threshold,
            )

            record.update(
                Status="Processed",
                Notes="Success",
                Primary_Channel="mCherry",
                Secondary_Channel="GFP",
                DAPI_Channel=mapping["DAPI"] + 1,
                GFP_Channel=mapping["GFP"] + 1,
                mCherry_Channel=mapping["mCherry"] + 1,
                Threshold=threshold,
                mCherry_SNR=round(mcherry.snr_metric, 4),
                GFP_SNR=round(gfp.snr_metric, 4),
                DAPI_SNR=round(dapi.snr_metric, 4),
                **{key: round(value, 4) if isinstance(value, float) else value
                   for key, value in metrics.items()},
            )

            rgb = np.zeros((*projected.shape[-2:], 3), dtype=np.float32)
            rgb[..., 0] = mcherry.normalized
            rgb[..., 1] = gfp.normalized
            rgb[..., 2] = dapi.normalized

            fig, axes = plt.subplots(1, 4, figsize=(20, 5), facecolor="black")
            axes[0].imshow(mcherry.normalized, cmap=cmap_red, vmin=0.001, vmax=1.0)
            axes[0].set_title(f"Ch {mapping['mCherry'] + 1}: mCherry", color="#FF3333", fontweight="bold")
            axes[1].imshow(gfp.normalized, cmap=cmap_green, vmin=0.001, vmax=1.0)
            axes[1].set_title(f"Ch {mapping['GFP'] + 1}: GFP", color="#00FF00", fontweight="bold")
            axes[2].imshow(dapi.normalized, cmap=cmap_blue, vmin=0.001, vmax=1.0)
            axes[2].set_title(f"Ch {mapping['DAPI'] + 1}: DAPI", color="#3366FF", fontweight="bold")
            axes[3].imshow(rgb)
            axes[3].set_title(
                f"Merged (mCherry/GFP overlap: {metrics['Overlay_Percentage']:.1f}%)",
                color="orange",
                fontweight="bold",
            )
            for axis in axes:
                axis.axis("off")
            fig.suptitle(f"LSM microscopy summary: {file_path.name}", color="white", fontsize=13)
            fig.tight_layout()

            plot_path = plots_folder / f"layout_{file_path.stem}.png"
            fig.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor="black", edgecolor="none")
            plt.close(fig)
            generated_plots.append(plot_path)
            records.append(record)
            LOGGER.info("Processed %s", file_path.name)

        except Exception as exc:
            record["Notes"] = str(exc)
            records.append(record)
            LOGGER.exception("Could not process %s", file_path.name)

    csv_path = data_folder / "lsm_microscopy_report.csv"
    xlsx_path = data_folder / "lsm_microscopy_report.xlsx" if export_excel else None
    save_reports(records, csv_path, xlsx_path)

    outputs = {"csv": csv_path, "plots": plots_folder}
    if xlsx_path:
        outputs["xlsx"] = xlsx_path

    if export_powerpoint and generated_plots:
        pptx_path = data_folder / "lsm_qc_presentation.pptx"
        create_qc_powerpoint(generated_plots, pptx_path, title_prefix="LSM QC Review")
        outputs["pptx"] = pptx_path

    return outputs
