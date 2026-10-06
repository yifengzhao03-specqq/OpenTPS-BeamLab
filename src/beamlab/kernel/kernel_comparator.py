from pathlib import Path

import numpy as np


BINARY_FILES = [
    "angles.bin",
    "energies.bin",
    "fluence.bin",
    "mu.bin",
    "mu_en.bin",
    "radii.bin",
    "primary.bin",
    "first_scatter.bin",
    "second_scatter.bin",
    "multiple_scatter.bin",
    "brem_annih.bin",
    "total.bin",
]


def compare_binary_file(
    reference_file,
    generated_file,
    rtol=1e-6,
    atol=1e-8,
):
    reference_file = Path(reference_file)
    generated_file = Path(generated_file)

    reference = np.fromfile(
        reference_file,
        dtype=np.float32,
    )

    generated = np.fromfile(
        generated_file,
        dtype=np.float32,
    )

    if reference.shape != generated.shape:
        return {
            "status": "FAIL",
            "exact": False,
            "allclose": False,
            "max_abs_diff": None,
            "mean_abs_diff": None,
            "message": (
                f"Shape mismatch: "
                f"{reference.shape} vs {generated.shape}"
            ),
        }

    difference = np.abs(
        reference - generated
    )

    exact = np.array_equal(
        reference,
        generated,
    )

    allclose = np.allclose(
        reference,
        generated,
        rtol=rtol,
        atol=atol,
    )

    if exact:
        status = "IDENTICAL"
    elif allclose:
        status = "EQUIVALENT"
    else:
        status = "FAIL"

    return {
        "status": status,
        "exact": exact,
        "allclose": allclose,
        "max_abs_diff": float(
            np.max(difference)
        ),
        "mean_abs_diff": float(
            np.mean(difference)
        ),
        "message": "",
    }


def compare_headers(
    reference_folder,
    generated_folder,
):
    reference_header = (
        Path(reference_folder)
        / "kernel_header.txt"
    )

    generated_header = (
        Path(generated_folder)
        / "kernel_header.txt"
    )

    reference_text = (
        reference_header
        .read_text(encoding="utf-8")
        .strip()
    )

    generated_text = (
        generated_header
        .read_text(encoding="utf-8")
        .strip()
    )

    identical = (
        reference_text == generated_text
    )

    return {
        "status": (
            "IDENTICAL"
            if identical
            else "FAIL"
        ),
        "exact": identical,
        "reference": reference_text,
        "generated": generated_text,
    }


def compare_kernel_folders(
    reference_folder,
    generated_folder,
):
    reference_folder = Path(
        reference_folder
    )

    generated_folder = Path(
        generated_folder
    )

    if not reference_folder.exists():
        raise FileNotFoundError(
            f"Reference kernel folder not found:\n"
            f"{reference_folder}"
        )

    if not generated_folder.exists():
        raise FileNotFoundError(
            f"Generated kernel folder not found:\n"
            f"{generated_folder}"
        )

    results = {}

    results["kernel_header.txt"] = (
        compare_headers(
            reference_folder,
            generated_folder,
        )
    )

    for file_name in BINARY_FILES:
        reference_file = (
            reference_folder
            / file_name
        )

        generated_file = (
            generated_folder
            / file_name
        )

        if not reference_file.exists():
            results[file_name] = {
                "status": "FAIL",
                "message": (
                    "Missing reference file"
                ),
            }
            continue

        if not generated_file.exists():
            results[file_name] = {
                "status": "FAIL",
                "message": (
                    "Missing generated file"
                ),
            }
            continue

        results[file_name] = (
            compare_binary_file(
                reference_file,
                generated_file,
            )
        )

    overall_pass = all(
        result["status"]
        in ("IDENTICAL", "EQUIVALENT")
        for result in results.values()
    )

    return results, overall_pass


def print_comparison_report(
    reference_folder,
    generated_folder,
):
    results, overall_pass = (
        compare_kernel_folders(
            reference_folder,
            generated_folder,
        )
    )

    print("=" * 78)
    print(
        "OpenTPS BeamLab — "
        "Kernel Comparison"
    )
    print("=" * 78)

    print()
    print(
        f"Reference: {reference_folder}"
    )
    print(
        f"Generated: {generated_folder}"
    )
    print()

    print(
        f"{'FILE':25s} "
        f"{'STATUS':12s} "
        f"{'MAX ABS DIFF':>15s}"
    )

    print("-" * 58)

    for file_name, result in results.items():

        max_diff = result.get(
            "max_abs_diff"
        )

        if max_diff is None:
            diff_text = "-"
        else:
            diff_text = (
                f"{max_diff:.8e}"
            )

        print(
            f"{file_name:25s} "
            f"{result['status']:12s} "
            f"{diff_text:>15s}"
        )

    print()
    print("=" * 78)

    if overall_pass:
        print(
            "RESULT: KERNEL COMPARISON PASSED"
        )
    else:
        print(
            "RESULT: KERNEL COMPARISON FAILED"
        )

    print("=" * 78)

    return overall_pass


if __name__ == "__main__":

    reference = Path(
        r"C:\Users\Yifen\opentps"
        r"\OpenTPS_venv\Lib\site-packages"
        r"\opentps\core\processing"
        r"\doseCalculation\photons"
        r"\Kernels_18MV"
    )

    generated = Path(
        r"C:\Users\Yifen\opentps"
        r"\OpenTPS-BeamLab\data"
        r"\Kernels_18MV_test"
    )

    print_comparison_report(
        reference,
        generated,
    )