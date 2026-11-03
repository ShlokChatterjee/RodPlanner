import numpy as np
import pytest

from rodplanner.placement.metrics import coverage_fraction
from rodplanner.placement.models import Rod

# A simple (N, 2) sample grid for testing
POINTS = np.array([
    [0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
    [0.0, 1.0], [1.0, 1.0], [2.0, 1.0],
], dtype=np.float64)


def _rod(x: float, y: float, radius: float) -> Rod:
    return Rod(x=x, y=y, height=radius, radius=radius)


def test_no_rods_gives_zero() -> None:
    assert coverage_fraction([], POINTS) == pytest.approx(0.0)


def test_empty_points_gives_one() -> None:
    empty = np.empty((0, 2), dtype=np.float64)
    assert coverage_fraction([_rod(0.0, 0.0, 10.0)], empty) == pytest.approx(1.0)


def test_one_rod_covers_all() -> None:
    # Rod at centre of POINTS with large radius
    rod = _rod(1.0, 0.5, radius=10.0)
    assert coverage_fraction([rod], POINTS) == pytest.approx(1.0)


def test_one_rod_covers_none() -> None:
    # Rod far away
    rod = _rod(100.0, 100.0, radius=1.0)
    assert coverage_fraction([rod], POINTS) == pytest.approx(0.0)


def test_partial_coverage() -> None:
    # Rod only reaches the left column (x=0): 2 of 6 points
    rod = _rod(0.0, 0.5, radius=0.6)
    frac = coverage_fraction([rod], POINTS)
    assert 0.0 < frac < 1.0


def test_two_rods_cover_more_than_one() -> None:
    rod_left = _rod(0.0, 0.5, radius=0.6)
    rod_right = _rod(2.0, 0.5, radius=0.6)
    frac_one = coverage_fraction([rod_left], POINTS)
    frac_two = coverage_fraction([rod_left, rod_right], POINTS)
    assert frac_two >= frac_one
