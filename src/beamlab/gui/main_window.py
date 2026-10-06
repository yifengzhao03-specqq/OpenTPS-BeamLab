import sys
from pathlib import Path


import numpy as np

from PySide6.QtCore import QThread

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QStackedWidget,
    QTabWidget,
    QFileDialog,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# BEAMLAB
# ============================================================

from beamlab.gui.dose_worker import DoseCalculationWorker
from beamlab.visualization.dose_viewer import DoseViewer
from beamlab.visualization.comparison_viewer import ComparisonViewer
from beamlab.visualization.difference_viewer import DifferenceViewer
from beamlab.gui.kernel_builder_widget import KernelBuilderWidget

# ============================================================
# MAIN WINDOW
# ============================================================

class BeamLabMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenTPS BeamLab")
        self.resize(1400, 850)

        # Dose results
        self.dose = None
        self.dose_6mv = None
        self.dose_18mv = None

        # Thread objects
        self.thread = None
        self.worker = None

        # Calculation settings
        self.current_mode = None
        self.current_energy_text = None
        self.current_geometry = None
        self.current_field_size = None
        self.current_prescription = None
        self.current_weights = None

        self.build_ui()


    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # ====================================================
        # MAIN APPLICATION TABS
        # ====================================================

        app_layout = QVBoxLayout(central_widget)

        self.main_tabs = QTabWidget()

        app_layout.addWidget(
            self.main_tabs
        )

        # ====================================================
        # PAGE 1 — DOSE CALCULATOR
        # ====================================================

        dose_page = QWidget()

        main_layout = QHBoxLayout(
            dose_page
        )

        # ====================================================
        # LEFT PANEL
        # ====================================================

        control_panel = QGroupBox("Dose Setup")
        control_panel.setMaximumWidth(310)

        controls = QVBoxLayout(control_panel)

        # ----------------------------------------------------
        # CALCULATION MODE
        # ----------------------------------------------------

        controls.addWidget(
            QLabel("Calculation Mode")
        )

        self.mode_combo = QComboBox()

        self.mode_combo.addItems(
            [
                "Single Energy",
                "Compare 6 MV vs 18 MV",
            ]
        )

        self.mode_combo.currentTextChanged.connect(
            self.update_mode
        )

        controls.addWidget(
            self.mode_combo
        )

        # ----------------------------------------------------
        # ENERGY
        # ----------------------------------------------------

        self.energy_label = QLabel(
            "Photon Energy"
        )

        controls.addWidget(
            self.energy_label
        )

        self.energy_combo = QComboBox()

        self.energy_combo.addItems(
            [
                "6 MV",
                "18 MV",
            ]
        )

        controls.addWidget(
            self.energy_combo
        )

        # ----------------------------------------------------
        # GEOMETRY
        # ----------------------------------------------------

        controls.addWidget(
            QLabel("Beam Geometry")
        )

        self.geometry_combo = QComboBox()

        self.geometry_combo.addItems(
            [
                "AP/PA",
                "Four-Field Box",
            ]
        )

        self.geometry_combo.currentTextChanged.connect(
            self.update_weight_controls
        )

        controls.addWidget(
            self.geometry_combo
        )

        # ----------------------------------------------------
        # FIELD SIZE
        # ----------------------------------------------------

        controls.addWidget(
            QLabel("Field Size")
        )

        self.field_size = QDoubleSpinBox()

        self.field_size.setRange(
            10.0,
            400.0,
        )

        self.field_size.setValue(
            150.0
        )

        self.field_size.setSuffix(
            " mm"
        )

        controls.addWidget(
            self.field_size
        )

        # ----------------------------------------------------
        # PRESCRIPTION
        # ----------------------------------------------------

        controls.addWidget(
            QLabel("Prescription Dose")
        )

        self.prescription = QDoubleSpinBox()

        self.prescription.setRange(
            1.0,
            10000.0,
        )

        self.prescription.setValue(
            200.0
        )

        self.prescription.setSuffix(
            " cGy"
        )

        controls.addWidget(
            self.prescription
        )

        # ====================================================
        # BEAM WEIGHTS
        # ====================================================

        self.weight_group = QGroupBox(
            "Beam Weights"
        )

        self.weight_layout = QFormLayout(
            self.weight_group
        )

        self.ap_weight = self.create_weight_box()
        self.left_weight = self.create_weight_box()
        self.pa_weight = self.create_weight_box()
        self.right_weight = self.create_weight_box()

        self.weight_layout.addRow(
            "AP (0°)",
            self.ap_weight,
        )

        self.weight_layout.addRow(
            "Left (90°)",
            self.left_weight,
        )

        self.weight_layout.addRow(
            "PA (180°)",
            self.pa_weight,
        )

        self.weight_layout.addRow(
            "Right (270°)",
            self.right_weight,
        )

        controls.addWidget(
            self.weight_group
        )

        # ----------------------------------------------------
        # CALCULATE
        # ----------------------------------------------------

        self.calculate_button = QPushButton(
            "Calculate Dose"
        )

        self.calculate_button.clicked.connect(
            self.start_calculation
        )

        controls.addWidget(
            self.calculate_button
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        self.save_button = QPushButton(
            "Save Results"
        )

        self.save_button.setEnabled(
            False
        )

        self.save_button.clicked.connect(
            self.save_results
        )

        controls.addWidget(
            self.save_button
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_label = QLabel(
            "Ready"
        )

        self.status_label.setWordWrap(
            True
        )

        controls.addWidget(
            self.status_label
        )

        controls.addStretch()

        # ====================================================
        # RIGHT PANEL
        # ====================================================

        result_panel = QGroupBox(
            "Results"
        )

        result_layout = QVBoxLayout(
            result_panel
        )

        self.result_stack = QStackedWidget()

        # ====================================================
        # PAGE 0 — SINGLE ENERGY
        # ====================================================

        self.dose_viewer = DoseViewer()

        self.result_stack.addWidget(
            self.dose_viewer
        )

        # ====================================================
        # PAGE 1 — COMPARISON
        # ====================================================

        self.comparison_tabs = QTabWidget()

        # ----------------------------------------------------
        # PROFILE TAB
        # ----------------------------------------------------

        self.comparison_viewer = ComparisonViewer()

        self.comparison_tabs.addTab(
            self.comparison_viewer,
            "Profiles",
        )

        # ----------------------------------------------------
        # DIFFERENCE MAP TAB
        # ----------------------------------------------------

        self.difference_viewer = DifferenceViewer()

        self.comparison_tabs.addTab(
            self.difference_viewer,
            "Difference Map",
        )

        self.result_stack.addWidget(
            self.comparison_tabs
        )

        result_layout.addWidget(
            self.result_stack
        )

        # ====================================================
        # ADD PANELS
        # ====================================================

        main_layout.addWidget(
            control_panel
        )

        main_layout.addWidget(
            result_panel,
            1,
        )

        # ====================================================
        # ADD DOSE PAGE
        # ====================================================

        self.main_tabs.addTab(
            dose_page,
            "Dose Calculator",
        )

        # ====================================================
        # PAGE 2 — KERNEL BUILDER
        # ====================================================

        self.kernel_builder = KernelBuilderWidget()

        self.main_tabs.addTab(
            self.kernel_builder,
            "Kernel Builder",
        )

        # ====================================================
        # INITIAL STATE
        # ====================================================

        self.update_weight_controls()
        self.update_mode()


    # ========================================================
    # CREATE WEIGHT BOX
    # ========================================================

    def create_weight_box(self):

        box = QDoubleSpinBox()

        box.setRange(
            0.0,
            10.0,
        )

        box.setDecimals(
            2
        )

        box.setSingleStep(
            0.1
        )

        box.setValue(
            1.0
        )

        return box


    # ========================================================
    # UPDATE MODE
    # ========================================================

    def update_mode(self):

        mode = self.mode_combo.currentText()

        if mode == "Single Energy":

            self.energy_label.setVisible(
                True
            )

            self.energy_combo.setVisible(
                True
            )

            self.calculate_button.setText(
                "Calculate Dose"
            )

            self.result_stack.setCurrentIndex(
                0
            )

        else:

            self.energy_label.setVisible(
                False
            )

            self.energy_combo.setVisible(
                False
            )

            self.calculate_button.setText(
                "Compare 6 MV vs 18 MV"
            )

            self.result_stack.setCurrentIndex(
                1
            )


    # ========================================================
    # UPDATE WEIGHT CONTROLS
    # ========================================================

    def update_weight_controls(self):

        geometry = self.geometry_combo.currentText()

        show_left_right = (
            geometry == "Four-Field Box"
        )

        self.left_weight.setVisible(
            show_left_right
        )

        self.right_weight.setVisible(
            show_left_right
        )

        left_label = self.weight_layout.labelForField(
            self.left_weight
        )

        right_label = self.weight_layout.labelForField(
            self.right_weight
        )

        if left_label is not None:
            left_label.setVisible(
                show_left_right
            )

        if right_label is not None:
            right_label.setVisible(
                show_left_right
            )


    # ========================================================
    # GET WEIGHTS
    # ========================================================

    def get_weights(self):

        geometry = self.geometry_combo.currentText()

        if geometry == "AP/PA":

            return (
                self.ap_weight.value(),
                self.pa_weight.value(),
            )

        if geometry == "Four-Field Box":

            return (
                self.ap_weight.value(),
                self.left_weight.value(),
                self.pa_weight.value(),
                self.right_weight.value(),
            )

        raise ValueError(
            "Unsupported beam geometry."
        )


    # ========================================================
    # START CALCULATION
    # ========================================================

    def start_calculation(self):

        mode = self.mode_combo.currentText()

        comparison_mode = (
            mode == "Compare 6 MV vs 18 MV"
        )

        energy_text = self.energy_combo.currentText()

        energy = (
            energy_text
            .replace(" ", "")
            .upper()
        )

        geometry = self.geometry_combo.currentText()

        field_size = self.field_size.value()

        prescription = self.prescription.value()

        weights = self.get_weights()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if sum(weights) <= 0:

            QMessageBox.warning(
                self,
                "Invalid Beam Weights",
                "At least one beam weight must be greater than zero.",
            )

            return

        # ----------------------------------------------------
        # SAVE SETTINGS
        # ----------------------------------------------------

        self.current_mode = mode
        self.current_energy_text = energy_text
        self.current_geometry = geometry
        self.current_field_size = field_size
        self.current_prescription = prescription
        self.current_weights = weights

        # Old results should not be saved while a new
        # calculation is running.
        self.save_button.setEnabled(
            False
        )

        # ----------------------------------------------------
        # GUI STATE
        # ----------------------------------------------------

        self.calculate_button.setEnabled(
            False
        )

        if comparison_mode:

            self.status_label.setText(
                "Starting 6 MV vs 18 MV comparison..."
            )

        else:

            self.status_label.setText(
                "Starting dose calculation..."
            )

        # ====================================================
        # THREAD
        # ====================================================

        self.thread = QThread()

        self.worker = DoseCalculationWorker(
            energy=energy,
            geometry=geometry,
            field_size_mm=field_size,
            prescription_cgy=prescription,
            weights=weights,
            comparison_mode=comparison_mode,
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.status.connect(
            self.update_status
        )

        self.worker.finished.connect(
            self.calculation_finished
        )

        self.worker.comparison_finished.connect(
            self.comparison_finished
        )

        self.worker.error.connect(
            self.calculation_error
        )

        # ----------------------------------------------------
        # QUIT THREAD
        # ----------------------------------------------------

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.comparison_finished.connect(
            self.thread.quit
        )

        self.worker.error.connect(
            self.thread.quit
        )

        # ----------------------------------------------------
        # CLEAN WORKER
        # ----------------------------------------------------

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.comparison_finished.connect(
            self.worker.deleteLater
        )

        self.worker.error.connect(
            self.worker.deleteLater
        )

        # ----------------------------------------------------
        # CLEAN THREAD
        # ----------------------------------------------------

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.thread_cleanup
        )

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        self.thread.start()


    # ========================================================
    # STATUS
    # ========================================================

    def update_status(
        self,
        message,
    ):

        self.status_label.setText(
            message
        )


    # ========================================================
    # SINGLE RESULT
    # ========================================================

    def calculation_finished(
        self,
        dose,
    ):

        self.dose = dose

        self.result_stack.setCurrentIndex(
            0
        )

        self.dose_viewer.set_dose(
            dose=self.dose,
            voxel_mm=5.0,
            prescription_cgy=self.current_prescription,
        )

        maximum = float(
            self.dose.max()
        )

        weight_text = ", ".join(
            f"{value:.2f}"
            for value in self.current_weights
        )

        self.status_label.setText(
            "Calculation complete.\n\n"
            f"{self.current_energy_text}\n"
            f"{self.current_geometry}\n"
            f"{self.current_field_size:.0f} mm field\n"
            f"Weights: {weight_text}\n\n"
            f"Maximum: {maximum:.2f} cGy"
        )

        self.save_button.setEnabled(
            True
        )


    # ========================================================
    # COMPARISON RESULT
    # ========================================================

    def comparison_finished(
        self,
        dose_6mv,
        dose_18mv,
    ):

        self.dose_6mv = dose_6mv
        self.dose_18mv = dose_18mv

        self.result_stack.setCurrentIndex(
            1
        )

        # ----------------------------------------------------
        # PROFILE VIEWER
        # ----------------------------------------------------

        self.comparison_viewer.set_doses(
            dose_6mv=self.dose_6mv,
            dose_18mv=self.dose_18mv,
            voxel_mm=5.0,
        )

        # ----------------------------------------------------
        # DIFFERENCE VIEWER
        # ----------------------------------------------------

        self.difference_viewer.set_doses(
            dose_6mv=self.dose_6mv,
            dose_18mv=self.dose_18mv,
            voxel_mm=5.0,
            prescription_cgy=self.current_prescription,
        )

        self.comparison_tabs.setCurrentIndex(
            0
        )

        weight_text = ", ".join(
            f"{value:.2f}"
            for value in self.current_weights
        )

        self.status_label.setText(
            "Comparison complete.\n\n"
            "6 MV vs 18 MV\n"
            f"{self.current_geometry}\n"
            f"{self.current_field_size:.0f} mm field\n"
            f"Weights: {weight_text}\n"
            f"Normalized to: "
            f"{self.current_prescription:.0f} cGy"
        )

        self.save_button.setEnabled(
            True
        )


    # ========================================================
    # ERROR
    # ========================================================

    def calculation_error(
        self,
        message,
    ):

        self.status_label.setText(
            "Calculation failed."
        )

        QMessageBox.critical(
            self,
            "Dose Calculation Error",
            message,
        )


    # ========================================================
    # SAVE RESULTS
    # ========================================================

    def save_results(self):

        if self.current_mode is None:
            QMessageBox.warning(
                self,
                "No Results",
                "No calculation results are available.",
            )
            return

        # ----------------------------------------------------
        # SELECT FOLDER
        # ----------------------------------------------------

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Save BeamLab Results",
            str(PROJECT_ROOT / "data"),
        )

        if not folder:
            return

        output_folder = Path(folder)

        # ====================================================
        # SINGLE ENERGY
        # ====================================================

        if self.current_mode == "Single Energy":

            if self.dose is None:
                QMessageBox.warning(
                    self,
                    "No Dose",
                    "No dose matrix is available.",
                )
                return

            energy_name = self.current_energy_text.replace(" ", "")

            geometry_name = (
                self.current_geometry
                .replace("/", "-")
                .replace(" ", "_")
            )

            base_name = (
                f"BeamLab_"
                f"{energy_name}_"
                f"{geometry_name}_"
                f"{self.current_field_size:.0f}mm"
            )

            # Save dose matrix
            output_path = output_folder / f"{base_name}.npy"

            np.save(
                output_path,
                self.dose,
            )

            # Save dose figure
            figure_path = (
                output_folder
                / f"{base_name}_isodose.png"
            )

            self.dose_viewer.save_figure(
                figure_path
            )

            # Show message only AFTER everything has been saved
            QMessageBox.information(
                self,
                "Results Saved",
                "Results saved successfully.\n\n"
                f"Dose matrix:\n{output_path}\n\n"
                f"Figure:\n{figure_path}",
            )

        # ====================================================
        # COMPARISON
        # ====================================================

        elif self.current_mode == "Compare 6 MV vs 18 MV":

            if (
                self.dose_6mv is None
                or self.dose_18mv is None
            ):
                QMessageBox.warning(
                    self,
                    "No Comparison",
                    "Comparison dose matrices are not available.",
                )
                return

            geometry_name = (
                self.current_geometry
                .replace("/", "-")
                .replace(" ", "_")
            )

            base_name = (
                f"BeamLab_Comparison_"
                f"{geometry_name}_"
                f"{self.current_field_size:.0f}mm"
            )

            # ------------------------------------------------
            # 6 MV
            # ------------------------------------------------

            path_6mv = (
                output_folder
                / f"{base_name}_6MV.npy"
            )

            np.save(
                path_6mv,
                self.dose_6mv,
            )

            # ------------------------------------------------
            # 18 MV
            # ------------------------------------------------

            path_18mv = (
                output_folder
                / f"{base_name}_18MV.npy"
            )

            np.save(
                path_18mv,
                self.dose_18mv,
            )

            # ------------------------------------------------
            # DIFFERENCE = 18 MV - 6 MV
            # ------------------------------------------------

            difference = (
                self.dose_18mv
                - self.dose_6mv
            )

            path_difference = (
                output_folder
                / f"{base_name}_18MV_minus_6MV.npy"
            )

            np.save(
                path_difference,
                difference,
            )

            # ------------------------------------------------
            # SAVE PROFILE FIGURE
            # ------------------------------------------------

            path_profiles = (
                output_folder
                / f"{base_name}_profiles.png"
            )

            self.comparison_viewer.save_figure(
                path_profiles
            )

            # ------------------------------------------------
            # SAVE DIFFERENCE MAP
            # ------------------------------------------------

            path_difference_figure = (
                output_folder
                / f"{base_name}_difference.png"
            )

            self.difference_viewer.save_figure(
                path_difference_figure
            )

            # ------------------------------------------------
            # SUCCESS MESSAGE
            # ------------------------------------------------

            QMessageBox.information(
                self,
                "Results Saved",
                "Comparison results saved successfully.\n\n"
                f"6 MV dose:\n{path_6mv}\n\n"
                f"18 MV dose:\n{path_18mv}\n\n"
                f"Difference dose:\n{path_difference}\n\n"
                f"Profiles:\n{path_profiles}\n\n"
                f"Difference map:\n{path_difference_figure}",
            )


    # ========================================================
    # THREAD CLEANUP
    # ========================================================

    def thread_cleanup(self):

        self.thread = None
        self.worker = None

        self.calculate_button.setEnabled(
            True
        )


# ============================================================
# RUN
# ============================================================

def run():

    app = QApplication(
        sys.argv
    )

    window = BeamLabMainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    run()