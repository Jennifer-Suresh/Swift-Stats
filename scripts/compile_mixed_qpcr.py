from argparse import ArgumentParser
from pathlib import Path

from swift_stats.qpcr.combined_qpcr_reader import compile_mixed_qpcr


def main() -> None:
    parser = ArgumentParser(
        description="Compile QS5 and 7500 Fast qPCR result files."
    )
    parser.add_argument(
        "--fast7500-input",
        type=Path,
        required=True,
        help="Folder containing 7500 Fast Excel files.",
    )
    parser.add_argument(
        "--qs5-input",
        type=Path,
        required=True,
        help="Folder containing QS5 Excel files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination Excel workbook.",
    )

    args = parser.parse_args()
    compile_mixed_qpcr(
        fast7500_folder=args.fast7500_input,
        qs5_folder=args.qs5_input,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
