import pytest
from shapely.geometry import Polygon

from rodplanner.geometry.sampling import sample_grid
from rodplanner.placement.greedy import place_rods
from rodplanner.placement.metrics import coverage_fraction
from rodplanner.placement.models import PlacementParams, Rod

SQUARE_10 = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
L_SHAPE = [(0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (5.0, 5.0), (5.0, 10.0), (0.0, 10.0)]


# ── basic contract ─────────────────────────────────────────────────────────────

def test_returns_list_of_rods() -> None:
    poly = Polygon(SQUARE_10)
    rods = place_rods(poly, PlacementParams())
    assert isinstance(rods, list)
    assert all(isinstance(r, Rod) for r in rods)


def test_rods_have_correct_height_and_radius() -> None:
    poly = Polygon(SQUARE_10)
    params = PlacementParams(height=4.0, protection_angle_deg=45.0)
    rods = place_rods(poly, params)
    for rod in rods:
        assert rod.height == pytest.approx(4.0)
        assert rod.radius == pytest.approx(4.0)   # tan(45°) = 1


def test_one_large_rod_covers_small_polygon() -> None:
    # 4×4 polygon, rod height=20 → radius=20 → one rod covers everything
    poly = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
    params = PlacementParams(height=20.0, sample_resolution=1.0)
    rods = place_rods(poly, params)
    assert len(rods) == 1


# ── full coverage ──────────────────────────────────────────────────────────────

def test_full_coverage_square() -> None:
    poly = Polygon(SQUARE_10)
    params = PlacementParams(height=3.0, sample_resolution=1.0)
    rods = place_rods(poly, params)
    pts = sample_grid(poly, params.sample_resolution)
    assert coverage_fraction(rods, pts) == pytest.approx(1.0)


def test_full_coverage_l_shape() -> None:
    poly = Polygon(L_SHAPE)
    params = PlacementParams(height=3.0, sample_resolution=1.0)
    rods = place_rods(poly, params)
    pts = sample_grid(poly, params.sample_resolution)
    assert coverage_fraction(rods, pts) == pytest.approx(1.0)


# ── edge cases ────────────────────────────────────────────────────────────────

def test_empty_polygon_returns_no_rods() -> None:
    # A polygon too small to contain any sample points
    tiny = Polygon([(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1)])
    rods = place_rods(tiny, PlacementParams(sample_resolution=1.0))
    assert rods == []


def test_fewer_rods_with_taller_rods() -> None:
    poly = Polygon(SQUARE_10)
    short_params = PlacementParams(height=2.0, sample_resolution=1.0)
    tall_params = PlacementParams(height=6.0, sample_resolution=1.0)
    short_rods = place_rods(poly, short_params)
    tall_rods = place_rods(poly, tall_params)
    assert len(tall_rods) <= len(short_rods)
