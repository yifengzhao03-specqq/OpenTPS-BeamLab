from pathlib import Path

import numpy as np

from beamlab.kernel.edk_reader import read_edk_file


# ============================================================
# PATHS
# ============================================================

BASE_FOLDER = Path(
    r"C:\Users\Yifen\opentps\OpenTPS_venv"
    r"\Lib\site-packages\opentps\core\processing"
    r"\doseCalculation\photons\Kernels_6MV"
)

TEST_FOLDER = Path(
    r"C:\Users\Yifen\opentps\OpenTPS-BeamLab"
    r"\data\Kernels_18MV_test"
)

EDK_FOLDER = Path(
    r"C:\EGSnrc\egs_home\edknrc"
)


# ============================================================
# COMPONENTS
# ============================================================

COMPONENT_FILES = [
    "primary.bin",
    "first_scatter.bin",
    "second_scatter.bin",
    "multiple_scatter.bin",
    "brem_annih.bin",
]


HIGH_ENERGIES = [
    8,
    10,
    12,
    15,
    18,
]


# ============================================================
# MAIN VALIDATION
# ============================================================

def validate_sources():

    print()
    print(
        "OpenTPS BeamLab — Kernel Source Validator"
    )

    print("=" * 90)

    # --------------------------------------------------------
    # PART 1
    # LOW-ENERGY SLICES
    # --------------------------------------------------------

    print()
    print(
        "PART 1 — Original OpenTPS 0.2–6 MeV slices"
    )

    print("-" * 90)

    low_energy_ok = True

    for filename in COMPONENT_FILES:

        original = np.fromfile(
            BASE_FOLDER / filename,
            dtype=np.float32,
        ).reshape(
            14,
            24,
            48,
        )

        generated = np.fromfile(
            TEST_FOLDER / filename,
            dtype=np.float32,
        ).reshape(
            19,
            24,
            48,
        )

        difference = (
            generated[:14]
            - original
        )

        max_difference = float(
            np.max(
                np.abs(difference)
            )
        )

        exact = np.array_equal(
            generated[:14],
            original,
        )

        if not exact:
            low_energy_ok = False

        print(
            f"{filename:<25}"
            f"max_diff={max_difference:.12e}   "
            f"{'PASS' if exact else 'FAIL'}"
        )

    # --------------------------------------------------------
    # PART 2
    # HIGH-ENERGY SLICES
    # --------------------------------------------------------

    print()
    print(
        "PART 2 — EDKnrc 8–18 MeV slices"
    )

    print("-" * 90)

    high_energy_ok = True

    generated_components = {}

    for component_index, filename in enumerate(
        COMPONENT_FILES
    ):

        generated_components[
            component_index
        ] = np.fromfile(
            TEST_FOLDER / filename,
            dtype=np.float32,
        ).reshape(
            19,
            24,
            48,
        )

    for high_index, energy in enumerate(
        HIGH_ENERGIES
    ):

        edk_file = (
            EDK_FOLDER
            / f"{energy}MeV_MVgrid.keV"
        )

        edk_kernel, _ = read_edk_file(
            edk_file
        )

        print()
        print(
            f"{energy} MeV"
        )

        generated_index = (
            14 + high_index
        )

        for component_index, filename in enumerate(
            COMPONENT_FILES
        ):

            expected = (
                edk_kernel[
                    component_index
                ].astype(
                    np.float32
                )
            )

            generated = (
                generated_components[
                    component_index
                ][generated_index]
            )

            difference = (
                generated
                - expected
            )

            max_difference = float(
                np.max(
                    np.abs(difference)
                )
            )

            exact = np.array_equal(
                generated,
                expected,
            )

            if not exact:
                high_energy_ok = False

            print(
                f"  {filename:<23}"
                f"max_diff="
                f"{max_difference:.12e}   "
                f"{'PASS' if exact else 'FAIL'}"
            )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 90)

    print(
        "Low-energy source preservation:",
        "PASS"
        if low_energy_ok
        else "FAIL",
    )

    print(
        "High-energy EDK integration:",
        "PASS"
        if high_energy_ok
        else "FAIL",
    )

    print()

    if (
        low_energy_ok
        and high_energy_ok
    ):

        print(
            "RESULT: ALL KERNEL SLICES MATCH "
            "THEIR SOURCE DATA EXACTLY"
        )

    else:

        print(
            "RESULT: KERNEL SOURCE "
            "VALIDATION FAILED"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    validate_sources()