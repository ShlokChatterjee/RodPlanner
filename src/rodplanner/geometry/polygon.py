from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Polygon
from shapely.validation import explain_validity

# A coordinate list: [(x0,y0), (x1,y1), ...]  Units: metres throughout.
Coords = list[tuple[float, float]]


def make_polygon(coords: Coords) -> Polygon:
    """Create a validated Shapely Polygon from a list of (x, y) coordinates."""
    poly = Polygon(coords)
    if poly.is_empty:
        raise ValueError("Polygon is empty (fewer than 3 distinct points?)")
    if not poly.is_valid:
        reason = explain_validity(poly)
        raise ValueError(f"Polygon is not valid (self-intersecting?): {reason}")
    return poly


def corners(poly: Polygon) -> NDArray[np.float64]:
    """Return the corner vertices as an (N, 2) array."""
    # exterior.coords repeats the first point at the end to close the ring; drop it
    return np.array(poly.exterior.coords[:-1], dtype=np.float64)
