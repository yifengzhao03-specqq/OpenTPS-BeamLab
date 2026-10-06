from pathlib import Path
from beamlab.kernel import opentps_kernel_builder
from beamlab.kernel import opentps_kernel_validator
from beamlab.kernel import kernel_comparator

from PySide6.QtWidgets import (
    QApplication,   
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QMessageBox,
)


class KernelBuilderWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.build_ui()
        self.inspect_edk_folder()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            "OpenTPS Photon Kernel Builder"
        )

        title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(title)

        description = QLabel(
            "Build OpenTPS-compatible photon kernels "
            "from EDKnrc energy-deposition kernel files."
        )

        description.setWordWrap(True)

        main_layout.addWidget(description)

        # ====================================================
        # PATH SETTINGS
        # ====================================================

        path_group = QGroupBox(
            "Kernel Sources"
        )

        path_layout = QFormLayout(
            path_group
        )

        # ----------------------------------------------------
        # EDK FOLDER
        # ----------------------------------------------------

        self.edk_folder_edit = QLineEdit(
            r"C:\EGSnrc\egs_home\edknrc"
        )

        edk_row = QHBoxLayout()

        edk_row.addWidget(
            self.edk_folder_edit
        )

        self.edk_browse_button = QPushButton(
            "Browse"
        )

        self.edk_browse_button.clicked.connect(
            self.browse_edk_folder
        )

        edk_row.addWidget(
            self.edk_browse_button
        )

        path_layout.addRow(
            "EDKnrc Folder:",
            edk_row,
        )

        # ----------------------------------------------------
        # BASE KERNEL
        # ----------------------------------------------------

        self.base_kernel_edit = QLineEdit(
            r"C:\Users\Yifen\opentps\OpenTPS_venv"
            r"\Lib\site-packages\opentps\core"
            r"\processing\doseCalculation\photons"
            r"\Kernels_6MV"
        )

        base_row = QHBoxLayout()

        base_row.addWidget(
            self.base_kernel_edit
        )

        self.base_browse_button = QPushButton(
            "Browse"
        )

        self.base_browse_button.clicked.connect(
            self.browse_base_kernel
        )

        base_row.addWidget(
            self.base_browse_button
        )

        path_layout.addRow(
            "Base OpenTPS Kernel:",
            base_row,
        )

        # ----------------------------------------------------
        # OUTPUT FOLDER
        # ----------------------------------------------------

        default_output = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "Kernels_18MV_test"
        )

        self.output_folder_edit = QLineEdit(
            str(default_output)
        )

        output_row = QHBoxLayout()

        output_row.addWidget(
            self.output_folder_edit
        )

        self.output_browse_button = QPushButton(
            "Browse"
        )

        self.output_browse_button.clicked.connect(
            self.browse_output_folder
        )

        output_row.addWidget(
            self.output_browse_button
        )

        path_layout.addRow(
            "Output Folder:",
            output_row,
        )

        main_layout.addWidget(
            path_group
        )

        # ====================================================
        # EDK STATUS
        # ====================================================

        status_group = QGroupBox(
            "Detected EDK Kernels"
        )

        status_layout = QVBoxLayout(
            status_group
        )

        self.energy_labels = {}

        for energy in [
            8,
            10,
            12,
            15,
            18,
        ]:

            label = QLabel(
                f"○ {energy} MeV"
            )

            self.energy_labels[
                energy
            ] = label

            status_layout.addWidget(
                label
            )

        main_layout.addWidget(
            status_group
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        button_layout = QHBoxLayout()

        self.inspect_button = QPushButton(
            "Inspect EDK"
        )

        self.inspect_button.clicked.connect(
            self.inspect_edk_folder
        )

        button_layout.addWidget(
            self.inspect_button
        )
        self.compare_button = QPushButton(
            "Compare with Installed Kernel"
        )

        self.compare_button.setEnabled(
            False
        )

        self.compare_button.clicked.connect(
            self.compare_kernel
        )

        button_layout.addWidget(
            self.compare_button
        )        
        self.validate_button = QPushButton(
            "Validate Kernel"
        )

        self.validate_button.setEnabled(
            False
        )

        self.validate_button.clicked.connect(
            self.validate_kernel
        )

        button_layout.addWidget(
            self.validate_button
        )
        
        self.build_button = QPushButton(
        "Build Kernel"
)

        self.build_button.setEnabled(
            False
        )

        self.build_button.clicked.connect(
            self.build_kernel
        )

        button_layout.addWidget(
            self.build_button
        )

        main_layout.addLayout(
            button_layout
        )

        # ====================================================
        # STATUS
        # ====================================================

        self.status_label = QLabel(
            "Ready"
        )

        self.status_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.status_label
        )

        main_layout.addStretch()

    # ========================================================
    # BROWSE EDK
    # ========================================================

    def browse_edk_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select EDKnrc Folder",
            self.edk_folder_edit.text(),
        )

        if folder:

            self.edk_folder_edit.setText(
                folder
            )

            self.inspect_edk_folder()

    # ========================================================
    # BROWSE BASE KERNEL
    # ========================================================

    def browse_base_kernel(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select OpenTPS Base Kernel",
            self.base_kernel_edit.text(),
        )

        if folder:

            self.base_kernel_edit.setText(
                folder
            )

    # ========================================================
    # BROWSE OUTPUT
    # ========================================================

    def browse_output_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Kernel Output Folder",
            self.output_folder_edit.text(),
        )

        if folder:

            self.output_folder_edit.setText(
                folder
            )

    # ========================================================
    # INSPECT EDK
    # ========================================================

    def inspect_edk_folder(self):

        folder = Path(
            self.edk_folder_edit.text()
        )

        all_found = True
        found_count = 0

        for energy in [
            8,
            10,
            12,
            15,
            18,
        ]:

            file_path = (
                folder
                / f"{energy}MeV_MVgrid.keV"
            )

            label = self.energy_labels[
                energy
            ]

            if file_path.exists():

                label.setText(
                    f"✓ {energy} MeV    "
                    f"{file_path.name}"
                )

                found_count += 1

            else:

                label.setText(
                    f"✗ {energy} MeV    Missing"
                )

                all_found = False

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if all_found:

            self.status_label.setText(
                "EDKnrc inspection complete.\n"
                "5 / 5 required high-energy "
                "kernel files detected."
            )

            self.build_button.setEnabled(
                True
            )

            output_folder = Path(
                self.output_folder_edit.text()
            )

            if (
                output_folder
                / "kernel_header.txt"
            ).exists():

                self.validate_button.setEnabled(
                    True
                )
        else:

            self.status_label.setText(
                "EDKnrc inspection complete.\n"
                f"{found_count} / 5 required "
                "kernel files detected."
            )

            self.build_button.setEnabled(
                False
            )

    # ========================================================
    # BUILD KERNEL
    # ========================================================

    def build_kernel(self):

        edk_folder = Path(
            self.edk_folder_edit.text()
        )

        base_folder = Path(
            self.base_kernel_edit.text()
        )

        output_folder = Path(
            self.output_folder_edit.text()
        )

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not edk_folder.exists():

            QMessageBox.warning(
                self,
                "Invalid EDK Folder",
                f"EDKnrc folder does not exist:\n\n"
                f"{edk_folder}",
            )

            return

        if not base_folder.exists():

            QMessageBox.warning(
                self,
                "Invalid Base Kernel",
                f"Base OpenTPS kernel folder "
                f"does not exist:\n\n"
                f"{base_folder}",
            )

            return

        required_base_files = [
            "energies.bin",
            "fluence.bin",
            "mu.bin",
            "mu_en.bin",
            "radii.bin",
            "angles.bin",
            "primary.bin",
            "first_scatter.bin",
            "second_scatter.bin",
            "multiple_scatter.bin",
            "brem_annih.bin",
        ]

        missing_base_files = [
            filename
            for filename in required_base_files
            if not (
                base_folder / filename
            ).exists()
        ]

        if missing_base_files:

            QMessageBox.warning(
                self,
                "Incomplete Base Kernel",
                "The selected base kernel is "
                "missing required files:\n\n"
                + "\n".join(
                    missing_base_files
                ),
            )

            return

        # ----------------------------------------------------
        # GUI STATE
        # ----------------------------------------------------

        self.build_button.setEnabled(
            False
        )

        self.inspect_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Building OpenTPS 18 MV kernel..."
        )

        QApplication.processEvents()

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        try:

            opentps_kernel_builder.BASE_KERNEL_FOLDER = (
                base_folder
            )

            opentps_kernel_builder.EDK_FOLDER = (
                edk_folder
            )

            opentps_kernel_builder.OUTPUT_FOLDER = (
                output_folder
            )

            opentps_kernel_builder.build_opentps_18mv_kernel()

            self.status_label.setText(
                "Kernel build complete.\n\n"
                f"Output:\n{output_folder}"
            )

            QMessageBox.information(
                self,
                "Kernel Build Complete",
                "OpenTPS-compatible 18 MV kernel "
                "folder created successfully.\n\n"
                f"{output_folder}",
            )

        except Exception as error:

            self.status_label.setText(
                "Kernel build failed."
            )

            QMessageBox.critical(
                self,
                "Kernel Build Error",
                str(error),
            )

        finally:

            self.inspect_button.setEnabled(
                True
            )

            self.inspect_edk_folder()

            # Keep validation available if a kernel was built
            if (
                output_folder
                / "kernel_header.txt"
            ).exists():

                self.validate_button.setEnabled(
                    True
                )
    # ========================================================
    # VALIDATE KERNEL
    # ========================================================

    def validate_kernel(self):

        output_folder = Path(
            self.output_folder_edit.text()
        )

        if not output_folder.exists():

            QMessageBox.warning(
                self,
                "Kernel Not Found",
                "The output kernel folder does not exist:\n\n"
                f"{output_folder}",
            )

            return

        self.validate_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Validating OpenTPS kernel..."
        )

        QApplication.processEvents()

        try:

            opentps_kernel_validator.KERNEL_FOLDER = (
                output_folder
            )

            opentps_kernel_validator.validate_kernel_folder(
                output_folder
            )

            # -----------------------------------------------
            # HEADER CHECK
            # -----------------------------------------------

            header_path = (
                output_folder
                / "kernel_header.txt"
            )

            if not header_path.exists():

                raise ValueError(
                    "kernel_header.txt is missing."
                )

            header_lines = (
                header_path
                .read_text(
                    encoding="utf-8"
                )
                .strip()
                .splitlines()
            )

            if len(header_lines) < 2:

                raise ValueError(
                    "kernel_header.txt is invalid."
                )

            dimensions = (
                header_lines[1]
                .split()
            )

            if dimensions != [
                "24",
                "48",
                "19",
            ]:

                raise ValueError(
                    "Kernel header dimensions are incorrect.\n\n"
                    f"Found: {' '.join(dimensions)}\n"
                    "Expected: 24 48 19"
                )

            # -----------------------------------------------
            # SUCCESS
            # -----------------------------------------------

            self.validate_button.setEnabled(
                True
            )

            self.compare_button.setEnabled(
                True
            )

            QMessageBox.information(
                self,
                "Kernel Validation Passed",
                "OpenTPS kernel structure "
                "validated successfully.\n\n"
                "Energy bins: 19\n"
                "Radial bins: 24\n"
                "Angular bins: 48\n"
                "Header: 24 48 19",
            )

        except Exception as error:

            self.status_label.setText(
                "Kernel validation failed."
            )

            QMessageBox.critical(
                self,
                "Kernel Validation Error",
                str(error),
            )

        finally:

            self.validate_button.setEnabled(
                True
            )

