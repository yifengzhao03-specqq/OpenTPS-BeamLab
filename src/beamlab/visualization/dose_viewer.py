import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QComboBox,
)

from PySide6.QtCore import Qt


class DoseViewer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dose = None
        self.voxel_mm = 5.0
        self.prescription_cgy = 200.0

        self.build_ui()


    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # ----------------------------------------------------
        # VIEW CONTROLS
        # ----------------------------------------------------

        controls = QHBoxLayout()

        controls.addWidget(
            QLabel("View:")
        )

        self.view_combo = QComboBox()

        self.view_combo.addItems(
            [
                "Axial",
                "Coronal",
                "Sagittal",
            ]
        )

        self.view_combo.currentTextChanged.connect(
            self.change_view
        )

        controls.addWidget(
            self.view_combo
        )

        controls.addStretch()

        layout.addLayout(
            controls
        )

        # ----------------------------------------------------
        # MATPLOTLIB CANVAS
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
        # SLICE SLIDER
        # ----------------------------------------------------

        slider_layout = QHBoxLayout()

        slider_layout.addWidget(
            QLabel("Slice:")
        )

        self.slice_slider = QSlider(
            Qt.Horizontal
        )

        self.slice_slider.setMinimum(0)
        self.slice_slider.setMaximum(0)

        self.slice_slider.valueChanged.connect(
            self.update_plot
        )

        slider_layout.addWidget(
            self.slice_slider,
            1,
        )

        self.slice_label = QLabel(
            "0"
        )

        slider_layout.addWidget(
            self.slice_label
        )

        layout.addLayout(
            slider_layout
        )

        # ----------------------------------------------------
        # DOSE INFORMATION
        # ----------------------------------------------------

        self.info_label = QLabel(
            "No dose loaded."
        )

        layout.addWidget(
            self.info_label
        )

        self.show_empty_view()
    
    def save_figure(self, output_path):
        """
        Save the currently displayed dose figure as a high-resolution PNG.
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
            "No dose calculated yet.",
            horizontalalignment="center",
            verticalalignment="center",
            transform=self.ax.transAxes,
            fontsize=16,
        )

        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.canvas.draw()


    # ========================================================
    # LOAD DOSE
    # ========================================================

    def set_dose(
        self,
        dose,
        voxel_mm=5.0,
        prescription_cgy=200.0,
    ):

        self.dose = np.asarray(
            dose,
            dtype=float,
        )

        if self.dose.ndim != 3:
            raise ValueError(
                "Dose must be a 3D array."
            )

        self.voxel_mm = float(
            voxel_mm
        )

        self.prescription_cgy = float(
            prescription_cgy
        )

        self.configure_slider()

        self.update_plot()


    # ========================================================
    # VIEW
    # ========================================================

    def change_view(self):

        if self.dose is None:
            return

        self.configure_slider()
        self.update_plot()


    def configure_slider(self):

        if self.dose is None:
            return

        view = self.view_combo.currentText()

        if view == "Axial":
            number_of_slices = self.dose.shape[2]

        elif view == "Coronal":
            number_of_slices = self.dose.shape[1]

        elif view == "Sagittal":
            number_of_slices = self.dose.shape[0]

        else:
            return

        self.slice_slider.blockSignals(
            True
        )

        self.slice_slider.setMinimum(0)

        self.slice_slider.setMaximum(
            number_of_slices - 1
        )

        self.slice_slider.setValue(
            number_of_slices // 2
        )

        self.slice_slider.blockSignals(
            False
        )


    # ========================================================
    # GET CURRENT PLANE
    # ========================================================

    def get_current_plane(self):

        view = self.view_combo.currentText()

        index = self.slice_slider.value()

        if view == "Axial":

            plane = self.dose[
                :,
                :,
                index,
            ]

            x_size = self.dose.shape[0]
            y_size = self.dose.shape[1]

            xlabel = "Left-Right X (mm)"
            ylabel = "AP Y (mm)"

        elif view == "Coronal":

            plane = self.dose[
                :,
                index,
                :,
            ]

            x_size = self.dose.shape[0]
            y_size = self.dose.shape[2]

            xlabel = "Left-Right X (mm)"
            ylabel = "Superior-Inferior Z (mm)"

        elif view == "Sagittal":

            plane = self.dose[
                index,
                :,
                :,
            ]

            x_size = self.dose.shape[1]
            y_size = self.dose.shape[2]

            xlabel = "AP Y (mm)"
            ylabel = "Superior-Inferior Z (mm)"

        else:

            raise ValueError(
                "Unknown view."
            )

        x = (
            np.arange(x_size)
            - x_size // 2
        ) * self.voxel_mm

        y = (
            np.arange(y_size)
            - y_size // 2
        ) * self.voxel_mm

        return (
            plane,
            x,
            y,
            xlabel,
            ylabel,
            index,
        )


    # ========================================================
    # UPDATE PLOT
    # ========================================================

    def update_plot(self):

        if self.dose is None:
            return

        (
            plane,
            x,
            y,
            xlabel,
            ylabel,
            index,
        ) = self.get_current_plane()

        self.ax.clear()

        # ----------------------------------------------------
        # DOSE MAP
        # ----------------------------------------------------

        image = self.ax.imshow(
            plane.T,
            origin="lower",
            extent=[
                x.min(),
                x.max(),
                y.min(),
                y.max(),
            ],
            aspect="equal",
            vmin=0,
            vmax=float(
                np.max(self.dose)
            ),
        )

        # ----------------------------------------------------
        # ISODOSE CONTOURS
        # ----------------------------------------------------

        percentages = np.array(
            [
                50,
                70,
                80,
                90,
                95,
                100,
                105,
                110,
                120,
            ],
            dtype=float,
        )

        levels = (
            percentages
            / 100.0
            * self.prescription_cgy
        )

        valid_levels = levels[
            levels < np.max(plane)
        ]

        if len(valid_levels) > 0:

            contours = self.ax.contour(
                x,
                y,
                plane.T,
                levels=valid_levels,
                colors="red",
                linewidths=0.8,
            )

            self.ax.clabel(
                contours,
                inline=True,
                fontsize=7,
                fmt=lambda value:
                    f"{value / self.prescription_cgy * 100:.0f}%",
            )

        # ----------------------------------------------------
        # ISOCENTER
        # ----------------------------------------------------

        self.ax.plot(
            0.0,
            0.0,
            marker="+",
            markersize=14,
            markeredgewidth=2,
        )

        # ----------------------------------------------------
        # LABELS
        # ----------------------------------------------------

        view = self.view_combo.currentText()

        self.ax.set_title(
            f"{view} Dose Distribution"
        )

        self.ax.set_xlabel(
            xlabel
        )

        self.ax.set_ylabel(
            ylabel
        )

        self.slice_label.setText(
            str(index)
        )

        # ----------------------------------------------------
        # INFORMATION
        # ----------------------------------------------------

        center = tuple(
            dimension // 2
            for dimension in self.dose.shape
        )

        center_dose = float(
            self.dose[center]
        )

        maximum = float(
            np.max(self.dose)
        )

        self.info_label.setText(
            f"Isocenter: {center_dose:.2f} cGy    "
            f"Maximum: {maximum:.2f} cGy    "
            f"Slice: {index}"
        )

        self.figure.tight_layout()

        self.canvas.draw()