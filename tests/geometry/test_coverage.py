import math

import numpy as np
import pytest

from rodplanner.geometry.coverage import cone_radius, covered_mask

# ── cone_radius ───────────────────────────────────────────────────────────────

def test_cone_radius_45_deg() -> None:
    # tan(45°) = 1.0, so radius should equal height
    assert cone_radius(5.0, protection_angle_deg=45.0) == pytest.approx(5.0)


def test_cone_radius_60_deg() -> None:
    expected = 5.0 * math.tan(math.radians(60))
    assert cone_radius(5.0, protection_angle_deg=60.0) == pytest.approx(expected)


def test_cone_radius_default_angle_is_45() -> None:
    assert cone_radius(3.0) == pytest.approx(3.0)


def test_cone_radius_rejects_nonpositive_height() -> None:
    with pytest.raises(ValueError):
        cone_radius(0.0)


def test_cone_radius_rejects_bad_angle() -> None:
    with pytest.raises(ValueError):
        cone_radius(5.0, protection_angle_deg=90.0)


# ── covered_mask ──────────────────────────────────────────────────────────────

def _pts(*pairs: tuple[float, float]) -> np.ndarray:
    return np.array(pairs, dtype=np.float64)


def test_point_at_rod_base_is_covered() -> None:
    pts = _pts((5.0, 5.0))
    assert covered_mask((5.0, 5.0), radius=3.0, sample_points=pts)[0]


def test_point_outside_radius_not_covered() -> None:
    pts = _pts((5.0, 9.1))  # distance = 4.1 > 3.0
    assert not covered_mask((5.0, 5.0), radius=3.0, sample_points=pts)[0]


def test_point_exactly_on_boundary_is_covered() -> None:
    pts = _pts((5.0, 8.0))  # distance = 3.0 exactly
    assert covered_mask((5.0, 5.0), radius=3.0, sample_points=pts)[0]


def test_mixed_points() -> None:
    pts = _pts(
        (5.0, 5.0),   # at rod base — covered
        (7.0, 7.0),   # distance ≈ 2.83 < 3 — covered
        (5.0, 9.0),   # distance = 4.0 > 3 — not covered
    )
    mask = covered_mask((5.0, 5.0), radius=3.0, sample_points=pts)
    assert mask.tolist() == [True, True, False]


def test_output_is_bool_array() -> None:
    pts = _pts((0.0, 0.0), (1.0, 1.0))
    mask = covered_mask((0.0, 0.0), radius=2.0, sample_points=pts)
    assert mask.dtype == np.bool_
    assert mask.shape == (2,)


def test_invalid_sample_points_shape() -> None:
    bad = np.array([1.0, 2.0, 3.0])  # 1-D, not (N, 2)
    with pytest.raises(ValueError):
        covered_mask((0.0, 0.0), radius=1.0, sample_points=bad)
