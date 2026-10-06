import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)

from beamlab.core.comparison import compare_doses


class ComparisonViewer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dose_6mv = None
        self.dose_18mv = None
        self.voxel_mm = 5.0
        self.result = None

        self.build_ui()


    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        controls = QHBoxLayout()

        # ----------------------------------------------------
        # PROFILE DIRECTION
        # ----------------------------------------------------

        controls.addWidget(
            QLabel("Profile:")
        )

        self.direction_combo = QComboBox()

        self.direction_combo.addItems(
            [
                "X — Left/Right",
                "Y — AP Depth",
                "Z — Superior/Inferior",
            ]
        )

        self.direction_combo.currentTextChanged.connect(
            self.update_plot
        )

        controls.addWidget(
            self.direction_combo
        )

        # ----------------------------------------------------
        # DISPLAY MODE
        # ----------------------------------------------------

        controls.addWidget(
            QLabel("Display:")
        )

        self.display_combo = QComboBox()

        self.display_combo.addItems(
            [
                "Absolute Dose (cGy)",
                "Relative Dose (%)",
            ]
        )

        self.display_combo.currentTextChanged.connect(
            self.update_plot
        )

        controls.addWidget(
            self.display_combo
        )

        controls.addStretch()

        layout.addLayout(
            controls
        )

        # ----------------------------------------------------
        # FIGURE
        # ----------------------------------------------------

        self.figure = Figure(
            figsize=(8, 6)
        )

        self.canvas = FigureCanvasQTAgg(
            self.figure
        )

        self.ax = self.figure.add_subplot(
            111
        )

        layout.addWidget(
            self.canvas,
            1,
        )

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        self.info_label = QLabel(
            "No comparison loaded."
        )

        layout.addWidget(
            self.info_label
        )

        self.show_empty_view()

    def save_figure(self, output_path):
        """
        Save the currently displayed comparison profile
        as a high-resolution PNG.
        """

        self.figure.savefig(
            str(output_path),
            dpi=300,
            bbox_inches="tight",
        )

    # ========================================================
    # EMPTY VIEW
    # ========================================================

    def show_empty_view(self):

        self.ax.clear()

        self.ax.text(
            0.5,
            0.5,
            "No comparison loaded.",
            horizontalalignment="center",
            verticalalignment="center",
            transform=self.ax.transAxes,
            fontsize=16,
        )

        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.canvas.draw()


    # ========================================================
    # SET DOSES
    # ========================================================

    def set_doses(
        self,
        dose_6mv,
        dose_18mv,
        voxel_mm=5.0,
    ):

        self.dose_6mv = np.asarray(
            dose_6mv,
            dtype=float,
        )

        self.dose_18mv = np.asarray(
            dose_18mv,
            dtype=float,
        )

        self.voxel_mm = float(
            voxel_mm
        )

        self.result = compare_doses(
            self.dose_6mv,
            self.dose_18mv,
            voxel_mm=self.voxel_mm,
        )

        self.update_plot()


    # ========================================================
    # DIRECTION
    # ========================================================

    def get_direction(self):

        text = (
            self.direction_combo.currentText()
        )

        if text.startswith("X"):
            return "x"

        if text.startswith("Y"):
            return "y"

        if text.startswith("Z"):
            return "z"

        return "x"


    # ========================================================
    # NORMALIZE PROFILE
    # ========================================================

    def normalize_profile(
        self,
        dose,
    ):

        dose = np.asarray(
            dose,
            dtype=float,
        )

        center_index = (
            len(dose) // 2
        )

        center_dose = float(
            dose[center_index]
        )

        if center_dose <= 0:
            return dose

        return (
            dose
            / center_dose
            * 100.0
        )


    # ========================================================
    # UPDATE PLOT
    # ========================================================

    def update_plot(self):

        if self.result is None:
            return

        direction = (
            self.get_direction()
        )

        profile_6 = (
            self.result[
                "profiles_a"
            ][direction]
        )

        profile_18 = (
            self.result[
                "profiles_b"
            ][direction]
        )

        position = np.asarray(
            profile_6[
                "position_mm"
            ],
            dtype=float,
        )

        dose_6 = np.asarray(
            profile_6[
                "dose"
            ],
            dtype=float,
        )

        dose_18 = np.asarray(
            profile_18[
                "dose"
            ],
            dtype=float,
        )

        display_mode = (
            self.display_combo.currentText()
        )

        # ----------------------------------------------------
        # ABSOLUTE / RELATIVE
        # ----------------------------------------------------

        if display_mode == "Relative Dose (%)":

            plot_6 = self.normalize_profile(
                dose_6
            )

            plot_18 = self.normalize_profile(
                dose_18
            )

            ylabel = (
                "Relative Dose (%)"
            )

        else:

            plot_6 = dose_6
            plot_18 = dose_18

            ylabel = (
                "Dose (cGy)"
            )

        # ----------------------------------------------------
        # AXIS LABEL
        # ----------------------------------------------------

        if direction == "x":

            profile_name = (
                "Left–Right Profile"
            )

            xlabel = (
                "Left–Right Position (mm)"
            )

        elif direction == "y":

            profile_name = (
                "AP Depth Profile"
            )

            xlabel = (
                "AP Position (mm)"
            )

        else:

            profile_name = (
                "Superior–Inferior Profile"
            )

            xlabel = (
                "Superior–Inferior Position (mm)"
            )

        # ----------------------------------------------------
        # PLOT
        # ----------------------------------------------------

        self.ax.clear()

        self.ax.plot(
            position,
            plot_6,
            linewidth=2,
            label="6 MV",
        )

        self.ax.plot(
            position,
            plot_18,
            linewidth=2,
            label="18 MV",
        )

        # Isocenter
        self.ax.axvline(
            0.0,
            linestyle="--",
            linewidth=1,
            label="Isocenter",
        )

        if display_mode == "Relative Dose (%)":

            self.ax.axhline(
                100.0,
                linestyle=":",
                linewidth=1,
            )

        self.ax.set_title(
            f"6 MV vs 18 MV — {profile_name}"
        )

        self.ax.set_xlabel(
            xlabel
        )

        self.ax.set_ylabel(
            ylabel
        )

        self.ax.grid(
            True,
            alpha=0.3,
        )

        self.ax.legend()

        # ----------------------------------------------------
        # CENTER DOSES
        # ----------------------------------------------------

        center_6 = float(
            dose_6[
                len(dose_6) // 2
            ]
        )

        center_18 = float(
            dose_18[
                len(dose_18) // 2
            ]
        )

        self.info_label.setText(
            f"6 MV isocenter: "
            f"{center_6:.2f} cGy    "
            f"18 MV isocenter: "
            f"{center_18:.2f} cGy    "
            f"Maximum 6 MV: "
            f"{self.result['max_a']:.2f} cGy    "
            f"Maximum 18 MV: "
            f"{self.result['max_b']:.2f} cGy"
        )

        self.figure.tight_layout()

        self.canvas.draw()