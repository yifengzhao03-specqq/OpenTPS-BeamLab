from pathlib import Path

from beamlab.kernel.edk_inspector import inspect_components


ENERGIES_MEV = [8, 10, 12, 15, 18]

EDK_FOLDER = Path(
    r"C:\EGSnrc\egs_home\edknrc"
)


def compare_edk_components():

    reports = []

    # --------------------------------------------------------
    # READ ALL EDK FILES
    # --------------------------------------------------------

    for energy in ENERGIES_MEV:

        file_path = (
            EDK_FOLDER
            / f"{energy}MeV_MVgrid.keV"
        )

        report = inspect_components(
            file_path
        )

        reports.append(
            (
                energy,
                report,
            )
        )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    print()
    print(
        "OpenTPS BeamLab — EDK Energy Comparison"
    )

    print("=" * 100)

    print(
        f"{'Energy':>8}"
        f"{'Primary':>13}"
        f"{'First':>13}"
        f"{'Second':>13}"
        f"{'Multiple':>13}"
        f"{'Brem+Ann':>13}"
        f"{'Total':>14}"
    )

    print("-" * 100)

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    for energy, report in reports:

        percentages = [
            component["percent"]
            for component in report["components"]
        ]

        print(
            f"{energy:>6} MeV"
            f"{percentages[0]:>12.3f}%"
            f"{percentages[1]:>12.3f}%"
            f"{percentages[2]:>12.3f}%"
            f"{percentages[3]:>12.3f}%"
            f"{percentages[4]:>12.3f}%"
            f"{report['total']:>14.9f}"
        )

    print("-" * 100)

    # --------------------------------------------------------
    # CHECKS
    # --------------------------------------------------------

    print()
    print("Validation")
    print("=" * 100)

    all_valid = True

    for energy, report in reports:

        shape_ok = (
            report["shape"]
            == (5, 24, 48)
        )

        percent_sum = sum(
            component["percent"]
            for component in report["components"]
        )

        percentage_ok = abs(
            percent_sum - 100.0
        ) < 0.001

        status = (
            "PASS"
            if shape_ok and percentage_ok
            else "FAIL"
        )

        if status == "FAIL":
            all_valid = False

        print(
            f"{energy:>2} MeV : "
            f"shape={report['shape']}   "
            f"sum={percent_sum:.3f}%   "
            f"{status}"
        )

    print()

    if all_valid:
        print(
            "RESULT: ALL EDK FILES PASSED STRUCTURAL VALIDATION"
        )
    else:
        print(
            "RESULT: ONE OR MORE EDK FILES FAILED VALIDATION"
        )


if __name__ == "__main__":

    compare_edk_components()