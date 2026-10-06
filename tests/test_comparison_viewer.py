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


from beamlab.visualization.comparison_viewer import (
    ComparisonViewer,
)


# ============================================================
# FIND DOSE FILES
# ============================================================

data_dir = (
    PROJECT_ROOT / "data"
)

file_6mv = (
    data_dir /
    "test_6MV_APPA_15x15.npy"
)


# ============================================================
# LOAD 6 MV
# ============================================================

if not file_6mv.exists():

    raise FileNotFoundError(
        f"6 MV dose file not found:\n{file_6mv}"
    )


dose_6mv = np.load(
    file_6mv
)


# ============================================================
# TEMPORARY 18 MV TEST DATA
# ============================================================

# For this GUI-component test only, create a modified copy.
# This is NOT a physical 18 MV dose calculation.
#
# We only want to verify that ComparisonViewer correctly
# displays two different 3D matrices.

dose_18mv = (
    dose_6mv.copy()
)

cx = dose_18mv.shape[0] // 2
cy = dose_18mv.shape[1] // 2
cz = dose_18mv.shape[2] // 2


# Make the Y profile slightly different
for offset in range(
    -20,
    21,
):

    index = cy + offset

    if (
        index >= 0
        and
        index < dose_18mv.shape[1]
    ):

        factor = (
            1.0
            +
            0.15
            *
            abs(offset)
            /
            20.0
        )

        dose_18mv[
            cx,
            index,
            cz,
        ] *= factor


# ============================================================
# QT
# ============================================================

app = QApplication(
    sys.argv
)

viewer = ComparisonViewer()

viewer.setWindowTitle(
    "BeamLab Comparison Viewer Test"
)

viewer.resize(
    1000,
    700,
)

viewer.set_doses(
    dose_6mv=dose_6mv,
    dose_18mv=dose_18mv,
    voxel_mm=5.0,
)

viewer.show()

sys.exit(
    app.exec()
)