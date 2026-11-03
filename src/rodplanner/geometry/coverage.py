from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray


def cone_radius(height: float, protection_angle_deg: float = 45.0) -> float:
    """Horizontal protection radius at roof level for a rod of given height."""
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}")
    if not (0 < protection_angle_deg < 90):
        raise ValueError(
            f"protection_angle_deg must be in (0, 90), got {protection_angle_deg}"
        )
    return height * math.tan(math.radians(protection_angle_deg))


def covered_mask(
    rod_xy: tuple[float, float],
    radius: float,
    sample_points: NDArray[np.float64],
) -> NDArray[np.bool_]:
    """
    Boolean mask over sample_points: True where the point is within the rod's cone.

    rod_xy:        (x, y) position of the rod base on the roof surface
    radius:        protection radius from cone_radius()
    sample_points: (N, 2) array of points to check
    """
    if radius < 0:
        raise ValueError(f"radius must be non-negative, got {radius}")
    if sample_points.ndim != 2 or sample_points.shape[1] != 2:
        raise ValueError(
            f"sample_points must be (N, 2), got shape {sample_points.shape}"
        )

    dx = sample_points[:, 0] - rod_xy[0]
    dy = sample_points[:, 1] - rod_xy[1]
    # Compare squared distances — avoids sqrt, same result
    return (dx * dx + dy * dy) <= radius * radius
