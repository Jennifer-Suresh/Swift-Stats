# Filename conventions

Swift-Stats extracts qPCR metadata from the source filename.

## Recommended pattern

```text
YYYYMMDD_TestMethod_PlateNumber_Instrument_Operator.ext
```

Example:

```text
20231214_test_p01_7500fast-instr1_op4_data.xls
```

The readers use the first five underscore-separated filename components. Extra components after the operator are ignored for metadata extraction.

## Components

### `YYYYMMDD`

The experiment or acquisition date in year-month-day order without separators.

Example:

```text
20231214
```

This becomes:

```text
Date = 20231214
```

The date is validated using the `YYYYMMDD` format. An invalid date produces a blank Date value.

### `TestMethod`

A concise identifier for the assay, test or sample category.

Examples:

```text
test
trial
sample
```

This becomes the `Test method` output column.

Avoid underscores inside this component because underscores are used as separators.

### `PlateNumber`

The plate, run or batch identifier.

Examples:

```text
p01
p14
p31r1
```

This becomes the `Plate number` output column.

### `Instrument`

The instrument or instrument-instance identifier.

Examples:

```text
qs5-instr1
7500fast-instr2
```

This becomes the `Instrument` output column.

### `Operator`

The operator identifier.

Examples:

```text
op1
op4
```

This becomes the `Operator` output column.

## File extension

Supported qPCR extensions include:

```text
.xlsx
.xls
.xlsm
```

Use the extension produced by the source software where possible.

## Complete examples

### QS5

```text
20230818_test_p14_qs5-instr1_op1.xlsx
```

Parsed metadata:

```text
Date = 20230818
Test method = test
Plate number = p14
Instrument = qs5-instr1
Operator = op1
```

### 7500 Fast

```text
20231214_test_p01_7500fast-instr1_op4_data.xls
```

Parsed metadata:

```text
Date = 20231214
Test method = test
Plate number = p01
Instrument = 7500fast-instr1
Operator = op4
```

The extra component `data` is ignored.

## Naming recommendations

- Use exactly one underscore between metadata components.
- Do not use underscores inside a component.
- Keep dates in `YYYYMMDD` format.
- Use stable, non-identifying operator codes for public examples.
- Avoid spaces where possible.
- Do not include confidential patient, donor or study identifiers.
- Keep the original extension.
- Ensure filenames are unique within an input folder.

## Missing components

If fewer than five components are present, unavailable metadata fields are left blank.

For example:

```text
20231214_test_p01.xlsx
```

does not provide Instrument or Operator metadata.

## Additional components

If more than five underscore-separated components are present, only the first five are used.

For example:

```text
20231214_test_p01_7500fast-instr1_op4_data_export1.xls
```

is interpreted using:

```text
20231214
test
p01
7500fast-instr1
op4
```
