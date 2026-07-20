from argparse import ArgumentParser
from pathlib import Path

from swift_stats.qpcr.fast7500_reader import compile_fast7500_folder


def main() -> None:
    parser = ArgumentParser(
        description="Compile 7500 Fast qPCR result files."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Folder containing 7500 Fast Excel files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination Excel workbook.",
    )

    args = parser.parse_args()
    compile_fast7500_folder(args.input, args.output)


if __name__ == "__main__":
    main()
