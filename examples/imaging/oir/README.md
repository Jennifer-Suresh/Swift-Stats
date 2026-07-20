**Olympus OIR imaging example**



This directory contains example Olympus .oir microscopy files for testing the Swift-Stats OIR processing workflow.



**Supported three-channel staining**



The current workflow processes:



DAPI

GFP

Mitotracker Red



**The default channel assignments are:**



Channel 1: DAPI

Channel 2: GFP

Channel 3: Mitotracker Red

Folder structure

oir/

├── README.md

├── two\_channel/

├── three\_channel/

└── expected\_output/

three\_channel/



**Place example three-channel .oir files in this folder.**



**Example:**



example\_dapi\_gfp\_mitotracker.oir

two\_channel/



Reserved for future two-channel OIR workflows.



expected\_output/



Contains the generated plots, tabular reports and PowerPoint quality-control presentation.



**Install requirements**



**Run from the repository root:**



python -m pip install numpy pandas matplotlib oirfile openpyxl python-pptx

Run the three-channel example

python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output"

Specify channel numbers manually



Channel numbers entered in the command are one-based.



python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output" --dapi-channel 1 --gfp-channel 2 --mitotracker-channel 3



For example, where GFP is Channel 1, Mitotracker is Channel 2 and DAPI is Channel 3:



python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output" --gfp-channel 1 --mitotracker-channel 2 --dapi-channel 3

Optional processing settings



**Change the normalised signal threshold:**



python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output" --threshold 0.1



Run without creating a PowerPoint file:



python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output" --no-pptx



Run without creating an Excel report:



python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output" --no-xlsx

Output files



The default output includes:



expected\_output/

├── data/

│   ├── oir\_microscopy\_report.csv

│   ├── oir\_microscopy\_report.xlsx

│   └── oir\_qc\_presentation.pptx

└── plots/

&#x20;   └── layout\_<source-file-name>.png



The four-panel plot contains:



DAPI

GFP

Mitotracker Red

merged RGB image



The tabular report includes GFP/Mitotracker overlap measurements and processing quality metrics.



**Data requirements**



Example files should be anonymised, synthetic or approved for public distribution.



Do not upload confidential or identifiable microscopy data.

