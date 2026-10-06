import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from beamlab.core.beam import (
    create_open_field,
    create_parallel_opposed,
    create_four_field_box,
)


print("========================================")
print("OpenTPS BeamLab - Beam Test")
print("========================================")


# ============================================================
# TEST 1 - SINGLE OPEN FIELD
# ============================================================

print()
print("TEST 1 - Single Open Field")

beam = create_open_field(
    gantry_angle=0.0,
    field_size_mm=150.0,
)

print("Number of segments:")
print(len(beam.beamSegments))

segment = beam.beamSegments[0]

print("Gantry angle:")
print(segment.gantryAngle_degree)

print("X jaws:")
print(segment.x_jaw_mm)

print("Y jaws:")
print(segment.y_jaw_mm)

print("MU:")
print(segment.mu)

print("MLC shape:")
print(segment.Xmlc_mm.shape)

assert len(beam.beamSegments) == 1
assert segment.gantryAngle_degree == 0.0
assert segment.x_jaw_mm == [-75.0, 75.0]
assert segment.y_jaw_mm == [-75.0, 75.0]
assert segment.mu == 100.0

print("PASS: Single open field")


# ============================================================
# TEST 2 - PARALLEL OPPOSED
# ============================================================

print()
print("TEST 2 - Parallel Opposed AP/PA")

beams = create_parallel_opposed(
    field_size_mm=150.0,
    weights=(1.0, 1.0),
)

print("Number of beams:")
print(len(beams))

angles = [
    beam.beamSegments[0].gantryAngle_degree
    for beam in beams
]

print("Gantry angles:")
print(angles)

assert len(beams) == 2
assert angles == [0.0, 180.0]

print("PASS: Parallel opposed beams")


# ============================================================
# TEST 3 - FOUR FIELD BOX
# ============================================================

print()
print("TEST 3 - Four Field Box")

beams = create_four_field_box(
    field_size_mm=150.0,
    weights=(1.0, 1.0, 1.0, 1.0),
)

print("Number of beams:")
print(len(beams))

angles = [
    beam.beamSegments[0].gantryAngle_degree
    for beam in beams
]

print("Gantry angles:")
print(angles)

assert len(beams) == 4
assert angles == [
    0.0,
    90.0,
    180.0,
    270.0,
]

print("PASS: Four-field box")


# ============================================================
# DONE
# ============================================================

print()
print("========================================")
print("PASS: ALL BEAM TESTS SUCCESSFUL")
print("========================================")