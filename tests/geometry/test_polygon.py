import pytest
from shapely.geometry import Polygon

from rodplanner.geometry.polygon import corners, make_polygon

# ── fixtures ──────────────────────────────────────────────────────────────────

SQUARE: list[tuple[float, float]] = [(0, 0), (10, 0), (10, 10), (0, 10)]

L_SHAPE: list[tuple[float, float]] = [
    (0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10)
]

# ── make_polygon ──────────────────────────────────────────────────────────────

def test_make_polygon_returns_polygon() -> None:
    poly = make_polygon(SQUARE)
    assert isinstance(poly, Polygon)


def test_make_polygon_area_square() -> None:
    poly = make_polygon(SQUARE)
    assert poly.area == pytest.approx(100.0)


def test_make_polygon_area_l_shape() -> None:
    # Full 10×10 minus the 5×5 cut-out = 100 - 25 = 75
    poly = make_polygon(L_SHAPE)
    assert poly.area == pytest.approx(75.0)


def test_make_polygon_rejects_self_intersecting() -> None:
    # Bowtie: edges cross each other
    bowtie: list[tuple[float, float]] = [(0, 0), (10, 10), (10, 0), (0, 10)]
    with pytest.raises(ValueError, match="not valid"):
        make_polygon(bowtie)


def test_make_polygon_rejects_empty() -> None:
    with pytest.raises(ValueError, match="empty"):
        make_polygon([])


# ── corners ───────────────────────────────────────────────────────────────────

def test_corners_square_count() -> None:
    poly = make_polygon(SQUARE)
    assert corners(poly).shape == (4, 2)


def test_corners_l_shape_count() -> None:
    poly = make_polygon(L_SHAPE)
    assert corners(poly).shape == (6, 2)


def test_corners_no_duplicate_close_point() -> None:
    # Shapely repeats the first vertex at the end; corners() must strip it
    poly = make_polygon(SQUARE)
    pts = corners(poly)
    assert not (pts[0] == pts[-1]).all(), "first and last corner should differ"
