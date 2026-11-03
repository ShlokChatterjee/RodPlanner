from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionParams:
    """Parameters for the classical-OpenCV footprint extractor."""

    pixels_per_metre: float = 10.0  # scale: how many pixels represent one metre
    blur_kernel: int = 5            # Gaussian blur kernel size (must be odd)
    morph_kernel: int = 5           # morphological close kernel size
    contour_epsilon: float = 3.0    # Douglas-Peucker simplification tolerance (pixels)
    invert: bool = False            # True when building is light on a dark background
