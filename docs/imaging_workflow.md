# Imaging workflow

This document describes the Swift-Stats confocal microscopy workflows and complements the example READMEs under `examples/imaging/`.

## Supported formats

Swift-Stats currently supports:

- Zeiss `.lsm` files through `tifffile`
- Olympus `.oir` files through `oirfile`

The readers process files directly inside the specified input folder. They do not recursively search nested subfolders.

## Supported channel counts

The current launcher scripts are designed for three-channel workflows.

### LSM workflow

Default biological channels:

1. mCherry
2. GFP
3. DAPI

### OIR workflow

Default biological channels:

1. DAPI
2. GFP
3. Mitotracker Red

The repository also contains `two_channel` example folders, but the current `process_lsm.py` and `process_oir.py` launchers are configured for three-channel processing.

## Image dimensionality and maximum projection

The shared processing code standardises supported image arrays to:

```text
Channel, Y, X
```

Common layouts include:

- `C, Y, X`
- `Z, C, Y, X`
- `T, Z, C, Y, X`

Acquisition dimensions such as time and Z are collapsed by maximum-intensity projection.

For non-standard layouts, the user can provide a channel-axis index using:

```text
--channel-axis
```

## How channels are selected

### LSM

The LSM reader first attempts to identify channel names from Zeiss metadata.

Recognised metadata terms include:

- DAPI, Hoechst or blue
- GFP or green
- mCherry, cherry or red

Where metadata is absent or incomplete, the fallback order is:

```text
mCherry = Channel 1
GFP = Channel 2
DAPI = Channel 3
```

The fallback channels can be overridden from the command line.

### OIR

The current optimised OIR reader uses explicit channel assignments supplied by the launcher, with the default order:

```text
DAPI = Channel 1
GFP = Channel 2
Mitotracker = Channel 3
```

These assignments can be overridden from the command line.

## Channel validation and normalisation

Each projected channel is checked for:

- finite pixel values;
- non-zero variance;
- an SNR-like metric above the configured threshold.

The default SNR threshold is:

```text
2.5
```

The adaptive lower contrast threshold is calculated from the channel mean and standard deviation. The default lower-threshold multiplier is:

```text
1.2
```

Images with a required blank or low-signal channel are marked as skipped.

## Signal masks and overlap measurements

The default normalised mask threshold is:

```text
0.1
```

### LSM comparison

The LSM workflow compares:

```text
mCherry-positive pixels versus GFP-positive pixels
```

### OIR comparison

The OIR workflow compares:

```text
GFP-positive pixels versus Mitotracker-positive pixels
```

The report may contain:

- Filename
- File_Type
- Status
- Notes
- Primary_Channel
- Secondary_Channel
- channel assignments
- Threshold
- channel SNR metrics
- Channel_A_Positive_Pixels
- Channel_B_Positive_Pixels
- Overlap_Pixels
- Union_Pixels
- Overlay_Percentage
- A_Overlap_Percentage
- B_Overlap_Percentage

`Overlay_Percentage` is calculated as the overlap divided by the union of the two positive-pixel masks.

## Generated plots

Each successfully processed image produces a four-panel PNG.

### LSM panels

1. mCherry
2. GFP
3. DAPI
4. merged RGB image

### OIR panels

1. DAPI
2. GFP
3. Mitotracker Red
4. merged RGB image

## Output structure

Each run creates:

```text
expected_output/
├── data/
│   ├── <format>_microscopy_report.csv
│   ├── <format>_microscopy_report.xlsx
│   └── <format>_qc_presentation.pptx
└── plots/
    └── layout_<source-file-name>.png
```

The Excel report can be disabled with `--no-xlsx`. The PowerPoint report can be disabled with `--no-pptx`.

## Memory requirements

Microscopy processing can require substantial memory because each source file is:

1. loaded into a NumPy array;
2. projected across acquisition dimensions;
3. converted to floating-point normalised channels;
4. combined into an RGB array;
5. rendered as a high-resolution figure.

Memory use depends on:

- image width and height;
- number of Z slices;
- number of time points;
- number of channels;
- source bit depth;
- the number of temporary arrays created during normalisation.

The readers process files one at a time, which limits batch memory use. However, a single large multidimensional file can still require several times its on-disk size in RAM.

For large files:

- close memory-intensive applications;
- process a small test set first;
- avoid unnecessarily high output DPI;
- use `--no-pptx` if only tabular results are required;
- split very large batches into smaller input folders;
- confirm the channel axis before processing the full batch.

## Example commands

Run commands from:

```powershell
cd "C:\pythontraining\Swift-Stats"
```

### LSM default three-channel workflow

```powershell
python scripts\process_lsm.py --input "examples\imaging\lsm\three_channel" --output "examples\imaging\lsm\expected_output"
```

### LSM with explicit channel assignments

```powershell
python scripts\process_lsm.py --input "examples\imaging\lsm\three_channel" --output "examples\imaging\lsm\expected_output" --mcherry-channel 1 --gfp-channel 2 --dapi-channel 3
```

### OIR default three-channel workflow

```powershell
python scripts\process_oir.py --input "examples\imaging\oir\three_channel" --output "examples\imaging\oir\expected_output"
```

### OIR with explicit channel assignments

```powershell
python scripts\process_oir.py --input "examples\imaging\oir\three_channel" --output "examples\imaging\oir\expected_output" --dapi-channel 1 --gfp-channel 2 --mitotracker-channel 3
```

### Skip PowerPoint generation

```powershell
python scripts\process_lsm.py --input "examples\imaging\lsm\three_channel" --output "examples\imaging\lsm\expected_output" --no-pptx
```

### Skip Excel generation

```powershell
python scripts\process_oir.py --input "examples\imaging\oir\three_channel" --output "examples\imaging\oir\expected_output" --no-xlsx
```

## Required packages

Typical imaging dependencies include:

```text
numpy
pandas
matplotlib
tifffile
oirfile
openpyxl
python-pptx
```
