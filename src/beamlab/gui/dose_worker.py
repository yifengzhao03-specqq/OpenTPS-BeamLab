from PySide6.QtCore import QObject, Signal, Slot

from beamlab.core.phantom import create_water_phantom
from beamlab.core.beam import (
    create_parallel_opposed,
    create_four_field_box,
)
from beamlab.core.dose_engine import calculate_dose


class DoseCalculationWorker(QObject):

    finished = Signal(object)
    comparison_finished = Signal(object, object)

    error = Signal(str)
    status = Signal(str)


    def __init__(
        self,
        energy,
        geometry,
        field_size_mm,
        prescription_cgy,
        weights,
        comparison_mode=False,
    ):
        super().__init__()

        self.energy = energy
        self.geometry = geometry
        self.field_size_mm = field_size_mm
        self.prescription_cgy = prescription_cgy
        self.weights = weights
        self.comparison_mode = comparison_mode


    # ========================================================
    # CREATE PHANTOM
    # ========================================================

    def create_phantom(self):

        self.status.emit(
            "Creating water phantom..."
        )

        phantom = create_water_phantom(
            size_mm=(
                400.0,
                300.0,
                400.0,
            ),
            voxel_mm=5.0,
        )

        return phantom


    # ========================================================
    # CREATE BEAMS
    # ========================================================

    def create_beams(self):

        self.status.emit(
            "Creating beam geometry..."
        )

        if self.geometry == "AP/PA":

            if len(self.weights) != 2:
                raise ValueError(
                    "AP/PA requires exactly 2 beam weights."
                )

            beams = create_parallel_opposed(
                field_size_mm=self.field_size_mm,
                weights=self.weights,
                isocenter=(
                    0.0,
                    0.0,
                    0.0,
                ),
            )

        elif self.geometry == "Four-Field Box":

            if len(self.weights) != 4:
                raise ValueError(
                    "Four-Field Box requires exactly 4 beam weights."
                )

            beams = create_four_field_box(
                field_size_mm=self.field_size_mm,
                weights=self.weights,
                isocenter=(
                    0.0,
                    0.0,
                    0.0,
                ),
            )

        else:

            raise ValueError(
                f"Unsupported geometry: {self.geometry}"
            )

        return beams


    # ========================================================
    # SINGLE ENERGY
    # ========================================================

    def calculate_single(
        self,
        phantom,
        beams,
    ):

        self.status.emit(
            f"Running {self.energy} CCC calculation..."
        )

        dose = calculate_dose(
            ct=phantom,
            beams=beams,
            energy=self.energy,
            prescription_cgy=self.prescription_cgy,
        )

        return dose


    # ========================================================
    # COMPARISON
    # ========================================================

    def calculate_comparison(
        self,
        phantom,
    ):

        # ----------------------------------------------------
        # 6 MV
        # ----------------------------------------------------

        self.status.emit(
            "Comparison 1/2: Running 6 MV CCC..."
        )

        beams_6mv = self.create_beams()

        dose_6mv = calculate_dose(
            ct=phantom,
            beams=beams_6mv,
            energy="6MV",
            prescription_cgy=self.prescription_cgy,
        )

        # ----------------------------------------------------
        # 18 MV
        # ----------------------------------------------------

        self.status.emit(
            "Comparison 2/2: Running 18 MV CCC..."
        )

        # Create a fresh beam set for the second calculation.
        beams_18mv = self.create_beams()

        dose_18mv = calculate_dose(
            ct=phantom,
            beams=beams_18mv,
            energy="18MV",
            prescription_cgy=self.prescription_cgy,
        )

        return (
            dose_6mv,
            dose_18mv,
        )


    # ========================================================
    # RUN
    # ========================================================

    @Slot()
    def run(self):

        try:

            phantom = self.create_phantom()

            # =================================================
            # COMPARISON MODE
            # =================================================

            if self.comparison_mode:

                dose_6mv, dose_18mv = (
                    self.calculate_comparison(
                        phantom
                    )
                )

                self.status.emit(
                    "6 MV vs 18 MV comparison complete."
                )

                self.comparison_finished.emit(
                    dose_6mv,
                    dose_18mv,
                )

            # =================================================
            # SINGLE MODE
            # =================================================

            else:

                beams = self.create_beams()

                dose = self.calculate_single(
                    phantom,
                    beams,
                )

                self.finished.emit(
                    dose
                )

        except Exception as error:

            self.error.emit(
                str(error)
            )