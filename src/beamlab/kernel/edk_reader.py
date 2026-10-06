from pathlib import Path

import numpy as np


N_COMPONENTS = 5
N_RADII = 24
N_ANGLES = 48

EXPECTED_ROWS = N_COMPONENTS * N_RADII * N_ANGLES


def read_edk_file(file_path):
    """
    Read an EDKnrc .keV energy-deposition kernel file.

    Expected structure:
        5760 rows
        2 columns

    Column 0:
        Energy-deposition kernel value

    Column 1:
        Statistical uncertainty

    The data are reshaped into:

        (5, 24, 48)

    corresponding to:

        5 components
        24 radial bins
        48 angular bins
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"EDKnrc file not found:\n{file_path}"
        )

    data = np.loadtxt(file_path)

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    if data.ndim != 2:
        raise ValueError(
            f"Expected a 2D EDKnrc table, got shape {data.shape}"
        )

    if data.shape[1] != 2:
        raise ValueError(
            "EDKnrc file must contain exactly 2 columns.\n"
            f"Detected shape: {data.shape}"
        )

    if data.shape[0] != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} rows "
            f"({N_COMPONENTS} × {N_RADII} × {N_ANGLES}), "
            f"but found {data.shape[0]} rows."
        )

    # --------------------------------------------------------
    # Separate values and uncertainties
    # --------------------------------------------------------

    values = data[:, 0]
    uncertainties = data[:, 1]

   # --------------------------------------------------------
# Reshape EDKnrc interleaved component layout
#
# Each spatial bin contains 5 consecutive components:
# Primary, First Scatter, Second Scatter,
# Multiple Scatter, Brem + Annihilation.
#
# Raw layout:
#     (radius, angle, component)
#
# OpenTPS BeamLab layout:
#     (component, radius, angle)
# --------------------------------------------------------

    kernel = (
        values
        .reshape(
            N_RADII,
            N_ANGLES,
            N_COMPONENTS,
            order="C",
        )
        .transpose(2, 0, 1)
    )

    uncertainty = (
        uncertainties
        .reshape(
            N_RADII,
            N_ANGLES,
            N_COMPONENTS,
            order="C",
        )
        .transpose(2, 0, 1)
    )

    return kernel, uncertainty


def inspect_edk_file(file_path):
    """
    Read an EDKnrc file and return a small summary.
    """

    kernel, uncertainty = read_edk_file(file_path)

    summary = {
        "kernel_shape": kernel.shape,
        "uncertainty_shape": uncertainty.shape,
        "minimum": float(np.min(kernel)),
        "maximum": float(np.max(kernel)),
        "mean": float(np.mean(kernel)),
        "total": float(np.sum(kernel)),
        "mean_uncertainty": float(np.mean(uncertainty)),
        "max_uncertainty": float(np.max(uncertainty)),
    }

    return summary


if __name__ == "__main__":

    print("OpenTPS BeamLab — EDKnrc Reader")
    print()
    print(f"Expected rows: {EXPECTED_ROWS}")
    print(
        "Expected kernel shape:",
        (N_COMPONENTS, N_RADII, N_ANGLES),
    )