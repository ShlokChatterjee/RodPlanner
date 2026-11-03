from __future__ import annotations

from pydantic import BaseModel, Field


class RodOut(BaseModel):
    x: float
    y: float
    height: float
    radius: float


class AnalyseResponse(BaseModel):
    polygon: list[list[float]]      # [[x0,y0], [x1,y1], ...]
    rods: list[RodOut]
    coverage_fraction: float
    rod_count: int
    area_m2: float


class AnalyseParams(BaseModel):
    """Query parameters for the /analyse endpoint."""

    height: float = Field(default=3.0, gt=0, description="Rod height in metres")
    protection_angle_deg: float = Field(
        default=45.0, gt=0, lt=90,
        description="Protection cone half-angle in degrees"
    )
    pixels_per_metre: float = Field(
        default=10.0, gt=0,
        description="Image scale: pixels per metre"
    )
    sample_resolution: float = Field(
        default=1.0, gt=0,
        description="Grid spacing for coverage sampling in metres"
    )
