import os
import numpy as np

from opentps.core.data.plan._photonPlan import PhotonPlan
from opentps.core.io.scannerReader import readScanner

from opentps.core.processing.doseCalculation.doseCalculationConfig import (
    DoseCalculationConfig,
)

from opentps.core.processing.doseCalculation.photons.cccDoseCalculator import (
    CCCDoseCalculator,
)


class EnergyCCCDoseCalculator(CCCDoseCalculator):
    """
    CCC dose calculator that allows selection of a custom
    OpenTPS photon kernel folder.
    """

    def __init__(self, kernel_folder, *args, **kwargs):
        self.kernel_folder = kernel_folder
        super().__init__(*args, **kwargs)

    def createKernelFilePath(self):

        kernels_dir = os.path.join(
            self.WorkSpaceDir,
            "opentps",
            "core",
            "processing",
            "doseCalculation",
            "photons",
            self.kernel_folder,
        )

        if not os.path.isdir(kernels_dir):
            raise RuntimeError(
                "Kernel directory not found:\n" + kernels_dir
            )

        header = os.path.join(
            kernels_dir,
            "kernel_header.txt",
        )

        if not os.path.isfile(header):
            raise RuntimeError(
                "kernel_header.txt not found:\n" + header
            )

        kernel_paths_file = os.path.join(
            self._CCCSimuDir,
            "kernelPaths.txt",
        )

        with open(kernel_paths_file, "w") as f:

            f.write("kernel_header\n")
            f.write(header + "\n")

            bin_files = sorted(
                filename
                for filename in os.listdir(kernels_dir)
                if filename.lower().endswith(".bin")
            )

            for filename in bin_files:

                kernel_name = os.path.splitext(filename)[0]

                f.write("kernel_" + kernel_name + "\n")
                f.write(
                    os.path.join(
                        kernels_dir,
                        filename,
                    )
                    + "\n"
                )

        print("Using kernel directory:")
        print(kernels_dir)

        return kernel_paths_file


KERNEL_FOLDERS = {
    "6MV": "Kernels_6MV",
    "18MV": "Kernels_18MV",
}


def calculate_dose(
    ct,
    beams,
    energy="6MV",
    prescription_cgy=200.0,
    normalize=True,
    batch_size=30,
):
    """
    Calculate a 3D photon dose distribution using OpenTPS CCC.

    Parameters
    ----------
    ct
        OpenTPS CTImage.

    beams
        List of PlanPhotonBeam objects.

    energy
        "6MV" or "18MV".

    prescription_cgy
        Dose used for isocenter normalization.

    normalize
        If True, normalize the center voxel to prescription_cgy.

    batch_size
        CCC calculation batch size.

    Returns
    -------
    numpy.ndarray
        3D dose array.
    """

    energy = str(energy).upper().replace(" ", "")

    if energy not in KERNEL_FOLDERS:
        raise ValueError(
            f"Unsupported energy: {energy}. "
            f"Available energies: {list(KERNEL_FOLDERS)}"
        )

    print()
    print("========================================")
    print("OpenTPS BeamLab - CCC Dose Calculation")
    print("========================================")
    print("Energy:", energy)
    print("Number of beams:", len(beams))

    plan = PhotonPlan(
        name=f"BeamLab_{energy}"
    )

    for beam in beams:
        plan.appendBeam(beam)

    calculator = EnergyCCCDoseCalculator(
        kernel_folder=KERNEL_FOLDERS[energy],
        batchSize=batch_size,
    )

    calculator.ctCalibration = readScanner(
        DoseCalculationConfig().scannerFolder
    )

    if calculator.ctCalibration is None:
        raise RuntimeError(
            "CT calibration could not be loaded."
        )

    print()
    print("Starting CCC calculation...")

    dose = calculator.computeDose(
        ct,
        plan,
    )

    raw = np.asarray(
        dose.imageArray,
        dtype=float,
    )

    print()
    print("Raw dose shape:")
    print(raw.shape)

    if not normalize:
        return raw

    cx = raw.shape[0] // 2
    cy = raw.shape[1] // 2
    cz = raw.shape[2] // 2

    raw_center = float(
        raw[cx, cy, cz]
    )

    print("Raw isocenter dose:")
    print(raw_center)

    if raw_center <= 0:
        raise RuntimeError(
            "Isocenter dose is zero or negative."
        )

    normalization_factor = (
        float(prescription_cgy) / raw_center
    )

    normalized = (
        raw * normalization_factor
    )

    print("Normalization factor:")
    print(normalization_factor)

    print("Normalized isocenter dose:")
    print(
        normalized[cx, cy, cz],
        "cGy",
    )

    print("Maximum dose:")
    print(
        np.max(normalized),
        "cGy",
    )

    return normalized