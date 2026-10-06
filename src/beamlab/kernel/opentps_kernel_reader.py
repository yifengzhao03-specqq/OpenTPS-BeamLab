from pathlib import Path

import numpy as np


# ============================================================
# OPENTPS KERNEL READER
# ============================================================

COMPONENT_FILES = {
    "primary": "primary.bin",
    "first_scatter": "first_scatter.bin",
    "second_scatter": "second_scatter.bin",
    "multiple_scatter": "multiple_scatter.bin",
    "brem_annih": "brem_annih.bin",
    "total": "total.bin",
}


def read_float32_file(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found:\n{file_path}"
        )

    return np.fromfile(
        file_path,
        dtype=np.float32,
    )


def inspect_opentps_kernel_folder(
    kernel_folder,
):

    kernel_folder = Path(
        kernel_folder
    )

    print()
    print(
        "OpenTPS BeamLab — OpenTPS Kernel Inspector"
    )

    print("=" * 80)

    print(
        f"Folder: {kernel_folder}"
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header_file = (
        kernel_folder
        / "kernel_header.txt"
    )

    print()
    print("HEADER")
    print("-" * 80)

    if header_file.exists():

        header_text = (
            header_file
            .read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

        print(header_text)

    else:

        print(
            "kernel_header.txt not found"
        )

    # --------------------------------------------------------
    # AXES / ENERGY DATA
    # --------------------------------------------------------

    data_files = [
        "energies.bin",
        "fluence.bin",
        "mu.bin",
        "mu_en.bin",
        "radii.bin",
        "angles.bin",
    ]

    arrays = {}

    print()
    print("BINARY ARRAYS")
    print("-" * 80)

    for filename in data_files:

        file_path = (
            kernel_folder
            / filename
        )

        array = read_float32_file(
            file_path
        )

        arrays[filename] = array

        print(
            f"{filename:<20}"
            f"count={array.size:<6}"
            f"dtype={array.dtype}   "
            f"bytes={array.nbytes}"
        )

    # --------------------------------------------------------
    # PRINT VALUES
    # --------------------------------------------------------

    print()
    print("ENERGIES")
    print("-" * 80)

    print(
        arrays["energies.bin"]
    )

    print()
    print("FLUENCE")
    print("-" * 80)

    print(
        arrays["fluence.bin"]
    )

    print()
    print("MU")
    print("-" * 80)

    print(
        arrays["mu.bin"]
    )

    print()
    print("MU_EN")
    print("-" * 80)

    print(
        arrays["mu_en.bin"]
    )

    print()
    print("RADII")
    print("-" * 80)

    print(
        arrays["radii.bin"]
    )

    print()
    print("ANGLES")
    print("-" * 80)

    print(
        arrays["angles.bin"]
    )

    # --------------------------------------------------------
    # DETERMINE DIMENSIONS
    # --------------------------------------------------------

    n_energy = (
        arrays["energies.bin"].size
    )

    n_radii = (
        arrays["radii.bin"].size
    )

    n_angles = (
        arrays["angles.bin"].size
    )

    expected_kernel_values = (
        n_energy
        * n_radii
        * n_angles
    )

    print()
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
        "Expected component shape: "
        f"({n_energy}, "
        f"{n_radii}, "
        f"{n_angles})"
    )

    print(
        "Expected values per component: "
        f"{expected_kernel_values}"
    )

    # --------------------------------------------------------
    # COMPONENT FILES
    # --------------------------------------------------------

    print()
    print("KERNEL COMPONENTS")
    print("-" * 80)

    components = {}

    for name, filename in (
        COMPONENT_FILES.items()
    ):

        file_path = (
            kernel_folder
            / filename
        )

        raw = read_float32_file(
            file_path
        )

        status = (
            "PASS"
            if raw.size
            == expected_kernel_values
            else "FAIL"
        )

        print(
            f"{filename:<25}"
            f"count={raw.size:<8}"
            f"expected={expected_kernel_values:<8}"
            f"{status}"
        )

        if (
            raw.size
            == expected_kernel_values
        ):

            components[name] = (
                raw.reshape(
                    n_energy,
                    n_radii,
                    n_angles,
                    order="C",
                )
            )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    all_valid = all(
        component.shape
        == (
            n_energy,
            n_radii,
            n_angles,
        )
        for component
        in components.values()
    )

    print()
    print("=" * 80)

    if (
        all_valid
        and len(components)
        == len(COMPONENT_FILES)
    ):

        print(
            "RESULT: OPENTPS KERNEL STRUCTURE VALIDATED"
        )

    else:

        print(
            "RESULT: OPENTPS KERNEL STRUCTURE VALIDATION FAILED"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    kernel_folder = Path(
        r"C:\Users\Yifen\opentps"
        r"\OpenTPS_venv\Lib\site-packages"
        r"\opentps\core\processing\doseCalculation"
        r"\photons\Kernels_6MV"
    )

    inspect_opentps_kernel_folder(
        kernel_folder
    )