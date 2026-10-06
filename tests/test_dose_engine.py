import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))


from beamlab.core.dose_engine import (
    get_kernel_path,
    inspect_kernel,
)


print("========================================")
print("OpenTPS BeamLab - Dose Engine Test")
print("========================================")


for energy in ["6MV", "18MV"]:

    print()
    print("----------------------------------------")
    print(f"Testing {energy}")
    print("----------------------------------------")

    kernel_path = get_kernel_path(energy)

    print("Kernel directory:")
    print(kernel_path)

    results = inspect_kernel(energy)

    all_passed = True

    for filename, exists in results.items():

        status = "PASS" if exists else "MISSING"

        print(f"{filename:25s} {status}")

        if not exists:
            all_passed = False

    if all_passed:
        print()
        print(f"PASS: {energy} kernel is complete.")

    else:
        print()
        print(f"FAIL: {energy} kernel is incomplete.")


print()
print("========================================")
print("Kernel inspection finished.")
print("========================================")