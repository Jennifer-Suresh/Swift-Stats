from pathlib import Path
import warnings

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

SHEET_NAME = "Results"
SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}

OUTPUT_COLUMNS = [
    "Well", "Sample Name", "Target Name", "Task", "Reporter", "Ct",
    "Date", "Test method", "Plate number", "Instrument", "Operator",
    "Source File",
]

METADATA_COLUMNS = [
    "Date", "Test method", "Plate number", "Instrument", "Operator",
]


def _extract_filename_metadata(filename: str) -> dict[str, str]:
    parts = [part.strip() for part in Path(filename).stem.split("_")]
    values = (parts + [""] * len(METADATA_COLUMNS))[:len(METADATA_COLUMNS)]

    parsed = pd.to_datetime(
        pd.Series([values[0]], dtype="string"),
        format="%Y%m%d",
        errors="coerce",
    ).iloc[0]

    values[0] = parsed.strftime("%Y%m%d") if not pd.isna(parsed) else ""
    return dict(zip(METADATA_COLUMNS, values, strict=True))


def _read_results(filepath: Path, skiprows: int) -> pd.DataFrame:
    engine = "xlrd" if filepath.suffix.lower() == ".xls" else "openpyxl"

    with pd.ExcelFile(filepath, engine=engine) as workbook:
        if SHEET_NAME not in workbook.sheet_names:
            raise ValueError(
                f"Sheet '{SHEET_NAME}' was not found. "
                f"Available sheets: {workbook.sheet_names}"
            )

        dataframe = pd.read_excel(
            workbook,
            sheet_name=SHEET_NAME,
            skiprows=skiprows,
        )

    dataframe.columns = dataframe.columns.astype(str).str.strip()
    return dataframe


def _non_empty(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.notna() & dataframe.astype(str).apply(
        lambda column: column.str.strip().ne("")
    )


def _clean_7500(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.shape[1] < 11:
        raise ValueError("7500 Fast file does not contain columns A through K.")

    non_empty = _non_empty(dataframe)
    fully_blank = ~non_empty.any(axis=1)
    only_a = non_empty.iloc[:, 0] & ~non_empty.iloc[:, 1:11].any(axis=1)
    return dataframe.loc[~fully_blank & ~only_a].copy()


def _clean_qs5(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.shape[1] < 3:
        raise ValueError("QS5 file does not contain enough columns.")

    non_empty = _non_empty(dataframe)
    fully_blank = ~non_empty.any(axis=1)
    only_a_b = (
        non_empty.iloc[:, :2].any(axis=1)
        & ~non_empty.iloc[:, 2:].any(axis=1)
    )
    return dataframe.loc[~fully_blank & ~only_a_b].copy()


def _get_column(dataframe: pd.DataFrame, *candidates: str) -> pd.Series:
    lookup = {
        str(column).strip().casefold(): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        key = candidate.casefold()
        if key in lookup:
            return dataframe[lookup[key]]

    return pd.Series(pd.NA, index=dataframe.index, dtype="object")


def _normalise(dataframe: pd.DataFrame, platform: str) -> pd.DataFrame:
    if platform == "7500":
        if dataframe.shape[1] <= 6:
            raise ValueError("7500 Fast file is missing source column G.")
        ct_values = dataframe.iloc[:, 6]
    elif platform == "QS5":
        if dataframe.shape[1] <= 11:
            raise ValueError("QS5 file is missing source column L.")
        ct_values = dataframe.iloc[:, 11]
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    result = pd.DataFrame(index=dataframe.index)
    result["Well"] = _get_column(dataframe, "Well")
    result["Sample Name"] = _get_column(dataframe, "Sample Name", "Sample")
    result["Target Name"] = _get_column(dataframe, "Target Name", "Detector")
    result["Task"] = _get_column(dataframe, "Task")
    result["Reporter"] = _get_column(dataframe, "Reporter")

    ct_text = ct_values.astype(str).str.strip().str.casefold()
    result["Ct"] = ct_values.mask(ct_text.eq("undetermined"), 40)
    return result


def read_qpcr_file(filepath: Path, platform: str) -> pd.DataFrame | None:
    filepath = Path(filepath)

    if platform == "7500":
        cleaned = _clean_7500(_read_results(filepath, skiprows=15))
    elif platform == "QS5":
        cleaned = _clean_qs5(_read_results(filepath, skiprows=22))
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    if cleaned.empty:
        print(f"Skipped [{platform}] {filepath.name}: No valid rows remained.")
        return None

    result = _normalise(cleaned, platform)

    for column, value in _extract_filename_metadata(filepath.name).items():
        result[column] = value

    result["Source File"] = filepath.name
    result = result.loc[:, OUTPUT_COLUMNS].copy()

    print(f"Processed [{platform}]: {filepath.name}")
    return result


def _collect(folder: Path, platform: str) -> list[pd.DataFrame]:
    folder = Path(folder)

    if not folder.is_dir():
        raise FileNotFoundError(f"{platform} input folder does not exist: {folder}")

    results: list[pd.DataFrame] = []

    for filepath in sorted(folder.iterdir()):
        if filepath.name.startswith("~$"):
            continue
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if "combined_" in filepath.name.casefold():
            continue

        try:
            result = read_qpcr_file(filepath, platform)
            if result is not None:
                results.append(result)
        except Exception as error:
            print(f"Error reading [{platform}] {filepath.name}: {error}")

    return results


def compile_mixed_qpcr(
    fast7500_folder: Path,
    qs5_folder: Path,
    output_file: Path,
) -> pd.DataFrame:
    results = [
        *_collect(Path(fast7500_folder), "7500"),
        *_collect(Path(qs5_folder), "QS5"),
    ]

    if not results:
        raise ValueError("No valid QS5 or 7500 Fast files were processed.")

    combined = pd.concat(results, ignore_index=True)
    combined = combined.loc[:, OUTPUT_COLUMNS].copy()

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    combined.to_excel(output_file, index=False)

    print(f"Saved combined qPCR data to: {output_file}")
    return combined
