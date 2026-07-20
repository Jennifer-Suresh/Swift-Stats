</> Markdown
# Swift-Stats
Swift Stats provides Python workflows for reading, cleaning and
compiling qPCR and confocal microscopy data.

## Supported data

### qPCR
- Applied Biosystems QuantStudio 5
- Applied Biosystems 7500 Fast
- Mixed QS5 and 7500 Fast folder compilation

## Downstream examples

- [qPCR data cleanup, compilation and JMP analysis](downstream_examples/qpcr_summary/qpcr_data_cleanup_compilation_jmp_analysis.pdf)

### Confocal imaging
- Zeiss LSM
- Olympus OIR
- Two-channel and three-channel image files

## Repository contents

- `src/`: reusable Python modules
- `scripts/`: command-line scripts
- `examples/`: sample inputs and expected outputs
- `downstream_examples/`: processed tables and figures
- `tests/`: automated checks
- `docs/`: detailed instructions

## Installation

```bash
git clone https://github.com/Jennifer-Suresh/Swift-Stats.git
cd Swift-Stats

python -m venv .venv
