from dataclasses import dataclass
from pathlib import Path

import numpy as np

from beamlab.kernel.edk_reader import read_edk_file


# ============================================================
# HIGH-ENERGY PHOTON DATA
# ============================================================

HIGH_ENERGY_DATA = {
    8.0: {
        "mu_rho": 0.02423000,
        "fpri": 0.68437900,
        "mu_en_rho": 0.01658250,
    },
    10.0: {
        "mu_rho": 0.02213500,
        "fpri": 0.70620500,
        "mu_en_rho": 0.01563185,
    },
    12.0: {
        "mu_rho": 0.02073200,
        "fpri": 0.72371100,
        "mu_en_rho": 0.01500398,
    },
    15.0: {
        "mu_rho": 0.01936100,
        "fpri": 0.74201100,
        "mu_en_rho": 0.01436607,
    },
    18.0: {
        "mu_rho": 0.01849500,
        "fpri": 0.75821300,
        "mu_en_rho": 0.01402315,
    },
}


# ============================================================
# ENERGY KERNEL OBJECT
# ============================================================

@dataclass
class EnergyKernel:
    """
    Container for one monoenergetic EDKnrc kernel.
    """

    energy_mev: float

    kernel: np.ndarray
    uncertainty: np.ndarray

    mu_rho: float
    fpri: float
    mu_en_rho: float

    source_file: Path

    @property
    def shape(self):
        return self.kernel.shape

    @property
    def total(self):
        return float(
            np.sum(self.kernel)
        )

    @property
    def component_totals(self):
        return np.sum(
            self.kernel,
            axis=(1, 2),
        )

    @property
    def component_percentages(self):

        totals = self.component_totals

        total = float(
            np.sum(totals)
        )

        if total == 0:
            raise ValueError(
                "Kernel total is zero."
            )

        return (
            totals / total
        ) * 100.0


# ============================================================
# BUILD ONE ENERGY KERNEL
# ============================================================

def build_energy_kernel(
    energy_mev,
    edk_file,
):
    """
    Read and validate one EDKnrc kernel and associate
    the corresponding photon interaction data.
    """

    energy_mev = float(
        energy_mev
    )

    edk_file = Path(
        edk_file
    )

    # --------------------------------------------------------
    # CHECK ENERGY
    # --------------------------------------------------------

    if energy_mev not in HIGH_ENERGY_DATA:

        available = ", ".join(
            f"{energy:g}"
            for energy in sorted(
                HIGH_ENERGY_DATA.keys()
            )
        )

        raise ValueError(
            f"No photon interaction data are defined "
            f"for {energy_mev:g} MeV.\n"
            f"Available energies: {available} MeV"
        )

    # --------------------------------------------------------
    # READ EDK
    # --------------------------------------------------------

    kernel, uncertainty = read_edk_file(
        edk_file
    )

    # --------------------------------------------------------
    # VALIDATE SHAPE
    # --------------------------------------------------------

    expected_shape = (
        5,
        24,
        48,
    )

    if kernel.shape != expected_shape:

        raise ValueError(
            f"{energy_mev:g} MeV kernel has "
            f"unexpected shape: {kernel.shape}\n"
            f"Expected: {expected_shape}"
        )

    if uncertainty.shape != expected_shape:

        raise ValueError(
            f"{energy_mev:g} MeV uncertainty array has "
            f"unexpected shape: {uncertainty.shape}\n"
            f"Expected: {expected_shape}"
        )

    # --------------------------------------------------------
    # VALIDATE NUMBERS
    # --------------------------------------------------------

    if not np.all(
        np.isfinite(kernel)
    ):
        raise ValueError(
            f"{energy_mev:g} MeV kernel contains "
            "NaN or infinite values."
        )

    if not np.all(
        np.isfinite(uncertainty)
    ):
        raise ValueError(
            f"{energy_mev:g} MeV uncertainty array "
            "contains NaN or infinite values."
        )

    if np.any(
        kernel < 0
    ):
        raise ValueError(
            f"{energy_mev:g} MeV kernel contains "
            "negative energy-deposition values."
        )

    kernel_total = float(
        np.sum(kernel)
    )

    if kernel_total <= 0:
        raise ValueError(
            f"{energy_mev:g} MeV kernel total "
            "must be greater than zero."
        )

    # --------------------------------------------------------
    # PHOTON DATA
    # --------------------------------------------------------

    photon_data = (
        HIGH_ENERGY_DATA[
            energy_mev
        ]
    )

    # --------------------------------------------------------
    # BUILD OBJECT
    # --------------------------------------------------------

    energy_kernel = EnergyKernel(
        energy_mev=energy_mev,
        kernel=kernel,
        uncertainty=uncertainty,
        mu_rho=photon_data["mu_rho"],
        fpri=photon_data["fpri"],
        mu_en_rho=photon_data["mu_en_rho"],
        source_file=edk_file,
    )

    return energy_kernel


