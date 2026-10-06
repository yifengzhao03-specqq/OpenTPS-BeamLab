from pathlib import Path

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

KERNEL_FOLDER = Path(
    r"C:\Users\Yifen\opentps\OpenTPS-BeamLab"
    r"\data\Kernels_18MV_test"
)

COMPONENT_FILES = [
    "primary.bin",
    "first_scatter.bin",
    "second_scatter.bin",
    "multiple_scatter.bin",
    "brem_annih.bin",
]


# ============================================================
# VALIDATOR
# ============================================================

def validate_kernel_folder(kernel_folder):

    kernel_folder = Path(kernel_folder)

    print()
    print(
        "OpenTPS BeamLab — Kernel Binary Validator"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # READ AXES
    # --------------------------------------------------------

    energies = np.fromfile(
        kernel_folder / "energies.bin",
        dtype=np.float32,
    )

    fluence = np.fromfile(
        kernel_folder / "fluence.bin",
        dtype=np.float32,
    )

    mu = np.fromfile(
        kernel_folder / "mu.bin",
        dtype=np.float32,
    )

    mu_en = np.fromfile(
        kernel_folder / "mu_en.bin",
        dtype=np.float32,
    )

    radii = np.fromfile(
        kernel_folder / "radii.bin",
        dtype=np.float32,
    )

    angles = np.fromfile(
        kernel_folder / "angles.bin",
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # BASIC DIMENSIONS
    # --------------------------------------------------------

    n_energy = len(energies)
    n_radii = len(radii)
    n_angles = len(angles)

    expected_shape = (
        n_energy,
        n_radii,
        n_angles,
    )

    expected_values = (
        n_energy
        * n_radii
        * n_angles
    )

    expected_bytes = (
        expected_values
        * np.dtype(np.float32).itemsize
    )

    print("DIMENSIONS")
    print("-" * 80)

    print(
        f"Energy bins : {n_energy}"
    )

    print(
        f"Radial bins : {n_radii}"
    )

    print(
        f"Angular bins: {n_angles}"
    )

    print(
        f"Kernel shape: {expected_shape}"
    )

    print(
        f"Values/component: {expected_values}"
    )

    print(
        f"Bytes/component: {expected_bytes}"
    )

    # --------------------------------------------------------
    # ENERGY-DEPENDENT ARRAY LENGTHS
    # --------------------------------------------------------

    print()
    print("ENERGY ARRAY ALIGNMENT")
    print("-" * 80)

    arrays = {
        "energies": energies,
        "fluence": fluence,
        "mu": mu,
        "mu_en": mu_en,
    }

    alignment_ok = True

    for name, array in arrays.items():

        status = (
            "PASS"
            if len(array) == n_energy
            else "FAIL"
        )

        if status == "FAIL":
            alignment_ok = False

        print(
            f"{name:<12}"
            f"count={len(array):<4} "
            f"expected={n_energy:<4} "
            f"{status}"
        )

    # --------------------------------------------------------
    # ENERGY GRID
    # --------------------------------------------------------

    expected_energies = np.array(
        [
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.8,
            1.0,
            1.25,
            1.5,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            8.0,
            10.0,
            12.0,
            15.0,
            18.0,
        ],
        dtype=np.float32,
    )

    energy_grid_ok = np.array_equal(
        energies,
        expected_energies,
    )

    print()
    print("ENERGY GRID")
    print("-" * 80)

    print(energies)

    print(
        "\nEnergy grid:",
        "PASS"
        if energy_grid_ok
        else "FAIL",
    )

    # --------------------------------------------------------
    # FLUENCE
    # --------------------------------------------------------

    fluence_sum = float(
        np.sum(
            fluence,
            dtype=np.float64,
        )
    )

    fluence_ok = np.isclose(
        fluence_sum,
        1.0,
        atol=1e-6,
    )

    print()
    print("FLUENCE")
    print("-" * 80)

    print(
        f"Fluence sum: {fluence_sum:.9f}"
    )

    print(
        "Fluence normalization:",
        "PASS"
        if fluence_ok
        else "FAIL",
    )

    # --------------------------------------------------------
    # READ COMPONENTS
    # --------------------------------------------------------

    print()
    print("COMPONENT FILES")
    print("-" * 80)

    components = []

    component_files_ok = True

    for filename in COMPONENT_FILES:

        file_path = (
            kernel_folder / filename
        )

        raw = np.fromfile(
            file_path,
            dtype=np.float32,
        )

        size_ok = (
            raw.size == expected_values
        )

        byte_ok = (
            file_path.stat().st_size
            == expected_bytes
        )

        status = (
            "PASS"
            if size_ok and byte_ok
            else "FAIL"
        )

        if status == "FAIL":
            component_files_ok = False

        print(
            f"{filename:<25}"
            f"values={raw.size:<8}"
            f"bytes={file_path.stat().st_size:<8}"
            f"{status}"
        )

        if size_ok:

            components.append(
                raw.reshape(
                    expected_shape,
                    order="C",
                )
            )

    # --------------------------------------------------------
    # TOTAL.BIN
    # --------------------------------------------------------

    total_file = (
        kernel_folder / "total.bin"
    )

    total_raw = np.fromfile(
        total_file,
        dtype=np.float32,
    )

    total_size_ok = (
        total_raw.size
        == expected_values
    )

    print()
    print("TOTAL FILE")
    print("-" * 80)

    print(
        f"total.bin values: "
        f"{total_raw.size}"
    )

    print(
        f"total.bin bytes : "
        f"{total_file.stat().st_size}"
    )

    print(
        "total.bin size:",
        "PASS"
        if total_size_ok
        else "FAIL",
    )

    # --------------------------------------------------------
    # TOTAL == SUM OF COMPONENTS
    # --------------------------------------------------------

    total_consistency_ok = False

    if (
        len(components)
        == 5
        and total_size_ok
    ):

        total = total_raw.reshape(
            expected_shape,
            order="C",
        )

        calculated_total = np.zeros(
            expected_shape,
            dtype=np.float32,
        )

        for component in components:

            calculated_total += component

        difference = (
            total
            - calculated_total
        )

        max_abs_difference = float(
            np.max(
                np.abs(difference)
            )
        )

        total_consistency_ok = np.allclose(
            total,
            calculated_total,
            rtol=1e-6,
            atol=1e-8,
        )

        print()
        print("TOTAL CONSISTENCY")
        print("-" * 80)

        print(
            "Max |total - component sum|: "
            f"{max_abs_difference:.12e}"
        )

        print(
            "total == sum(components):",
            "PASS"
            if total_consistency_ok
            else "FAIL",
        )

    # --------------------------------------------------------
    # FINITE / NON-NEGATIVE CHECK
    # --------------------------------------------------------

    numeric_ok = True

    print()
    print("NUMERIC CHECK")
    print("-" * 80)

    files_to_check = (
        COMPONENT_FILES
        + ["total.bin"]
    )

    for filename in files_to_check:

        array = np.fromfile(
            kernel_folder / filename,
            dtype=np.float32,
        )

        finite = np.all(
            np.isfinite(array)
        )

        non_negative = np.all(
            array >= 0
        )

        status = (
            "PASS"
            if finite and non_negative
            else "FAIL"
        )

        if status == "FAIL":
            numeric_ok = False

        print(
            f"{filename:<25}"
            f"finite={str(finite):<6}"
            f"nonnegative={str(non_negative):<6}"
            f"{status}"
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    final_ok = all(
        [
            alignment_ok,
            energy_grid_ok,
            fluence_ok,
            component_files_ok,
            total_size_ok,
            total_consistency_ok,
            numeric_ok,
            n_energy == 19,
            n_radii == 24,
            n_angles == 48,
        ]
    )

    print()
    print("=" * 80)

    if final_ok:

        print(
            "RESULT: 18 MV KERNEL BINARY VALIDATION PASSED"
        )

    else:

        print(
            "RESULT: 18 MV KERNEL BINARY VALIDATION FAILED"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    validate_kernel_folder(
        KERNEL_FOLDER
    )