import pytest

from rodplanner.geometry.polygon import make_polygon
from rodplanner.geometry.sampling import sample_grid

SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
L_SHAPE = [(0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (5.0, 5.0), (5.0, 10.0), (0.0, 10.0)]


def test_all_points_inside_square() -> None:
    poly = make_polygon(SQUARE)
    pts = sample_grid(poly, resolution=1.0)
    assert pts.shape[1] == 2
    for x, y in pts:
        assert poly.contains(poly.__class__([(x, y), (x, y), (x, y)])) or poly.covers(
            __import__("shapely.geometry", fromlist=["Point"]).Point(x, y)
        )


def test_point_count_square() -> None:
    # 10×10 at resolution=1.0 → cell centres at 0.5, 1.5, …, 9.5 → 10×10 = 100
    poly = make_polygon(SQUARE)
    pts = sample_grid(poly, resolution=1.0)
    assert len(pts) == 100


def test_point_count_l_shape() -> None:
    # area=75, resolution=1.0 → expect 75 cell centres inside
    poly = make_polygon(L_SHAPE)
    pts = sample_grid(poly, resolution=1.0)
    assert len(pts) == 75


def test_finer_resolution_gives_more_points() -> None:
    poly = make_polygon(SQUARE)
    coarse = sample_grid(poly, resolution=2.0)
    fine = sample_grid(poly, resolution=0.5)
    assert len(fine) > len(coarse)


def test_output_shape() -> None:
    poly = make_polygon(SQUARE)
    pts = sample_grid(poly, resolution=1.0)
    assert pts.ndim == 2
    assert pts.shape[1] == 2


def test_invalid_resolution_raises() -> None:
    poly = make_polygon(SQUARE)
    with pytest.raises(ValueError):
        sample_grid(poly, resolution=0.0)
