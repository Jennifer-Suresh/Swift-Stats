from pathlib import Path
import warnings

import pandas as pd


warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="openpyxl",
)

SHEET_NAME = "Results"

FINAL_COLS = [
    0,
    2,
    *range(4, 7),
    11,
    *range(18, 21),
    *range(47, 49),
]

RESULT_COLUMNS = [
    "Well",
    "Task",
    "Sample Name",
    "Target Name",
    "Reporter",
    "Ct",
    "Automatic Baseline",
    "Baseline Start",
    "Baseline End",
    "Call",
    "Call Assessment",
]

METADATA_COLUMNS = [
    "Date",
    "Test method",
    "Plate number",
    "Instrument",
    "Operator",
]

EXPECTED_COLUMNS = [
    *RESULT_COLUMNS,
    "Source File",
    *METADATA_COLUMNS,
]


def _extract_filename_metadata(filename: str) -> dict[str, str]:
    """Extract metadata from the source filename."""

    filename_without_extension = Path(filename).stem

    parts = [
        part.strip()
        for part in filename_without_extension.split("_")
    ]

    metadata_values = (
        parts + [""] * len(METADATA_COLUMNS)
    )[:len(METADATA_COLUMNS)]

    parsed_date = pd.to_datetime(
        pd.Series([metadata_values[0]], dtype="string"),
        format="%Y%m%d",
        errors="coerce",
    ).iloc[0]

    metadata_values[0] = (
        parsed_date.strftime("%Y%m%d")
        if not pd.isna(parsed_date)
        else ""
    )

    return dict(
        zip(
            METADATA_COLUMNS,
            metadata_values,
            strict=True,
        )
    )


def read_qs5_file(filepath: Path) -> pd.DataFrame | None:
    """
    Read and clean one QS5 Excel file.

    Returns None when the file does not contain valid QS5 data.
    """

    filename = filepath.name

    with pd.ExcelFile(filepath) as workbook:
        if SHEET_NAME not in workbook.sheet_names:
            print(
                f"Skipped {filename}: Sheet '{SHEET_NAME}' "
                f"was not found."
            )
            return None

        df = pd.read_excel(
            workbook,
            sheet_name=SHEET_NAME,
            usecols="A:AW",
            skiprows=22,
        )

    df.columns = df.columns.astype(str).str.strip()

    if df.shape[1] < 49:
        print(
            f"Skipped {filename}: Required columns "
            f"through AW are missing."
        )
        return None

    non_empty = df.notna() & df.astype(str).apply(
        lambda column: column.str.strip().ne("")
    )

    fully_blank = ~non_empty.any(axis=1)

    only_a_b = (
        non_empty.iloc[:, :2].any(axis=1)
        & ~non_empty.iloc[:, 2:].any(axis=1)
    )

    valid_rows = ~fully_blank & ~only_a_b

    df_final = (
        df.loc[valid_rows]
        .iloc[:, FINAL_COLS]
        .copy()
    )

    if df_final.empty:
        print(
            f"Skipped {filename}: "
            f"No valid rows remained."
        )
        return None

    df_final.columns = RESULT_COLUMNS

    ct_text = (
        df_final["Ct"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    df_final["Ct"] = (
        df_final["Ct"]
        .astype("string")
        .mask(
            ct_text.eq("undetermined"),
            "40",
        )
    )

    df_final["Ct"] = pd.to_numeric(
        df_final["Ct"],
        errors="coerce",
    )

    df_final["Source File"] = filename

    metadata = _extract_filename_metadata(filename)
  

    for column_name, value in metadata.items():
        df_final[column_name] = value

    df_final = df_final.loc[:, EXPECTED_COLUMNS].copy()

    print(
        f"Processed: {filename} | "
        f"Removed A/B-only rows: {int(only_a_b.sum())}"
    )

    return df_final


def compile_qs5_folder(
    input_folder: Path,
    output_file: Path,
) -> pd.DataFrame:
    """
    Compile all QS5 Excel files in a folder.

    Parameters
    ----------
    input_folder:
        Folder containing QS5 .xlsx or .xls files.

    output_file:
        Destination Excel workbook.

    Returns
    -------
    pandas.DataFrame
        The combined QS5 result table.
    """

    input_folder = Path(input_folder)
    output_file = Path(output_file)

    if not input_folder.is_dir():
        raise FileNotFoundError(
            f"Input folder does not exist: {input_folder}"
        )

    results: list[pd.DataFrame] = []

    for filepath in sorted(input_folder.iterdir()):
        if filepath.name.startswith("~$"):
            continue

        if filepath.suffix.lower() not in {".xlsx", ".xls"}:
            continue

        try:
            result = read_qs5_file(filepath)

            if result is not None:
                results.append(result)

        except Exception as error:
            print(
                f"Error reading {filepath.name}: {error}"
            )

    if not results:
        raise ValueError(
            "No QS5 files were successfully processed."
        )

    combined_df = pd.concat(
        results,
        ignore_index=True,
    )

    combined_df = combined_df.loc[
        :,
        EXPECTED_COLUMNS,
    ].copy()

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_df.to_excel(
        output_file,
        index=False,
    )

    print(f"Saved compiled QS5 data to: {output_file}")

    return combined_df
