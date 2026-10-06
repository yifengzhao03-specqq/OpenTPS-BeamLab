import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSlider,
)


class DifferenceViewer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dose_6mv = None
        self.dose_18mv = None
        self.difference = None

        self.voxel_mm = 5.0
        self.prescription_cgy = 200.0

        self.build_ui()


    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # ----------------------------------------------------
        # CONTROLS
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

        controls.addWidget(
            QLabel("Display:")
        )

        self.display_combo = QComboBox()

        self.display_combo.addItems(
            [
                "Absolute Difference (cGy)",
                "Difference (% Rx)",
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
        # SLIDER
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
        Save the currently displayed difference map
        as a high-resolution PNG.
        """

        self.figure.savefig(
            str(output_path),
            dpi=300,
            bbox_inches="tight",
        )

    # ========================================================
    # EMPTY
    # ========================================================

    def show_empty_view(self):

        self.ax.clear()

        self.ax.text(
            0.5,
            0.5,
            "No difference map loaded.",
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
        prescription_cgy=200.0,
    ):

        self.dose_6mv = np.asarray(
            dose_6mv,
            dtype=float,
        )

        self.dose_18mv = np.asarray(
            dose_18mv,
            dtype=float,
        )

        if (
            self.dose_6mv.shape
            !=
            self.dose_18mv.shape
        ):
            raise ValueError(
                "6 MV and 18 MV dose matrices "
                "must have the same shape."
            )

        self.voxel_mm = float(
            voxel_mm
        )

        self.prescription_cgy = float(
            prescription_cgy
        )

        # IMPORTANT:
        # Positive = 18 MV dose is higher
        # Negative = 6 MV dose is higher

        self.difference = (
            self.dose_18mv
            -
            self.dose_6mv
        )

        self.configure_slider()

        self.update_plot()


    # ========================================================
    # CHANGE VIEW
    # ========================================================

    def change_view(self):

        if self.difference is None:
            return

        self.configure_slider()

        self.update_plot()


    # ========================================================
    # SLIDER
    # ========================================================

    def configure_slider(self):

        if self.difference is None:
            return

        view = (
            self.view_combo.currentText()
        )

        if view == "Axial":

            number_of_slices = (
                self.difference.shape[2]
            )

        elif view == "Coronal":

            number_of_slices = (
                self.difference.shape[1]
            )

        else:

            number_of_slices = (
                self.difference.shape[0]
            )

        self.slice_slider.blockSignals(
            True
        )

        self.slice_slider.setMinimum(
            0
        )

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
    # GET PLANE
    # ========================================================

    def get_current_plane(self):

        view = (
            self.view_combo.currentText()
        )

        index = (
            self.slice_slider.value()
        )

        if view == "Axial":

            plane = (
                self.difference[
                    :,
                    :,
                    index,
                ]
            )

            x_size = (
                self.difference.shape[0]
            )

            y_size = (
                self.difference.shape[1]
            )

            xlabel = (
                "Left–Right X (mm)"
            )

            ylabel = (
                "AP Y (mm)"
            )

        elif view == "Coronal":

            plane = (
                self.difference[
                    :,
                    index,
                    :,
                ]
            )

            x_size = (
                self.difference.shape[0]
            )

            y_size = (
                self.difference.shape[2]
            )

            xlabel = (
                "Left–Right X (mm)"
            )

            ylabel = (
                "Superior–Inferior Z (mm)"
            )

        else:

            plane = (
                self.difference[
                    index,
                    :,
                    :,
                ]
            )

            x_size = (
                self.difference.shape[1]
            )

            y_size = (
                self.difference.shape[2]
            )

            xlabel = (
                "AP Y (mm)"
            )

            ylabel = (
                "Superior–Inferior Z (mm)"
            )

        x = (
            np.arange(x_size)
            -
            x_size // 2
        ) * self.voxel_mm

        y = (
            np.arange(y_size)
            -
            y_size // 2
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

        if self.difference is None:
            return

        (
            plane,
            x,
            y,
            xlabel,
            ylabel,
            index,
        ) = self.get_current_plane()

        display_mode = (
            self.display_combo.currentText()
        )

        # ----------------------------------------------------
        # DISPLAY DATA
        # ----------------------------------------------------

        if (
            display_mode
            ==
            "Difference (% Rx)"
        ):

            if self.prescription_cgy <= 0:
                raise ValueError(
                    "Prescription must be positive."
                )

            display_plane = (
                plane
                /
                self.prescription_cgy
                *
                100.0
            )

            unit = "% Rx"

        else:

            display_plane = plane

            unit = "cGy"

        # ----------------------------------------------------
        # SYMMETRIC RANGE AROUND ZERO
        # ----------------------------------------------------

        max_abs = float(
            np.max(
                np.abs(
                    display_plane
                )
            )
        )

        if max_abs == 0:
            max_abs = 1.0

        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------

        self.ax.clear()

        image = self.ax.imshow(
            display_plane.T,
            origin="lower",
            extent=[
                x.min(),
                x.max(),
                y.min(),
                y.max(),
            ],
            aspect="equal",
            cmap="coolwarm",
            vmin=-max_abs,
            vmax=max_abs,
        )

        # ----------------------------------------------------
        # ZERO DIFFERENCE CONTOUR
        # ----------------------------------------------------

        if (
            np.min(display_plane) < 0
            and
            np.max(display_plane) > 0
        ):

            self.ax.contour(
                x,
                y,
                display_plane.T,
                levels=[0.0],
                colors="black",
                linewidths=0.8,
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
            color="black",
        )

        # ----------------------------------------------------
        # COLORBAR
        # ----------------------------------------------------

        if hasattr(
            self,
            "_colorbar",
        ):

            self._colorbar.remove()

        self._colorbar = (
            self.figure.colorbar(
                image,
                ax=self.ax,
            )
        )

        self._colorbar.set_label(
            f"18 MV − 6 MV ({unit})"
        )

        # ----------------------------------------------------
        # LABELS
        # ----------------------------------------------------

        view = (
            self.view_combo.currentText()
        )

        self.ax.set_title(
            f"{view} Dose Difference: "
            f"18 MV − 6 MV"
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
        # INFO
        # ----------------------------------------------------

        global_min = float(
            np.min(
                self.difference
            )
        )

        global_max = float(
            np.max(
                self.difference
            )
        )

        global_abs = float(
            np.max(
                np.abs(
                    self.difference
                )
            )
        )

        self.info_label.setText(
            "Positive = 18 MV higher    "
            "Negative = 6 MV higher    "
            f"Min: {global_min:.2f} cGy    "
            f"Max: {global_max:.2f} cGy    "
            f"Max |Δ|: {global_abs:.2f} cGy"
        )

        self.figure.tight_layout()

        self.canvas.draw()