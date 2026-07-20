**Zeiss LSM imaging example**



This directory contains example Zeiss .lsm microscopy files for testing the Swift-Stats LSM processing workflow.



Supported three-channel staining



**The current workflow processes:**



mCherry

GFP

DAPI



The default fallback channel assignments are:



Channel 1: mCherry

Channel 2: GFP

Channel 3: DAPI



When available, the script also attempts to identify channel names from the LSM metadata.



Folder structure

lsm/

├── README.md

├── two\_channel/

├── three\_channel/

└── expected\_output/

three\_channel/



**Place example three-channel .lsm files in this folder.**



Example:



example\_mcherry\_gfp\_dapi.lsm

two\_channel/



Reserved for two-channel LSM workflows, such as Alexa Fluor 633 and DAPI.



The current process\_lsm.py launcher is configured primarily for the three-channel mCherry, GFP and DAPI workflow.



expected\_output/



Contains the generated plots, tabular reports and PowerPoint quality-control presentation.



Install requirements



**Run from the repository root:**



python -m pip install numpy pandas matplotlib tifffile openpyxl python-pptx

Run the three-channel example

python scripts\\process\_lsm.py --input "examples\\imaging\\lsm\\three\_channel" --output "examples\\imaging\\lsm\\expected\_output"

Specify channel numbers manually



**Channel numbers entered in the command are one-based.**



python scripts\\process\_lsm.py --input "examples\\imaging\\lsm\\three\_channel" --output "examples\\imaging\\lsm\\expected\_output" --mcherry-channel 1 --gfp-channel 2 --dapi-channel 3

Optional processing settings



**Change the normalised signal threshold:**



python scripts\\process\_lsm.py --input "examples\\imaging\\lsm\\three\_channel" --output "examples\\imaging\\lsm\\expected\_output" --threshold 0.1



Run without creating a PowerPoint file:



python scripts\\process\_lsm.py --input "examples\\imaging\\lsm\\three\_channel" --output "examples\\imaging\\lsm\\expected\_output" --no-pptx



Run without creating an Excel report:



python scripts\\process\_lsm.py --input "examples\\imaging\\lsm\\three\_channel" --output "examples\\imaging\\lsm\\expected\_output" --no-xlsx

Output files



The default output includes:



expected\_output/

├── data/

│   ├── lsm\_microscopy\_report.csv

│   ├── lsm\_microscopy\_report.xlsx

│   └── lsm\_qc\_presentation.pptx

└── plots/

&#x20;   └── layout\_<source-file-name>.png



The four-panel plot contains:



mCherry

GFP

DAPI

merged RGB image



**The tabular report includes mCherry/GFP overlap measurements and processing quality metrics.**



**Data requirements**



Example files should be anonymised, synthetic or approved for public distribution.



Do not upload confidential or identifiable microscopy data

