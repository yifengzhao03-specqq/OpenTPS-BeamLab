\# OpenTPS BeamLab



OpenTPS BeamLab is a Python-based research tool for photon beam dose calculation, comparison, and photon kernel development within the OpenTPS framework.



\## Current Features



\- 6 MV and 18 MV photon dose calculation

\- Collapsed Cone Convolution (CCC) dose calculation using OpenTPS

\- AP/PA and four-field box beam geometries

\- Adjustable field size and beam weights

\- 3D water phantom generation

\- Axial, coronal, and sagittal dose visualization

\- Dose profile comparison between 6 MV and 18 MV

\- Dose difference visualization

\- Dose matrix and figure export

\- EDKnrc photon kernel inspection

\- OpenTPS-compatible 18 MV kernel construction

\- Kernel structure validation

\- Comparison of generated kernels with installed OpenTPS kernels



\## Photon Kernel Workflow



The current kernel-development workflow is:



EDKnrc energy-deposition kernels  

→ BeamLab EDK reader  

→ OpenTPS-compatible kernel construction  

→ Kernel validation  

→ Comparison with reference OpenTPS kernel



The 18 MV kernel builder combines the existing low-energy OpenTPS kernel data with EDKnrc-generated high-energy kernels.



\## Kernel Validation



The generated 18 MV kernel has been tested against the working OpenTPS 18 MV kernel.



The energy-deposition component files and total kernel reproduce the reference kernel exactly. The fluence spectrum is numerically equivalent within floating-point precision.



\## Project Structure



```text

OpenTPS-BeamLab/

├── src/

│   └── beamlab/

│       ├── core/

│       ├── gui/

│       ├── kernel/

│       └── visualization/

├── tests/

├── data/

├── docs/

└── examples/