# ============================================================
# PRINT ONE ENERGY REPORT
# ============================================================

def print_energy_kernel_report(
    energy_kernel,
):

    print()

    print(
        "OpenTPS BeamLab — Energy Kernel Builder"
    )

    print(
        "=" * 70
    )

    print(
        f"Energy:       "
        f"{energy_kernel.energy_mev:g} MeV"
    )

    print(
        f"Source:       "
        f"{energy_kernel.source_file}"
    )

    print(
        f"Shape:        "
        f"{energy_kernel.shape}"
    )

    print(
        f"Kernel total: "
        f"{energy_kernel.total:.9f}"
    )

    print()

    print(
        f"mu/rho:       "
        f"{energy_kernel.mu_rho:.8f}"
    )

    print(
        f"Fpri:         "
        f"{energy_kernel.fpri:.8f}"
    )

    print(
        f"mu_en/rho:    "
        f"{energy_kernel.mu_en_rho:.8f}"
    )

    print()

    print(
        "Component percentages:"
    )

    for index, percent in enumerate(
        energy_kernel.component_percentages
    ):

        print(
            f"  Component {index}: "
            f"{percent:.3f}%"
        )

    print()

    print(
        "RESULT: ENERGY KERNEL VALIDATED"
    )


# ============================================================
# BUILD HIGH-ENERGY KERNEL SET
# ============================================================

def build_high_energy_kernel_set(
    edk_folder,
):
    """
    Build the complete BeamLab high-energy kernel set:

        8 MeV
        10 MeV
        12 MeV
        15 MeV
        18 MeV
    """

    edk_folder = Path(
        edk_folder
    )

    if not edk_folder.exists():

        raise FileNotFoundError(
            f"EDKnrc folder not found:\n"
            f"{edk_folder}"
        )

    energies = sorted(
        HIGH_ENERGY_DATA.keys()
    )

    kernel_set = {}

    for energy in energies:

        energy_label = (
            f"{energy:g}"
        )

        edk_file = (
            edk_folder
            / f"{energy_label}MeV_MVgrid.keV"
        )

        if not edk_file.exists():

            raise FileNotFoundError(
                f"Missing EDKnrc file for "
                f"{energy:g} MeV:\n"
                f"{edk_file}"
            )

        energy_kernel = (
            build_energy_kernel(
                energy_mev=energy,
                edk_file=edk_file,
            )
        )

        kernel_set[
            energy
        ] = energy_kernel

    return kernel_set


# ============================================================
# VALIDATE HIGH-ENERGY KERNEL SET
# ============================================================

