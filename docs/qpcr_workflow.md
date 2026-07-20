# qPCR workflow

This document describes the reusable Swift-Stats qPCR readers and complements the example READMEs under `examples/qpcr/`.

## Supported instruments and workflows

Swift-Stats currently supports:

- Applied Biosystems QuantStudio 5 (QS5)
- Applied Biosystems 7500 Fast
- a mixed workflow that combines QS5 and 7500 Fast outputs into one standardised workbook

Supported source workbook formats are:

- `.xlsx`
- `.xls`
- `.xlsm`

Temporary Excel lock files beginning with `~$` are ignored.

## Required worksheet

Each source workbook must contain a worksheet named:

```text
Results
```

A file is skipped if the worksheet is absent.

## QS5 rows and columns read

The QS5 reader:

- reads the `Results` worksheet;
- skips the first 22 rows, so data reading begins at Excel row 23;
- reads source columns from A through AW;
- selects the following source-column positions:

```text
A, C, E:G, L, S:U, AV:AW
```

These are mapped to:

1. Well
2. Task
3. Sample Name
4. Target Name
5. Reporter
6. Ct
7. Automatic Baseline
8. Baseline Start
9. Baseline End
10. Call
11. Call Assessment

The reader requires the workbook to contain all columns through AW.

## 7500 Fast rows and columns read

The 7500 Fast reader:

- reads the `Results` worksheet;
- skips the first 15 rows;
- selects source columns corresponding to:

```text
A:E, G, Q:S, AM:AN
```

These are mapped to:

1. Well
2. Sample Name
3. Detector
4. Task
5. Reporter
6. Ct
7. Automatic Baseline
8. Baseline Start
9. Baseline End
10. Call
11. Call Assessment

The reader requires the workbook to contain all columns through AN.

## Cleaning rules

### QS5

The reader removes:

- fully blank rows;
- rows where information is present only in columns A and/or B;
- files with no valid rows after cleaning.

### 7500 Fast

The reader removes:

- fully blank rows;
- rows where only column A contains information and columns B through K are empty;
- files with no valid rows after cleaning.

Column headings are stripped of leading and trailing whitespace.

## Ct handling

For both readers:

```text
Undetermined
```

is matched without regard to case or surrounding spaces and replaced with:

```text
40
```

Other Ct values are retained as supplied by the source workbook.

## Filename metadata

Metadata is extracted from the first five underscore-separated filename components:

```text
YYYYMMDD_TestMethod_PlateNumber_Instrument_Operator
```

The values populate:

- Date
- Test method
- Plate number
- Instrument
- Operator

The date is validated against the `YYYYMMDD` format. If it is invalid, the output date is left blank.

Additional underscore-separated filename components are ignored for metadata extraction.

## QS5 output columns

The QS5 compiled workbook contains 17 columns:

1. Well
2. Task
3. Sample Name
4. Target Name
5. Reporter
6. Ct
7. Automatic Baseline
8. Baseline Start
9. Baseline End
10. Call
11. Call Assessment
12. Source File
13. Date
14. Test method
15. Plate number
16. Instrument
17. Operator

## 7500 Fast output columns

The 7500 Fast compiled workbook contains 17 columns:

1. Well
2. Sample Name
3. Detector
4. Task
5. Reporter
6. Ct
7. Automatic Baseline
8. Baseline Start
9. Baseline End
10. Call
11. Call Assessment
12. Source File
13. Date
14. Test method
15. Plate number
16. Instrument
17. Operator

## Mixed QS5 and 7500 Fast output columns

The mixed reader standardises both instruments to:

1. Well
2. Sample Name
3. Target Name
4. Task
5. Reporter
6. Ct
7. Date
8. Test method
9. Plate number
10. Instrument
11. Operator
12. Source File

For 7500 Fast files, the Detector field is used as the standardised Target Name value.

## Commands

Run all commands from the repository root:

```powershell
cd "C:\pythontraining\Swift-Stats"
```

### Compile QS5 files

```powershell
python scripts\compile_qs5.py --input "examples\qpcr\qs5\input" --output "examples\qpcr\qs5\expected_output\qs5_compiled.xlsx"
```

### Compile 7500 Fast files

```powershell
python scripts\compile_fast7500.py --input "examples\qpcr\fast7500\input" --output "examples\qpcr\fast7500\expected_output\fast7500_compiled.xlsx"
```

### Compile mixed QS5 and 7500 Fast files

```powershell
python scripts\compile_mixed_qpcr.py --fast7500-input "examples\qpcr\fast7500\input" --qs5-input "examples\qpcr\qs5\input" --output "examples\qpcr\mixed_qs5_fast7500\expected_output\combined_qpcr.xlsx"
```

## Required packages

Typical dependencies include:

```text
pandas
openpyxl
xlrd>=2.0.1
```

`xlrd` is required for legacy `.xls` files.
