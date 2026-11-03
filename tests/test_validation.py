"""
Validation suite: every benchmark shape must achieve 100% coverage.

These tests are the automated equivalent of the manual benchmark table in
benchmarks/run.py — they run on every push and catch regressions.
"""
import pytest

from benchmarks.shapes import SHAPES
from rodplanner.geometry.polygon import make_polygon
from rodplanner.geometry.sampling import sample_grid
from rodplanner.placement.greedy import place_rods
from rodplanner.placement.metrics import coverage_fraction
from rodplanner.placement.models import PlacementParams

PARAMS = PlacementParams(height=3.0, protection_angle_deg=45.0, sample_resolution=1.0)


@pytest.mark.parametrize("shape", SHAPES, ids=[s.name for s in SHAPES])
def test_full_coverage(shape) -> None:  # type: ignore[no-untyped-def]
    """Algorithm must cover 100% of sample points for every benchmark shape."""
    polygon = make_polygon(shape.polygon)
    rods = place_rods(polygon, PARAMS)
    sample_pts = sample_grid(polygon, PARAMS.sample_resolution)
    frac = coverage_fraction(rods, sample_pts)
    assert frac == pytest.approx(1.0), (
        f"{shape.name}: coverage {frac:.1%} < 100%  "
        f"({len(rods)} rods placed)"
    )


@pytest.mark.parametrize("shape", SHAPES, ids=[s.name for s in SHAPES])
def test_polygon_area(shape) -> None:  # type: ignore[no-untyped-def]
    """Polygon area matches the expected area defined in the shape spec."""
    polygon = make_polygon(shape.polygon)
    assert polygon.area == pytest.approx(shape.area_m2, rel=0.01)


@pytest.mark.parametrize("shape", SHAPES, ids=[s.name for s in SHAPES])
def test_rods_placed(shape) -> None:  # type: ignore[no-untyped-def]
    """At least one rod must be placed for every non-trivial shape."""
    polygon = make_polygon(shape.polygon)
    rods = place_rods(polygon, PARAMS)
    assert len(rods) > 0
