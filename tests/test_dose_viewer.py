import sys
from pathlib import Path

import numpy as np

from PySide6.QtWidgets import QApplication


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(
    0,
    str(SRC_DIR),
)


from beamlab.visualization.dose_viewer import (
    DoseViewer,
)


# ============================================================
# LOAD OUR REAL 6 MV DOSE
# ============================================================

dose_file = (
    PROJECT_ROOT
    / "data"
    / "beamlab_full_pipeline_6MV.npy"
)

if not dose_file.exists():

    raise FileNotFoundError(
        f"Dose file not found:\n{dose_file}"
    )


dose = np.load(
    dose_file
)


print()
print("========================================")
print("OpenTPS BeamLab - Dose Viewer Test")
print("========================================")

print("Dose file:")
print(dose_file)

print()

print("Dose shape:")
print(dose.shape)

print()

print("Dose maximum:")
print(np.max(dose))


# ============================================================
# QT
# ============================================================

app = QApplication(
    sys.argv
)

viewer = DoseViewer()

viewer.setWindowTitle(
    "OpenTPS BeamLab - Dose Viewer Test"
)

viewer.resize(
    900,
    700,
)

viewer.set_dose(
    dose=dose,
    voxel_mm=5.0,
    prescription_cgy=200.0,
)

viewer.show()

sys.exit(
    app.exec()
)