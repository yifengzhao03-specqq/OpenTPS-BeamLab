import numpy as np

from opentps.core.data.images._ctImage import CTImage


def create_water_phantom(
    size_mm=(400.0, 300.0, 400.0),
    voxel_mm=5.0
):
    """
    Create a homogeneous virtual water phantom for OpenTPS.

    Parameters
    ----------
    size_mm : tuple
        Phantom dimensions (X, Y, Z) in mm.

    voxel_mm : float
        Isotropic voxel size in mm.

    Returns
    -------
    CTImage
        OpenTPS CTImage object representing the water phantom.
    """

    size_x, size_y, size_z = size_mm

    nx = int(size_x / voxel_mm)
    ny = int(size_y / voxel_mm)
    nz = int(size_z / voxel_mm)

    ct = CTImage()

    ct.name = "Water_Phantom"

    ct.spacing = np.array(
        [voxel_mm, voxel_mm, voxel_mm],
        dtype=float
    )

    ct.imageArray = np.zeros(
        (nx, ny, nz),
        dtype=np.float32
    )

    ct.origin = np.array(
        [
            -size_x / 2.0,
            -size_y / 2.0,
            -size_z / 2.0
        ],
        dtype=float
    )

    return ct