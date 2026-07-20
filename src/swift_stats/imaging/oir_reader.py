from __future__ import annotations

import logging
from pathlib import Path
from typing import Mapping

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import oirfile

from .channel_processing import (
    create_qc_powerpoint,
    max_project_channels,
    normalize_channel,
    overlap_metrics,
    save_reports,
)

LOGGER = logging.getLogger(__name__)

DEFAULT_OIR_CHANNELS = {"DAPI": 0, "GFP": 1, "Mitotracker": 2}


def _pure_colormap(name: str, hex_color: str):
    cmap = mcolors.LinearSegmentedColormap.from_list(name, ["black", hex_color])
    cmap.set_under("black")
    cmap.set_bad("black")
    return cmap


def compile_oir_folder(
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
    """
    Process all .oir files and generate the same output types as the LSM workflow:
    plots/, data/, CSV, Excel, and a PowerPoint QC deck.
    """
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    plots_folder = output_folder / "plots"
    data_folder = output_folder / "data"
    plots_folder.mkdir(parents=True, exist_ok=True)
    data_folder.mkdir(parents=True, exist_ok=True)

    files = sorted(input_folder.glob("*.oir"))
    if not files:
        raise FileNotFoundError(f"No .oir files found in: {input_folder}")

    mapping = dict(DEFAULT_OIR_CHANNELS)
    if channels:
        mapping.update(channels)

    cmap_blue = _pure_colormap("PureBlue", "#0000FF")
    cmap_green = _pure_colormap("PureGreen", "#00FF00")
    cmap_red = _pure_colormap("PureRed", "#FF0000")

    records: list[dict] = []
    generated_plots: list[Path] = []

    for file_path in files:
        record: dict = {
            "Filename": file_path.name,
            "File_Type": "OIR",
            "Status": "Failed",
            "Notes": "",
        }

        try:
            with oirfile.OirFile(file_path) as source:
                raw = source.asarray()

            projected = max_project_channels(raw, channel_axis)
            required_max = max(mapping.values())
            if projected.shape[0] <= required_max:
                raise ValueError(
                    f"Projected image has {projected.shape[0]} channels, "
                    f"but channel index {required_max} was requested."
                )

            dapi = normalize_channel(
                projected[mapping["DAPI"]], "DAPI",
                snr_threshold=snr_threshold, lower_sigma=lower_sigma
            )
            gfp = normalize_channel(
                projected[mapping["GFP"]], "GFP",
                snr_threshold=snr_threshold, lower_sigma=lower_sigma
            )
            mito = normalize_channel(
                projected[mapping["Mitotracker"]], "Mitotracker",
                snr_threshold=snr_threshold, lower_sigma=lower_sigma
            )

            failures = [result.status for result in (dapi, gfp, mito) if result.normalized is None]
            if failures:
                record.update(Status="Skipped", Notes="; ".join(failures))
                records.append(record)
                LOGGER.warning("Skipped %s: %s", file_path.name, record["Notes"])
                continue

            assert dapi.normalized is not None
            assert gfp.normalized is not None
            assert mito.normalized is not None

            metrics = overlap_metrics(
                gfp.normalized > threshold,
                mito.normalized > threshold,
            )

            record.update(
                Status="Processed",
                Notes="Success",
                Primary_Channel="GFP",
                Secondary_Channel="Mitotracker",
                DAPI_Channel=mapping["DAPI"] + 1,
                GFP_Channel=mapping["GFP"] + 1,
                Mitotracker_Channel=mapping["Mitotracker"] + 1,
                Threshold=threshold,
                GFP_SNR=round(gfp.snr_metric, 4),
                Mitotracker_SNR=round(mito.snr_metric, 4),
                DAPI_SNR=round(dapi.snr_metric, 4),
                **{key: round(value, 4) if isinstance(value, float) else value
                   for key, value in metrics.items()},
            )

            rgb = np.zeros((*projected.shape[-2:], 3), dtype=np.float32)
            rgb[..., 0] = mito.normalized
            rgb[..., 1] = gfp.normalized
            rgb[..., 2] = dapi.normalized

            fig, axes = plt.subplots(1, 4, figsize=(20, 5), facecolor="black")
            axes[0].imshow(dapi.normalized, cmap=cmap_blue, vmin=0.001, vmax=1.0)
            axes[0].set_title(f"Ch {mapping['DAPI'] + 1}: DAPI", color="#3366FF", fontweight="bold")
            axes[1].imshow(gfp.normalized, cmap=cmap_green, vmin=0.001, vmax=1.0)
            axes[1].set_title(f"Ch {mapping['GFP'] + 1}: GFP", color="#00FF00", fontweight="bold")
            axes[2].imshow(mito.normalized, cmap=cmap_red, vmin=0.001, vmax=1.0)
            axes[2].set_title(
                f"Ch {mapping['Mitotracker'] + 1}: Mitotracker",
                color="#FF3333",
                fontweight="bold",
            )
            axes[3].imshow(rgb)
            axes[3].set_title(
                f"Merged (GFP/Mito overlap: {metrics['Overlay_Percentage']:.1f}%)",
                color="orange",
                fontweight="bold",
            )
            for axis in axes:
                axis.axis("off")
            fig.suptitle(f"OIR microscopy summary: {file_path.name}", color="white", fontsize=13)
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

    csv_path = data_folder / "oir_microscopy_report.csv"
    xlsx_path = data_folder / "oir_microscopy_report.xlsx" if export_excel else None
    save_reports(records, csv_path, xlsx_path)

    outputs = {"csv": csv_path, "plots": plots_folder}
    if xlsx_path:
        outputs["xlsx"] = xlsx_path

    if export_powerpoint and generated_plots:
        pptx_path = data_folder / "oir_qc_presentation.pptx"
        create_qc_powerpoint(generated_plots, pptx_path, title_prefix="OIR QC Review")
        outputs["pptx"] = pptx_path

    return outputs
