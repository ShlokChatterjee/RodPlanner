from __future__ import annotations

import numpy as np
import shapely
from numpy.typing import NDArray
from shapely.geometry import Polygon


def sample_grid(polygon: Polygon, resolution: float = 1.0) -> NDArray[np.float64]:
    """
    Return an (N, 2) array of points that lie strictly inside the polygon.

    resolution: spacing between grid points in the same units as the polygon
                (metres). Smaller = denser = more accurate coverage checks,
                but more memory and compute.
    """
    if resolution <= 0:
        raise ValueError(f"resolution must be positive, got {resolution}")

    minx, miny, maxx, maxy = polygon.bounds
    xs = np.arange(minx + resolution / 2, maxx, resolution)
    ys = np.arange(miny + resolution / 2, maxy, resolution)

    # Build every combination of (x, y) — meshgrid then flatten
    xx, yy = np.meshgrid(xs, ys)
    flat_x = xx.ravel()
    flat_y = yy.ravel()

    # Vectorised containment: one C-level call instead of N Python calls
    mask = shapely.contains_xy(polygon, flat_x, flat_y)

    return np.column_stack([flat_x[mask], flat_y[mask]])
