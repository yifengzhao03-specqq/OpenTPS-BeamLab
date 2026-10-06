import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from beamlab.core.phantom import create_water_phantom
from beamlab.core.beam import create_parallel_opposed
from beamlab.core.dose_engine import calculate_dose


print()
print("========================================")
print("OpenTPS BeamLab - Full Pipeline Test")
print("========================================")


# ============================================================
# 1. CREATE PHANTOM
# ============================================================

phantom = create_water_phantom(
    size_mm=(400.0, 300.0, 400.0),
    voxel_mm=5.0,
)

print()
print("Phantom created:")
print(phantom.imageArray.shape)


# ============================================================
# 2. CREATE AP/PA BEAMS
# ============================================================

beams = create_parallel_opposed(
    field_size_mm=150.0,
    weights=(1.0, 1.0),
    isocenter=(0.0, 0.0, 0.0),
)

print()
print("Beams created:")
print(len(beams))

for i, beam in enumerate(beams, start=1):
    segment = beam.beamSegments[0]

    print(
        f"Beam {i}: "
        f"gantry = {segment.gantryAngle_degree} deg, "
        f"MU = {segment.mu}"
    )


# ============================================================
# 3. CALCULATE 6 MV DOSE
# ============================================================

dose = calculate_dose(
    ct=phantom,
    beams=beams,
    energy="6MV",
    prescription_cgy=200.0,
)


# ============================================================
# 4. VALIDATE
# ============================================================

cx = dose.shape[0] // 2
cy = dose.shape[1] // 2
cz = dose.shape[2] // 2

center_dose = float(
    dose[cx, cy, cz]
)

maximum_dose = float(
    np.max(dose)
)

print()
print("========================================")
print("RESULT")
print("========================================")

print("Dose shape:")
print(dose.shape)

print("Isocenter:")
print(center_dose, "cGy")

print("Maximum:")
print(maximum_dose, "cGy")


assert dose.shape == phantom.imageArray.shape
assert np.isfinite(dose).all()
assert center_dose > 0
assert abs(center_dose - 200.0) < 0.01


# ============================================================
# 5. SAVE
# ============================================================

output_dir = PROJECT_ROOT / "data"
output_dir.mkdir(
    parents=True,
    exist_ok=True,
)

output_file = (
    output_dir /
    "beamlab_full_pipeline_6MV.npy"
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
print("PASS: FULL BEAMLAB PIPELINE SUCCESSFUL")
print("========================================")