# ========================================================
# COMPARE WITH INSTALLED KERNEL
# ========================================================

    def compare_kernel(self):

        generated_folder = Path(
            self.output_folder_edit.text()
        )

        installed_folder = Path(
            r"C:\Users\Yifen\opentps\OpenTPS_venv"
            r"\Lib\site-packages\opentps\core"
            r"\processing\doseCalculation\photons"
            r"\Kernels_18MV"
        )

        if not generated_folder.exists():

            QMessageBox.warning(
                self,
                "Kernel Not Found",
                "The generated kernel folder does not exist:\n\n"
                f"{generated_folder}",
            )

            return

        self.compare_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Comparing with installed 18 MV kernel..."
        )

        QApplication.processEvents()

        try:

            results, overall_pass = (
                kernel_comparator.compare_kernel_folders(
                    installed_folder,
                    generated_folder,
                )
            )

            lines = []

            for file_name, result in results.items():

                status = result["status"]

                if status == "IDENTICAL":
                    symbol = "✓"

                elif status == "EQUIVALENT":
                    symbol = "≈"

                else:
                    symbol = "✗"

                max_diff = result.get(
                    "max_abs_diff"
                )

                if (
                    status == "EQUIVALENT"
                    and max_diff is not None
                ):
                    line = (
                        f"{symbol} {file_name}: "
                        f"{status} "
                        f"(max diff "
                        f"{max_diff:.2e})"
                    )

                else:
                    line = (
                        f"{symbol} {file_name}: "
                        f"{status}"
                    )

                lines.append(line)

            report = "\n".join(lines)

            if overall_pass:

                self.status_label.setText(
                    "Kernel comparison passed."
                )

                QMessageBox.information(
                    self,
                    "Kernel Comparison Passed",
                    report
                    + "\n\n"
                    + "RESULT: COMPARISON PASSED",
                )

            else:

                self.status_label.setText(
                    "Kernel comparison failed."
                )

                QMessageBox.warning(
                    self,
                    "Kernel Comparison Failed",
                    report
                    + "\n\n"
                    + "RESULT: COMPARISON FAILED",
                )

        except Exception as error:

            self.status_label.setText(
                "Kernel comparison failed."
            )

            QMessageBox.critical(
                self,
                "Kernel Comparison Error",
                str(error),
            )

        finally:

            self.compare_button.setEnabled(
                True
            )

# ============================================================
# STANDALONE TEST
# ============================================================

def run():

    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(
        sys.argv
    )

    window = KernelBuilderWidget()

    window.resize(
        850,
        550,
    )

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    run()