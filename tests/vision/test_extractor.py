import numpy as np
import pytest
from shapely.geometry import Polygon

from rodplanner.vision.extractor import extract_footprint
from rodplanner.vision.models import VisionParams

# ── synthetic image helpers ───────────────────────────────────────────────────

def _white(h: int, w: int) -> np.ndarray:
    return np.full((h, w), 255, dtype=np.uint8)


def _rect_image(
    img_h: int, img_w: int,
    r0: int, r1: int, c0: int, c1: int,
) -> np.ndarray:
    """White image with a solid black rectangle from row r0:r1, col c0:c1."""
    img = _white(img_h, img_w)
    img[r0:r1, c0:c1] = 0
    return img


def _l_image() -> np.ndarray:
    """White 100×100 image with a black L-shaped footprint."""
    img = _white(100, 100)
    img[10:90, 10:55] = 0  # left column of the L
    img[10:55, 55:90] = 0  # top-right arm of the L
    return img


# ── basic contract ─────────────────────────────────────────────────────────────

def test_returns_polygon() -> None:
    img = _rect_image(100, 100, 10, 90, 10, 90)
    poly = extract_footprint(img, VisionParams(pixels_per_metre=10.0))
    assert isinstance(poly, Polygon)


def test_rectangle_area_approximately_correct() -> None:
    # Black rect: 80 px × 80 px, scale 10 px/m → 8 m × 8 m = 64 m²
    img = _rect_image(100, 100, 10, 90, 10, 90)
    params = VisionParams(pixels_per_metre=10.0, contour_epsilon=1.0)
    poly = extract_footprint(img, params)
    assert poly.area == pytest.approx(64.0, rel=0.05)


def test_l_shape_is_valid_polygon() -> None:
    poly = extract_footprint(_l_image(), VisionParams(pixels_per_metre=10.0))
    assert poly.is_valid
    assert poly.area > 0


def test_l_shape_area_approximately_correct() -> None:
    # Black L: (80*45 + 45*35) = 5175 px², ÷ 100 = 51.75 m²
    # Non-rectangular shapes have more contour-approximation error than rectangles,
    # so we allow 10% tolerance here.
    poly = extract_footprint(
        _l_image(),
        VisionParams(pixels_per_metre=10.0, contour_epsilon=1.0),
    )
    assert poly.area == pytest.approx(51.75, rel=0.10)


# ── colour image ──────────────────────────────────────────────────────────────

def test_colour_image_accepted() -> None:
    # BGR image built by stacking the grayscale channel three times
    img_gray = _rect_image(100, 100, 10, 90, 10, 90)
    img_bgr = np.stack([img_gray, img_gray, img_gray], axis=-1)
    poly = extract_footprint(img_bgr, VisionParams(pixels_per_metre=10.0))
    assert isinstance(poly, Polygon)


# ── scale parameter ───────────────────────────────────────────────────────────

def test_scale_affects_output_area() -> None:
    img = _rect_image(100, 100, 10, 90, 10, 90)
    p10 = VisionParams(pixels_per_metre=10.0, contour_epsilon=1.0)
    p20 = VisionParams(pixels_per_metre=20.0, contour_epsilon=1.0)
    poly_10 = extract_footprint(img, p10)
    poly_20 = extract_footprint(img, p20)
    # 20 px/m → each pixel is half a metre → area is ¼ of 10 px/m case
    assert poly_20.area == pytest.approx(poly_10.area / 4, rel=0.05)


# ── error cases ───────────────────────────────────────────────────────────────

def test_blank_image_raises() -> None:
    blank = _white(100, 100)  # all white — no dark region to detect
    with pytest.raises(ValueError, match="No contours"):
        extract_footprint(blank, VisionParams())


def test_even_blur_kernel_raises() -> None:
    img = _rect_image(100, 100, 10, 90, 10, 90)
    with pytest.raises(ValueError, match="odd"):
        extract_footprint(img, VisionParams(blur_kernel=4))
