from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from rodplanner.geometry.coverage import covered_mask

from .models import Rod


def coverage_fraction(
    rods: list[Rod],
    sample_points: NDArray[np.float64],
) -> float:
    """
    Fraction of sample points covered by at least one rod (0.0 – 1.0).

    Returns 1.0 for an empty sample set (vacuously fully covered).
    Returns 0.0 when no rods are placed.
    """
    if len(sample_points) == 0:
        return 1.0
    if not rods:
        return 0.0

    covered = np.zeros(len(sample_points), dtype=bool)
    for rod in rods:
        covered |= covered_mask((rod.x, rod.y), rod.radius, sample_points)

    return float(covered.sum()) / len(sample_points)
