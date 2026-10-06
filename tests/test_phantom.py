import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from beamlab.core.phantom import create_water_phantom


phantom = create_water_phantom()

print("================================")
print("OpenTPS BeamLab - Phantom Test")
print("================================")

print("Name:")
print(phantom.name)

print("\nShape:")
print(phantom.imageArray.shape)

print("\nSpacing:")
print(phantom.spacing)

print("\nOrigin:")
print(phantom.origin)

print("\nPASS: Water phantom created successfully.")