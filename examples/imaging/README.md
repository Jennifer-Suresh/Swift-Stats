**Imaging examples**



This directory contains example workflows for processing confocal microscopy files with Swift-Stats.



**The imaging workflows support:**



Zeiss .lsm files

Olympus .oir files

maximum-intensity projection

channel validation and contrast normalisation

generation of individual channel panels

RGB merged images

overlap-percentage calculations

CSV and Excel output reports

PowerPoint presentations for rapid visual quality control

Directory structure

imaging/

├── README.md

├── lsm/

│   ├── README.md

│   ├── two\_channel/

│   ├── three\_channel/

│   └── expected\_output/

└── oir/

&#x20;   ├── README.md

&#x20;   ├── two\_channel/

&#x20;   ├── three\_channel/

&#x20;   └── expected\_output/

LSM workflow



The current three-channel LSM workflow is designed for:



mCherry

GFP

DAPI



The default channel order is:



Channel 1: mCherry

Channel 2: GFP

Channel 3: DAPI



**Run from the repository root:**



python scripts\\process\_lsm.py --input "examples\\imaging\\lsm\\three\_channel" --output "examples\\imaging\\lsm\\expected\_output"

OIR workflow



The current three-channel OIR workflow is designed for:



DAPI

GFP

Mitotracker Red



The default channel order is:



Channel 1: DAPI

Channel 2: GFP

Channel 3: Mitotracker Red



**Run from the repository root:**



python scripts\\process\_oir.py --input "examples\\imaging\\oir\\three\_channel" --output "examples\\imaging\\oir\\expected\_output"

Generated outputs



Each workflow creates:



expected\_output/

├── data/

│   ├── microscopy report in CSV format

│   ├── microscopy report in Excel format

│   └── PowerPoint QC presentation

└── plots/

&#x20;   └── four-panel microscopy summary PNG files



The report includes processing status, channel signal metrics, channel assignments, positive-pixel counts and overlap percentages.



**Example data**



Only small, anonymised or synthetic microscopy files should be included in this public repository.



**Do not upload:**



identifiable patient or donor information

confidential experimental data

unpublished proprietary datasets

files that have not been approved for public release



**Large .lsm and .oir files should be tracked with Git LFS.**

