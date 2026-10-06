from pathlib import Path

import numpy as np

from beamlab.kernel.edk_reader import read_edk_file


# ============================================================
# CONFIGURATION
# ============================================================

BASE_KERNEL_FOLDER = Path(
    r"C:\Users\Yifen\opentps\OpenTPS_venv"
    r"\Lib\site-packages\opentps\core\processing"
    r"\doseCalculation\photons\Kernels_6MV"
)

EDK_FOLDER = Path(
    r"C:\EGSnrc\egs_home\edknrc"
)

OUTPUT_FOLDER = Path(
    r"C:\Users\Yifen\opentps\OpenTPS-BeamLab"
    r"\data\Kernels_18MV_test"
)


# ============================================================
# ENERGY GRID
# ============================================================

HIGH_ENERGIES = np.array(
    [
        8.0,
        10.0,
        12.0,
        15.0,
        18.0,
    ],
    dtype=np.float32,
)


# ============================================================
# 18 MV COMPUTATIONAL SPECTRUM
# ============================================================

FULL_FLUENCE = np.array(
    [
        0.005061804,
        0.019645069,
        0.022204363,
        0.022985391,
        0.034956073,
        0.046124592,
        0.049933231,
        0.052225105,
        0.071419532,
        0.119779773,
        0.121855295,
        0.091166302,
        0.069883729,
        0.077745516,
        0.071249941,
        0.048508583,
        0.040849085,
        0.028464029,
        0.005942586,
    ],
    dtype=np.float32,
)


# ============================================================
# HIGH-ENERGY ATTENUATION DATA
# ============================================================

HIGH_MU = np.array(
    [
        0.02423000,
        0.02213500,
        0.02073200,
        0.01936100,
        0.01849500,
    ],
    dtype=np.float32,
)

HIGH_MU_EN = np.array(
    [
        0.01658250,
        0.01563185,
        0.01500398,
        0.01436607,
        0.01402315,
    ],
    dtype=np.float32,
)


# ============================================================
# COMPONENT MAPPING
# ============================================================

COMPONENT_FILES = {
    0: "primary.bin",
    1: "first_scatter.bin",
    2: "second_scatter.bin",
    3: "multiple_scatter.bin",
    4: "brem_annih.bin",
}


# ============================================================
# READ BASE KERNEL
# ============================================================

def read_base_kernel():

    energies = np.fromfile(
        BASE_KERNEL_FOLDER / "energies.bin",
        dtype=np.float32,
    )

    mu = np.fromfile(
        BASE_KERNEL_FOLDER / "mu.bin",
        dtype=np.float32,
    )

    mu_en = np.fromfile(
        BASE_KERNEL_FOLDER / "mu_en.bin",
        dtype=np.float32,
    )

    radii = np.fromfile(
        BASE_KERNEL_FOLDER / "radii.bin",
        dtype=np.float32,
    )

    angles = np.fromfile(
        BASE_KERNEL_FOLDER / "angles.bin",
        dtype=np.float32,
    )

    components = {}

    shape = (
        len(energies),
        len(radii),
        len(angles),
    )

    for component_index, filename in COMPONENT_FILES.items():

        data = np.fromfile(
            BASE_KERNEL_FOLDER / filename,
            dtype=np.float32,
        )

        components[component_index] = data.reshape(
            shape,
            order="C",
        )

    return (
        energies,
        mu,
        mu_en,
        radii,
        angles,
        components,
    )


# ============================================================
# READ HIGH-ENERGY EDK
# ============================================================

def read_high_energy_kernels():

    kernels = {}

    for energy in HIGH_ENERGIES:

        energy_value = int(
            energy
        )

        file_path = (
            EDK_FOLDER
            / f"{energy_value}MeV_MVgrid.keV"
        )

        kernel, uncertainty = read_edk_file(
            file_path
        )

        if kernel.shape != (
            5,
            24,
            48,
        ):
            raise ValueError(
                f"Invalid EDK shape for "
                f"{energy_value} MeV: "
                f"{kernel.shape}"
            )

        kernels[
            float(energy)
        ] = kernel.astype(
            np.float32
        )

    return kernels


# ============================================================
# BUILD FULL 19-ENERGY COMPONENTS
# ============================================================

