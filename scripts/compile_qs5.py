from argparse import ArgumentParser
from pathlib import Path

from swift_stats.qpcr.qs5_reader import compile_qs5_folder


def main() -> None:
    parser = ArgumentParser(
        description="Compile QS5 qPCR result files."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Folder containing QS5 Excel files.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output Excel file.",
    )

    args = parser.parse_args()

    compile_qs5_folder(
        input_folder=args.input,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()