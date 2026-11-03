from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Polygon

from rodplanner.geometry.coverage import cone_radius, covered_mask
from rodplanner.geometry.polygon import corners
from rodplanner.geometry.sampling import sample_grid

from .models import PlacementParams, Rod


def _candidate_positions(polygon: Polygon, spacing: float) -> NDArray[np.float64]:
    """Interior grid points plus polygon corners as candidate rod positions."""
    interior = sample_grid(polygon, spacing)
    corner_pts = corners(polygon)  # boundary vertices — most exposed spots
    return np.vstack([interior, corner_pts])


def place_rods(polygon: Polygon, params: PlacementParams) -> list[Rod]:
    """
    Greedy set cover: repeatedly place the rod that covers the most
    currently-uncovered sample points until full coverage is achieved.

    Returns the list of placed rods in placement order (largest-gain first).
    """
    radius = cone_radius(params.height, params.protection_angle_deg)
    sample_pts = sample_grid(polygon, params.sample_resolution)
    candidates = _candidate_positions(polygon, params.candidate_spacing)

    if len(sample_pts) == 0:
        return []

    # Precompute coverage matrix — shape (N_candidates, N_sample_pts)
    # coverage[i, j] = True  ↔  candidate i covers sample point j
    coverage: NDArray[np.bool_] = np.stack(
        [covered_mask((float(c[0]), float(c[1])), radius, sample_pts)
         for c in candidates]
    )

    uncovered = np.ones(len(sample_pts), dtype=bool)
    rods: list[Rod] = []

    while uncovered.any():
        # Count uncovered points each candidate would newly protect
        counts = (coverage & uncovered).sum(axis=1)
        best_idx = int(counts.argmax())

        if counts[best_idx] == 0:
            break  # no candidate can reach the remaining points

        cx = float(candidates[best_idx, 0])
        cy = float(candidates[best_idx, 1])
        rods.append(Rod(x=cx, y=cy, height=params.height, radius=radius))
        uncovered &= ~coverage[best_idx]

    return rods
