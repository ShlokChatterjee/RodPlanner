from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rod:
    """A placed lightning rod on the roof surface."""

    x: float
    y: float
    height: float   # metres above the roof surface
    radius: float   # protection radius derived from height and angle


@dataclass(frozen=True)
class PlacementParams:
    """Parameters that control how rods are placed."""

    height: float = 3.0                 # rod height in metres
    protection_angle_deg: float = 45.0  # cone half-angle; 45° → radius = height
    sample_resolution: float = 1.0      # metres between coverage sample points
    candidate_spacing: float = 1.0      # metres between candidate rod positions
