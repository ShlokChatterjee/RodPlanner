from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Polygon

from rodplanner.geometry.polygon import make_polygon

from .models import VisionParams


def extract_footprint(
    image: NDArray[np.uint8],
    params: VisionParams = VisionParams(),
) -> Polygon:
    """
    Extract the largest building footprint polygon from an image array.

    Accepts a grayscale (H, W) or BGR colour (H, W, 3) uint8 image.
    Returns a Shapely Polygon with coordinates in metres.

    Note: pixel y-axis points down (image convention). The placement
    algorithm is orientation-agnostic, so no y-flip is applied in v1.
    """
    if params.blur_kernel % 2 == 0:
        raise ValueError(
            f"blur_kernel must be odd, got {params.blur_kernel}"
        )

    # ── 1. Grayscale ──────────────────────────────────────────────────────────
    gray: NDArray[np.uint8]
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # ── 2. Gaussian blur (reduces noise before thresholding) ──────────────────
    blurred = cv2.GaussianBlur(
        gray, (params.blur_kernel, params.blur_kernel), sigmaX=0
    )

    # ── 3. Otsu threshold ─────────────────────────────────────────────────────
    # THRESH_OTSU picks the optimal split automatically from the histogram.
    # THRESH_BINARY_INV makes dark pixels (building) white in the output so
    # OpenCV's findContours can detect them.
    otsu_flags = cv2.THRESH_BINARY + cv2.THRESH_OTSU
    if not params.invert:
        otsu_flags = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    _, binary = cv2.threshold(blurred, 0, 255, otsu_flags)

    # ── 4. Morphological close (fill gaps in walls / doorways) ────────────────
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (params.morph_kernel, params.morph_kernel)
    )
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # ── 5. Find external contours ─────────────────────────────────────────────
    # RETR_EXTERNAL: outermost contours only (skip rooms, furniture, etc.)
    # CHAIN_APPROX_SIMPLE: store only endpoints of straight segments
    contours, _ = cv2.findContours(
        closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        raise ValueError("No contours found — is the image blank or fully uniform?")

    # ── 6. Largest contour = building outline ─────────────────────────────────
    largest = max(contours, key=cv2.contourArea)

    # ── 7. Douglas-Peucker simplification ────────────────────────────────────
    approx = cv2.approxPolyDP(largest, epsilon=params.contour_epsilon, closed=True)
    pts_px = approx.reshape(-1, 2).astype(np.float64)

    # ── 8. Pixel → metres ─────────────────────────────────────────────────────
    pts_m = pts_px / params.pixels_per_metre
    coords = [(float(x), float(y)) for x, y in pts_m]

    return make_polygon(coords)


def load_and_extract(
    path: str | Path,
    params: VisionParams = VisionParams(),
) -> Polygon:
    """Load an image from disk and extract its building footprint."""
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return extract_footprint(img, params)
