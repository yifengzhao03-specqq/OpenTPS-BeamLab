from pathlib import Path

import numpy as np

from beamlab.kernel.edk_reader import read_edk_file


COMPONENT_NAMES = (
    "Primary",
    "First Scatter",
    "Second Scatter",
    "Multiple Scatter",
    "Bremsstrahlung + Annihilation",
)


def inspect_components(file_path):
    """
    Inspect the five EDKnrc kernel components.

    Returns the total contribution and fractional contribution
    of each component.
    """

    kernel, uncertainty = read_edk_file(file_path)

    component_totals = np.sum(
        kernel,
        axis=(1, 2),
    )

    total_kernel = float(
        np.sum(component_totals)
    )

    if total_kernel == 0:
        raise ValueError(
            "Kernel total is zero."
        )

    component_fractions = (
        component_totals / total_kernel
    )

    results = []

    for index, name in enumerate(COMPONENT_NAMES):

        results.append(
            {
                "index": index,
                "name": name,
                "total": float(component_totals[index]),
                "fraction": float(component_fractions[index]),
                "percent": float(component_fractions[index] * 100.0),
            }
        )

    return {
        "file": str(Path(file_path)),
        "shape": kernel.shape,
        "total": total_kernel,
        "components": results,
    }


def print_component_report(file_path):

    report = inspect_components(file_path)

    print()
    print("OpenTPS BeamLab — EDK Component Inspector")
    print("=" * 60)

    print(f"File:  {report['file']}")
    print(f"Shape: {report['shape']}")
    print(f"Total: {report['total']:.9f}")

    print()
    print("Component contributions")
    print("-" * 60)

    for component in report["components"]:

        print(
            f"{component['index']}  "
            f"{component['name']:<30} "
            f"{component['total']:.9f}   "
            f"{component['percent']:8.3f}%"
        )

    print("-" * 60)

    percent_sum = sum(
        component["percent"]
        for component in report["components"]
    )

    print(
        f"Component percentage sum: {percent_sum:.3f}%"
    )


if __name__ == "__main__":

    test_file = (
        r"C:\EGSnrc\egs_home\edknrc"
        r"\8MeV_MVgrid.keV"
    )

    print_component_report(
        test_file
    )