def build_components(
    base_components,
    high_energy_kernels,
):

    output_components = {}

    for component_index in range(5):

        low_energy = (
            base_components[
                component_index
            ]
        )

        high_energy = np.stack(
            [
                high_energy_kernels[
                    float(energy)
                ][component_index]
                for energy in HIGH_ENERGIES
            ],
            axis=0,
        )

        combined = np.concatenate(
            [
                low_energy,
                high_energy,
            ],
            axis=0,
        )

        if combined.shape != (
            19,
            24,
            48,
        ):
            raise ValueError(
                "Unexpected combined "
                f"component shape: {combined.shape}"
            )

        output_components[
            component_index
        ] = combined.astype(
            np.float32
        )

    return output_components


# ============================================================
# BUILD TOTAL KERNEL
# ============================================================

def build_total_kernel(
    components,
):

    total = np.zeros_like(
        components[0],
        dtype=np.float32,
    )

    for component_index in range(5):

        total += (
            components[
                component_index
            ]
        )

    return total


# ============================================================
# WRITE OPENTPS KERNEL FOLDER
# ============================================================

def build_opentps_18mv_kernel():

    print()
    print(
        "OpenTPS BeamLab — OpenTPS 18 MV Kernel Builder"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # READ BASE
    # --------------------------------------------------------

    print(
        "Reading OpenTPS 6 MV base kernel..."
    )

    (
        base_energies,
        base_mu,
        base_mu_en,
        radii,
        angles,
        base_components,
    ) = read_base_kernel()

    # --------------------------------------------------------
    # READ HIGH ENERGY
    # --------------------------------------------------------

    print(
        "Reading EDKnrc high-energy kernels..."
    )

    high_energy_kernels = (
        read_high_energy_kernels()
    )

    # --------------------------------------------------------
    # ENERGY GRID
    # --------------------------------------------------------

    energies = np.concatenate(
        [
            base_energies,
            HIGH_ENERGIES,
        ]
    ).astype(
        np.float32
    )

    if energies.shape != (19,):
        raise ValueError(
            f"Unexpected energy grid: "
            f"{energies.shape}"
        )

    # --------------------------------------------------------
    # MU
    # --------------------------------------------------------

    mu = np.concatenate(
        [
            base_mu,
            HIGH_MU,
        ]
    ).astype(
        np.float32
    )

    # --------------------------------------------------------
    # MU_EN
    # --------------------------------------------------------

    mu_en = np.concatenate(
        [
            base_mu_en,
            HIGH_MU_EN,
        ]
    ).astype(
        np.float32
    )

    # --------------------------------------------------------
    # COMPONENTS
    # --------------------------------------------------------

    print(
        "Building 19-energy component arrays..."
    )

    components = build_components(
        base_components,
        high_energy_kernels,
    )

    total = build_total_kernel(
        components
    )

    # --------------------------------------------------------
    # OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # WRITE AXES / PHOTON DATA
    # --------------------------------------------------------

    energies.tofile(
        OUTPUT_FOLDER / "energies.bin"
    )

    FULL_FLUENCE.tofile(
        OUTPUT_FOLDER / "fluence.bin"
    )

    mu.tofile(
        OUTPUT_FOLDER / "mu.bin"
    )

    mu_en.tofile(
        OUTPUT_FOLDER / "mu_en.bin"
    )

    radii.astype(
        np.float32
    ).tofile(
        OUTPUT_FOLDER / "radii.bin"
    )

    angles.astype(
        np.float32
    ).tofile(
        OUTPUT_FOLDER / "angles.bin"
    )

    # --------------------------------------------------------
    # WRITE COMPONENTS
    # --------------------------------------------------------

    for component_index, filename in COMPONENT_FILES.items():

        components[
            component_index
        ].tofile(
            OUTPUT_FOLDER / filename
        )

    total.tofile(
        OUTPUT_FOLDER / "total.bin"
    )

    # --------------------------------------------------------
    # WRITE HEADER
    # --------------------------------------------------------

    header_path = (
        OUTPUT_FOLDER
        / "kernel_header.txt"
    )

    with open(
        header_path,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Nradii Nangles Nenergies\n"
        )

        file.write(
            f"{len(radii)} "
            f"{len(angles)} "
            f"{len(energies)}\n"
        )
    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()
    print(
        f"Output folder:\n{OUTPUT_FOLDER}"
    )

    print()
    print(
        "Energy grid:"
    )

    print(
        energies
    )

    print()
    print(
        f"Fluence sum: "
        f"{float(np.sum(FULL_FLUENCE)):.9f}"
    )

    print(
        f"Component shape: "
        f"{components[0].shape}"
    )

    print(
        f"Total shape: "
        f"{total.shape}"
    )

    print()

    print(
        "RESULT: TEST 18 MV KERNEL FOLDER CREATED"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_opentps_18mv_kernel()