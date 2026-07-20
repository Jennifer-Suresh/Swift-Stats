from __future__ import annotations

import argparse
import logging
from pathlib import Path

from swift_stats.imaging.oir_reader import compile_oir_folder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch-process three-channel Olympus OIR microscopy files."
    )
    parser.add_argument("--input", required=True, type=Path, help="Folder containing .oir files.")
    parser.add_argument("--output", required=True, type=Path, help="Run output folder.")
    parser.add_argument("--dapi-channel", type=int, default=1, help="1-based channel number.")
    parser.add_argument("--gfp-channel", type=int, default=2, help="1-based channel number.")
    parser.add_argument("--mitotracker-channel", type=int, default=3, help="1-based channel number.")
    parser.add_argument("--channel-axis", type=int, default=None, help="Optional channel-axis index.")
    parser.add_argument("--threshold", type=float, default=0.1, help="Normalized mask threshold.")
    parser.add_argument("--snr-threshold", type=float, default=2.5)
    parser.add_argument("--lower-sigma", type=float, default=1.2)
    parser.add_argument("--no-pptx", action="store_true", help="Do not create the QC PowerPoint.")
    parser.add_argument("--no-xlsx", action="store_true", help="Do not create the Excel report.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    outputs = compile_oir_folder(
        args.input,
        args.output,
        channels={
            "DAPI": args.dapi_channel - 1,
            "GFP": args.gfp_channel - 1,
            "Mitotracker": args.mitotracker_channel - 1,
        },
        threshold=args.threshold,
        snr_threshold=args.snr_threshold,
        lower_sigma=args.lower_sigma,
        channel_axis=args.channel_axis,
        export_excel=not args.no_xlsx,
        export_powerpoint=not args.no_pptx,
    )

    print("\nOIR processing complete.")
    for output_type, path in outputs.items():
        print(f"{output_type}: {path}")


if __name__ == "__main__":
    main()
