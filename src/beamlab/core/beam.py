import numpy as np

from opentps.core.data.plan._planPhotonBeam import PlanPhotonBeam
from opentps.core.data.plan._planPhotonSegment import PlanPhotonSegment


def create_open_field(
    gantry_angle=0.0,
    field_size_mm=150.0,
    weight=1.0,
    isocenter=(0.0, 0.0, 0.0),
    beamlet_spacing_mm=5.0,
):
    """
    Create a square open photon field for OpenTPS.

    Parameters
    ----------
    gantry_angle : float
        Gantry angle in degrees.

    field_size_mm : float
        Square field size in mm.

    weight : float
        Relative beam weight.

    isocenter : tuple
        Isocenter position in mm.

    beamlet_spacing_mm : float
        Beamlet spacing in mm.
    """

    beam = PlanPhotonBeam()
    segment = PlanPhotonSegment()

    half_field = float(field_size_mm) / 2.0

    # --------------------------------------------------------
    # JAWS
    # --------------------------------------------------------

    segment.x_jaw_mm = [
        -half_field,
        half_field,
    ]

    segment.y_jaw_mm = [
        -half_field,
        half_field,
    ]

    # --------------------------------------------------------
    # GEOMETRY
    # --------------------------------------------------------

    segment.isocenterPosition_mm = list(
        map(float, isocenter)
    )

    segment.gantryAngle_degree = float(
        gantry_angle
    )

    segment.couchAngle_degree = 0.0

    segment.beamLimitingDeviceAngle_degree = 0.0

    # --------------------------------------------------------
    # BEAM WEIGHT
    # --------------------------------------------------------

    segment.mu = 100.0 * float(weight)

    # --------------------------------------------------------
    # BEAMLET GRID
    # --------------------------------------------------------

    segment.xBeamletSpacing_mm = float(
        beamlet_spacing_mm
    )

    segment.yBeamletSpacing_mm = float(
        beamlet_spacing_mm
    )

    # --------------------------------------------------------
    # OPEN MLC
    # --------------------------------------------------------

    mlc = []

    for y0 in np.arange(
        -half_field,
        half_field,
        beamlet_spacing_mm,
    ):
        mlc.append(
            [
                y0,
                y0 + beamlet_spacing_mm,
                -half_field,
                half_field,
            ]
        )

    segment.Xmlc_mm = np.asarray(
        mlc,
        dtype=float,
    )

    beam.appendBeamSegment(segment)

    return beam


def create_parallel_opposed(
    field_size_mm=150.0,
    weights=(1.0, 1.0),
    isocenter=(0.0, 0.0, 0.0),
):
    """
    Create parallel-opposed AP/PA photon beams.
    """

    if len(weights) != 2:
        raise ValueError(
            "weights must contain exactly two values: AP and PA."
        )

    ap = create_open_field(
        gantry_angle=0.0,
        field_size_mm=field_size_mm,
        weight=weights[0],
        isocenter=isocenter,
    )

    pa = create_open_field(
        gantry_angle=180.0,
        field_size_mm=field_size_mm,
        weight=weights[1],
        isocenter=isocenter,
    )

    return [ap, pa]


def create_four_field_box(
    field_size_mm=150.0,
    weights=(1.0, 1.0, 1.0, 1.0),
    isocenter=(0.0, 0.0, 0.0),
):
    """
    Create a four-field box:
    AP / Left Lateral / PA / Right Lateral

    Gantry:
    0 / 90 / 180 / 270 degrees
    """

    if len(weights) != 4:
        raise ValueError(
            "weights must contain four values."
        )

    angles = [
        0.0,
        90.0,
        180.0,
        270.0,
    ]

    beams = []

    for angle, weight in zip(
        angles,
        weights,
    ):
        beams.append(
            create_open_field(
                gantry_angle=angle,
                field_size_mm=field_size_mm,
                weight=weight,
                isocenter=isocenter,
            )
        )

    return beams