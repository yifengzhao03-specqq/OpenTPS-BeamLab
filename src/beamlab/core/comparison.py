import numpy as np


def extract_center_profiles(
    dose,
    voxel_mm=5.0,
):
    """
    Extract three orthogonal dose profiles through isocenter.

    Returns:
        {
            "x": {
                "position_mm": ...,
                "dose": ...
            },
            "y": {
                "position_mm": ...,
                "dose": ...
            },
            "z": {
                "position_mm": ...,
                "dose": ...
            }
        }
    """

    dose = np.asarray(
        dose,
        dtype=float,
    )

    if dose.ndim != 3:
        raise ValueError(
            "Dose must be a 3D array."
        )

    nx, ny, nz = dose.shape

    cx = nx // 2
    cy = ny // 2
    cz = nz // 2

    # X profile
    x_position = (
        np.arange(nx) - cx
    ) * voxel_mm

    x_dose = dose[
        :,
        cy,
        cz,
    ]

    # Y profile
    y_position = (
        np.arange(ny) - cy
    ) * voxel_mm

    y_dose = dose[
        cx,
        :,
        cz,
    ]

    # Z profile
    z_position = (
        np.arange(nz) - cz
    ) * voxel_mm

    z_dose = dose[
        cx,
        cy,
        :,
    ]

    return {
        "x": {
            "position_mm": x_position,
            "dose": x_dose,
        },
        "y": {
            "position_mm": y_position,
            "dose": y_dose,
        },
        "z": {
            "position_mm": z_position,
            "dose": z_dose,
        },
    }


def compare_doses(
    dose_a,
    dose_b,
    voxel_mm=5.0,
):
    """
    Compare two 3D dose distributions.
    """

    dose_a = np.asarray(
        dose_a,
        dtype=float,
    )

    dose_b = np.asarray(
        dose_b,
        dtype=float,
    )

    if dose_a.shape != dose_b.shape:
        raise ValueError(
            "Dose matrices must have the same shape."
        )

    difference = (
        dose_b - dose_a
    )

    profiles_a = extract_center_profiles(
        dose_a,
        voxel_mm,
    )

    profiles_b = extract_center_profiles(
        dose_b,
        voxel_mm,
    )

    return {
        "dose_a": dose_a,
        "dose_b": dose_b,
        "difference": difference,
        "profiles_a": profiles_a,
        "profiles_b": profiles_b,
        "max_a": float(
            np.max(dose_a)
        ),
        "max_b": float(
            np.max(dose_b)
        ),
        "mean_difference": float(
            np.mean(difference)
        ),
        "max_absolute_difference": float(
            np.max(
                np.abs(difference)
            )
        ),
    }