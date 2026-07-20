from pathlib import Path
import warnings

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

SHEET_NAME = "Results"
SOURCE_COLUMN_POSITIONS = [*range(0, 5), 6, *range(16, 19), *range(38, 40)]

RESULT_COLUMNS = [
    "Well",
    "Sample Name",
    "Detector",
    "Task",
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
    """Extract underscore-separated metadata from a source filename."""
    parts = [part.strip() for part in Path(filename).stem.split("_")]
    values: list[str] = (
        parts + [""] * len(METADATA_COLUMNS)
    )[:len(METADATA_COLUMNS)]

    parsed = pd.to_datetime(
        pd.Series([values[0]], dtype="string"),
        format="%Y%m%d",
        errors="coerce",
    ).iloc[0]

    values[0] = parsed.strftime("%Y%m%d") if not pd.isna(parsed) else ""
    return dict(zip(METADATA_COLUMNS, values, strict=True))


def read_fast7500_file(filepath: Path) -> pd.DataFrame | None:
    """Read and clean one 7500 Fast result workbook."""
    filepath = Path(filepath)
    filename = filepath.name
    engine = "xlrd" if filepath.suffix.lower() == ".xls" else "openpyxl"

    with pd.ExcelFile(filepath, engine=engine) as workbook:
        if SHEET_NAME not in workbook.sheet_names:
            print(f"Skipped {filename}: Sheet '{SHEET_NAME}' was not found.")
            return None

        df = pd.read_excel(
            workbook,
            sheet_name=SHEET_NAME,
            skiprows=15,
        )

    df.columns = df.columns.astype(str).str.strip()

    if df.shape[1] <= max(SOURCE_COLUMN_POSITIONS):
        print(f"Skipped {filename}: Required columns through AN are missing.")
        return None

    non_empty = df.notna() & df.astype(str).apply(
        lambda column: column.str.strip().ne("")
    )

    fully_blank = ~non_empty.any(axis=1)
    only_column_a = (
        non_empty.iloc[:, 0]
        & ~non_empty.iloc[:, 1:11].any(axis=1)
    )

    result = (
        df.loc[~fully_blank & ~only_column_a]
        .iloc[:, SOURCE_COLUMN_POSITIONS]
        .copy()
    )

    if result.empty:
        print(f"Skipped {filename}: No valid rows remained.")
        return None

    result.columns = RESULT_COLUMNS

    ct_text = result["Ct"].astype(str).str.strip().str.casefold()
    result.loc[ct_text.eq("undetermined"), "Ct"] = 40

    result["Source File"] = filename

    for column, value in _extract_filename_metadata(filename).items():
        result[column] = value

    result = result.loc[:, EXPECTED_COLUMNS].copy()

    print(
        f"Processed: {filename} | "
        f"Removed A-only rows: {int(only_column_a.sum())}"
    )

    return result


def compile_fast7500_folder(
    input_folder: Path,
    output_file: Path,
) -> pd.DataFrame:
    """Compile all supported 7500 Fast workbooks in a folder."""
    input_folder = Path(input_folder)
    output_file = Path(output_file)

    if not input_folder.is_dir():
        raise FileNotFoundError(f"Input folder does not exist: {input_folder}")

    results: list[pd.DataFrame] = []

    for filepath in sorted(input_folder.iterdir()):
        if filepath.name.startswith("~$"):
            continue

        if filepath.suffix.lower() not in {".xlsx", ".xls", ".xlsm"}:
            continue

        try:
            result = read_fast7500_file(filepath)
            if result is not None:
                results.append(result)
        except Exception as error:
            print(f"Error reading {filepath.name}: {error}")

    if not results:
        raise ValueError("No 7500 Fast files were successfully processed.")

    combined = pd.concat(results, ignore_index=True)
    combined = combined.loc[:, EXPECTED_COLUMNS].copy()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    combined.to_excel(output_file, index=False)

    print(f"Saved compiled 7500 Fast data to: {output_file}")
    return combined
