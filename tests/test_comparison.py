import sys
from pathlib import Path

import numpy as np


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


from beamlab.core.comparison import (
    extract_center_profiles,
    compare_doses,
)


# ============================================================
# CREATE TEST DOSE MATRICES
# ============================================================

shape = (
    80,
    60,
    80,
)

dose_6mv = np.zeros(
    shape,
    dtype=float,
)

dose_18mv = np.zeros(
    shape,
    dtype=float,
)


# Artificial center distributions
cx = shape[0] // 2
cy = shape[1] // 2
cz = shape[2] // 2


dose_6mv[
    cx,
    cy,
    cz,
] = 200.0


dose_18mv[
    cx,
    cy,
    cz,
] = 200.0


dose_6mv[
    cx - 1,
    cy,
    cz,
] = 180.0


dose_18mv[
    cx - 1,
    cy,
    cz,
] = 190.0


# ============================================================
# TEST PROFILES
# ============================================================

profiles = extract_center_profiles(
    dose_6mv,
    voxel_mm=5.0,
)


assert len(
    profiles["x"]["dose"]
) == 80


assert len(
    profiles["y"]["dose"]
) == 60


assert len(
    profiles["z"]["dose"]
) == 80


# ============================================================
# TEST COMPARISON
# ============================================================

result = compare_doses(
    dose_6mv,
    dose_18mv,
    voxel_mm=5.0,
)


assert result[
    "difference"
].shape == shape


assert (
    result[
        "difference"
    ][
        cx - 1,
        cy,
        cz,
    ]
    == 10.0
)


print()
print(
    "PASS: BeamLab comparison backend works."
)

print(
    "Maximum 6 MV:",
    result["max_a"],
)

print(
    "Maximum 18 MV:",
    result["max_b"],
)

print(
    "Maximum absolute difference:",
    result["max_absolute_difference"],
)