import sys
from pathlib import Path

import numpy as np


# ============================================================
# ADD PROJECT SRC TO PYTHON PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))


# ============================================================
# IMPORT BEAMLAB
# ============================================================

from beamlab.core.phantom import create_water_phantom
from beamlab.core.dose_engine import calculate_dose


# ============================================================
# IMPORT OPENTPS BEAM CLASSES
# ============================================================

from opentps.core.data.plan._planPhotonBeam import PlanPhotonBeam
from opentps.core.data.plan._planPhotonSegment import PlanPhotonSegment


# ============================================================
# CREATE OPEN FIELD
# ============================================================

def make_open_field(
    gantry_angle,
    field_size_mm=150.0,
):

    beam = PlanPhotonBeam()
    segment = PlanPhotonSegment()

    half_field = field_size_mm / 2.0

    segment.x_jaw_mm = [
        -half_field,
        half_field,
    ]

    segment.y_jaw_mm = [
        -half_field,
        half_field,
    ]

    segment.isocenterPosition_mm = [
        0.0,
        0.0,
        0.0,
    ]

    segment.gantryAngle_degree = float(
        gantry_angle
    )

    segment.couchAngle_degree = 0.0
    segment.beamLimitingDeviceAngle_degree = 0.0

    segment.mu = 100.0

    segment.xBeamletSpacing_mm = 5.0
    segment.yBeamletSpacing_mm = 5.0

    mlc = []

    for y0 in np.arange(
        -half_field,
        half_field,
        5.0,
    ):

        mlc.append(
            [
                y0,
                y0 + 5.0,
                -half_field,
                half_field,
            ]
        )

    segment.Xmlc_mm = np.array(
        mlc,
        dtype=float,
    )

    beam.appendBeamSegment(segment)

    return beam


# ============================================================
# TEST
# ============================================================

print()
print("========================================")
print("OpenTPS BeamLab")
print("6 MV CCC Dose Calculation Test")
print("========================================")


# Create water phantom
phantom = create_water_phantom()

print()
print("Phantom:")
print(phantom.imageArray.shape)


# Create AP / PA beams
beams = [
    make_open_field(0.0),
    make_open_field(180.0),
]

print()
print("Beams created:")
print(len(beams))


# Calculate dose
dose = calculate_dose(
    ct=phantom,
    beams=beams,
    energy="6MV",
    prescription_cgy=200.0,
)


# ============================================================
# CHECK RESULT
# ============================================================

print()
print("========================================")
print("RESULT")
print("========================================")

print("Dose shape:")
print(dose.shape)

cx = dose.shape[0] // 2
cy = dose.shape[1] // 2
cz = dose.shape[2] // 2

center_dose = float(
    dose[cx, cy, cz]
)

maximum_dose = float(
    np.max(dose)
)

minimum_dose = float(
    np.min(dose)
)

print()
print("Isocenter dose:")
print(center_dose, "cGy")

print()
print("Maximum dose:")
print(maximum_dose, "cGy")

print()
print("Minimum dose:")
print(minimum_dose, "cGy")


# ============================================================
# VALIDATION
# ============================================================

if not np.isfinite(dose).all():
    raise RuntimeError(
        "FAIL: Dose contains NaN or infinite values."
    )

if center_dose <= 0:
    raise RuntimeError(
        "FAIL: Isocenter dose is zero or negative."
    )

if abs(center_dose - 200.0) > 0.01:
    raise RuntimeError(
        "FAIL: Isocenter normalization is incorrect."
    )


print()
print("PASS: 6 MV CCC dose calculation successful.")
print("PASS: Isocenter normalized to 200 cGy.")
print("PASS: Dose array contains valid values.")


# ============================================================
# SAVE RESULT
# ============================================================

output_dir = PROJECT_ROOT / "data"
output_dir.mkdir(
    parents=True,
    exist_ok=True,
)

output_file = (
    output_dir /
    "test_6MV_APPA_15x15.npy"
)

np.save(
    output_file,
    dose,
)

print()
print("Saved:")
print(output_file)

print()
print("========================================")
print("TEST COMPLETE")
print("========================================")