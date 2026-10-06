import sys
from pathlib import Path

import numpy as np

from PySide6.QtWidgets import QApplication


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

SRC_DIR = (
    PROJECT_ROOT / "src"
)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR),
    )


from beamlab.visualization.difference_viewer import (
    DifferenceViewer,
)


# ============================================================
# CREATE CONTROLLED TEST DATA
# ============================================================

shape = (
    80,
    60,
    80,
)

dose_6mv = np.ones(
    shape,
    dtype=float,
) * 200.0

dose_18mv = dose_6mv.copy()


cx = shape[0] // 2
cy = shape[1] // 2
cz = shape[2] // 2


# ------------------------------------------------------------
# REGION 1:
# 18 MV is 20 cGy HIGHER
# ------------------------------------------------------------

dose_18mv[
    cx - 15:cx,
    cy - 10:cy + 10,
    cz - 10:cz + 10,
] += 20.0


# ------------------------------------------------------------
# REGION 2:
# 18 MV is 20 cGy LOWER
# Therefore 6 MV is higher.
# ------------------------------------------------------------

dose_18mv[
    cx:cx + 15,
    cy - 10:cy + 10,
    cz - 10:cz + 10,
] -= 20.0


# ============================================================
# QT
# ============================================================

app = QApplication(
    sys.argv
)

viewer = DifferenceViewer()

viewer.setWindowTitle(
    "BeamLab Difference Viewer Test"
)

viewer.resize(
    1000,
    750,
)

viewer.set_doses(
    dose_6mv=dose_6mv,
    dose_18mv=dose_18mv,
    voxel_mm=5.0,
    prescription_cgy=200.0,
)

viewer.show()

sys.exit(
    app.exec()
)