def validate_high_energy_kernel_set(
    kernel_set,
):
    """
    Validate the complete high-energy kernel set.
    """

    expected_energies = sorted(
        HIGH_ENERGY_DATA.keys()
    )

    actual_energies = sorted(
        kernel_set.keys()
    )

    if actual_energies != expected_energies:

        raise ValueError(
            "Kernel-set energy grid does not "
            "match the expected high-energy grid.\n"
            f"Expected: {expected_energies}\n"
            f"Found:    {actual_energies}"
        )

    expected_shape = (
        5,
        24,
        48,
    )

    for energy in expected_energies:

        item = (
            kernel_set[
                energy
            ]
        )

        if item.shape != expected_shape:

            raise ValueError(
                f"{energy:g} MeV has invalid shape: "
                f"{item.shape}"
            )

        if item.total <= 0:

            raise ValueError(
                f"{energy:g} MeV kernel "
                "has a non-positive total."
            )

        if not np.all(
            np.isfinite(
                item.kernel
            )
        ):

            raise ValueError(
                f"{energy:g} MeV kernel "
                "contains invalid numbers."
            )

        percent_sum = float(
            np.sum(
                item.component_percentages
            )
        )

        if not np.isclose(
            percent_sum,
            100.0,
            atol=0.001,
        ):

            raise ValueError(
                f"{energy:g} MeV component "
                f"percentage sum is "
                f"{percent_sum:.6f}%."
            )

    return True


# ============================================================
# PRINT HIGH-ENERGY KERNEL-SET REPORT
# ============================================================

def print_kernel_set_report(
    kernel_set,
):

    print()

    print(
        "OpenTPS BeamLab — High-Energy Kernel Set"
    )

    print(
        "=" * 100
    )

    print(
        f"{'Energy':>10}"
        f"{'Shape':>18}"
        f"{'Total':>16}"
        f"{'mu/rho':>14}"
        f"{'Fpri':>14}"
        f"{'mu_en/rho':>14}"
    )

    print(
        "-" * 100
    )

    for energy in sorted(
        kernel_set.keys()
    ):

        item = (
            kernel_set[
                energy
            ]
        )

        print(
            f"{energy:>7g} MeV"
            f"{str(item.shape):>18}"
            f"{item.total:>16.9f}"
            f"{item.mu_rho:>14.8f}"
            f"{item.fpri:>14.8f}"
            f"{item.mu_en_rho:>14.8f}"
        )

    print(
        "-" * 100
    )

    print()
    print(
        "Component percentages"
    )

    print(
        "=" * 100
    )

    print(
        f"{'Energy':>10}"
        f"{'Primary':>14}"
        f"{'First':>14}"
        f"{'Second':>14}"
        f"{'Multiple':>14}"
        f"{'Brem+Ann':>14}"
    )

    print(
        "-" * 100
    )

    for energy in sorted(
        kernel_set.keys()
    ):

        item = (
            kernel_set[
                energy
            ]
        )

        percentages = (
            item.component_percentages
        )

        print(
            f"{energy:>7g} MeV"
            f"{percentages[0]:>13.3f}%"
            f"{percentages[1]:>13.3f}%"
            f"{percentages[2]:>13.3f}%"
            f"{percentages[3]:>13.3f}%"
            f"{percentages[4]:>13.3f}%"
        )

    print(
        "-" * 100
    )

    print()
    print(
        "Validation"
    )

    print(
        "=" * 100
    )

    validate_high_energy_kernel_set(
        kernel_set
    )

    for energy in sorted(
        kernel_set.keys()
    ):

        item = (
            kernel_set[
                energy
            ]
        )

        percentage_sum = float(
            np.sum(
                item.component_percentages
            )
        )

        print(
            f"{energy:>2g} MeV : "
            f"shape={item.shape}   "
            f"total={item.total:.9f}   "
            f"sum={percentage_sum:.3f}%   "
            f"PASS"
        )

    print()

    print(
        "RESULT: HIGH-ENERGY KERNEL SET VALIDATED"
    )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    edk_folder = Path(
        r"C:\EGSnrc\egs_home\edknrc"
    )

    kernel_set = (
        build_high_energy_kernel_set(
            edk_folder
        )
    )

    print_kernel_set_report(
        kernel_set
    )