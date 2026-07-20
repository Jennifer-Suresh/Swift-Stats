# Troubleshooting

This guide covers common Swift-Stats qPCR, imaging and repository problems.

## `Results` sheet not found

### Example message

```text
Sheet 'Results' was not found
```

### Cause

The qPCR workbook does not contain a worksheet named exactly `Results`, or the workbook is not the expected instrument export.

### Resolution

List the workbook sheet names in Python or open the workbook in Excel and confirm the sheet name.

The supported readers expect:

```text
Results
```

Do not rename the sheet unless the source export is known to be compatible.

## Required columns missing

### QS5

The QS5 reader expects source data through column AW.

A common message is:

```text
File does not contain all required columns through AW
```

### 7500 Fast

The 7500 Fast reader expects source data through column AN.

A common message is:

```text
Required columns through AN are missing
```

### Resolution

- Confirm the correct instrument export was selected.
- Confirm the workbook is not a summary-only export.
- Do not delete or rearrange source columns before running the reader.
- Compare the file with a known working example.
- Confirm the correct reader is being used for the instrument.

## `Undetermined` Ct value

`Undetermined` Ct values are intentionally replaced with:

```text
40
```

This supports consistent downstream numeric analysis.

If a different rule is required, change the Ct handling in the reader before processing and document the change.

Do not manually mix different Ct replacement rules in one compiled dataset.

## Unsupported file type

Supported qPCR formats are:

```text
.xlsx
.xls
.xlsm
```

Supported microscopy formats are:

```text
.lsm
.oir
```

Files with other extensions are ignored or rejected.

For a legacy `.xls` error, install or upgrade `xlrd`:

```powershell
python -m pip install --upgrade "xlrd>=2.0.1"
```

## Git LFS file not downloaded

### Symptoms

- microscopy files appear very small;
- a file opens as text;
- the content starts with a Git LFS pointer;
- the imaging reader cannot parse the file.

### Resolution

Install and initialise Git LFS:

```powershell
git lfs install
```

Download the actual large files:

```powershell
git lfs pull
```

Check tracked files:

```powershell
git lfs ls-files
```

The repository `.gitattributes` should include entries such as:

```text
*.lsm filter=lfs diff=lfs merge=lfs -text
*.oir filter=lfs diff=lfs merge=lfs -text
```

## Python package import error

### Example messages

```text
ModuleNotFoundError: No module named 'swift_stats'
ModuleNotFoundError: No module named 'oirfile'
ModuleNotFoundError: No module named 'pptx'
```

### Resolution

Move to the repository root:

```powershell
cd "C:\pythontraining\Swift-Stats"
```

Install the project in editable mode:

```powershell
python -m pip install -e .
```

Install the dependencies:

```powershell
python -m pip install numpy pandas matplotlib tifffile oirfile openpyxl python-pptx "xlrd>=2.0.1"
```

Test imports:

```powershell
python -c "import swift_stats, numpy, pandas, matplotlib, tifffile, oirfile, openpyxl, pptx, xlrd; print('Imports successful')"
```

## Input folder does not exist

### Cause

The command was run from the wrong folder or the relative path was mistyped.

### Resolution

Move to the repository root:

```powershell
cd "C:\pythontraining\Swift-Stats"
```

Check the location:

```powershell
Get-Location
```

Then verify the expected input folder:

```powershell
Get-ChildItem "examples\qpcr\qs5\input"
```

or:

```powershell
Get-ChildItem "examples\imaging\lsm\three_channel"
```

## No supported files found

### Cause

- the input folder is empty;
- files are inside an extra nested folder;
- extensions are incorrect;
- the wrong input directory was supplied.

### Resolution

Place files directly inside the input folder named in the command.

For example:

```text
examples\imaging\lsm\three_channel\example.lsm
```

not:

```text
examples\imaging\lsm\three_channel\extra_folder\example.lsm
```

## Imaging channel-count error

### Example message

```text
Projected image has only 2 channels
```

### Cause

The file does not contain the three channels expected by the current launcher, or the channel axis was identified incorrectly.

### Resolution

- confirm the source file contains three channels;
- verify the acquisition order;
- provide explicit channel numbers;
- use `--channel-axis` for a non-standard array layout;
- test one file before processing a large batch.

## Imaging channel skipped for low signal

### Example messages

```text
Channel DAPI has zero variance
Channel GFP lacks signal
```

### Cause

A required channel is blank or does not exceed the default SNR criterion.

### Resolution

- inspect the original image;
- verify channel assignments;
- confirm the file was fully downloaded;
- use a lower `--snr-threshold` only when scientifically justified;
- document any changed threshold.

## PowerPoint was not created

### Cause

- `python-pptx` is not installed;
- no image was successfully processed;
- `--no-pptx` was used.

### Resolution

Install the package:

```powershell
python -m pip install python-pptx
```

Then rerun the imaging workflow without `--no-pptx`.

## Excel report was not created

### Cause

- `openpyxl` is missing;
- `--no-xlsx` was used.

### Resolution

Install:

```powershell
python -m pip install openpyxl
```

Then rerun without `--no-xlsx`.

## Git push rejected with `fetch first`

### Cause

The remote branch contains commits not present locally.

### Resolution

After committing local work:

```powershell
git pull --rebase origin main
git push origin main
```

Do not use force push unless the consequences are fully understood.

## `__pycache__` or `.egg-info` appears

These are generated Python files and should normally not be committed.

Add to `.gitignore`:

```text
__pycache__/
*.py[cod]
*.egg-info/
```

Remove generated folders locally:

```powershell
Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" |
    Remove-Item -Recurse -Force

Remove-Item "src\swift_stats.egg-info" -Recurse -Force
```
