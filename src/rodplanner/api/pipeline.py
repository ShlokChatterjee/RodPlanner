from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from rodplanner.geometry.sampling import sample_grid
from rodplanner.placement.greedy import place_rods
from rodplanner.placement.metrics import coverage_fraction
from rodplanner.placement.models import PlacementParams
from rodplanner.vision.extractor import extract_footprint
from rodplanner.vision.models import VisionParams

from .models import AnalyseParams, AnalyseResponse, RodOut


@dataclass(frozen=True)
class PipelineParams:
    vision: VisionParams = field(default_factory=VisionParams)
    placement: PlacementParams = field(default_factory=PlacementParams)


def run_pipeline(
    image: NDArray[np.uint8],
    params: PipelineParams,
) -> AnalyseResponse:
    """
    Full pipeline: image array → AnalyseResponse.

    Raises ValueError for domain errors (blank image, invalid polygon, etc.)
    so the caller (route handler) can convert them to HTTP 422 responses.
    """
    polygon = extract_footprint(image, params.vision)
    rods = place_rods(polygon, params.placement)
    sample_pts = sample_grid(polygon, params.placement.sample_resolution)
    frac = coverage_fraction(rods, sample_pts)

    polygon_coords = [
        [float(x), float(y)] for x, y in polygon.exterior.coords[:-1]
    ]
    rod_list = [RodOut(x=r.x, y=r.y, height=r.height, radius=r.radius) for r in rods]

    return AnalyseResponse(
        polygon=polygon_coords,
        rods=rod_list,
        coverage_fraction=round(frac, 4),
        rod_count=len(rods),
        area_m2=round(polygon.area, 2),
    )


def params_from_api(api: AnalyseParams) -> PipelineParams:
    """Convert API-level params to internal PipelineParams."""
    return PipelineParams(
        vision=VisionParams(pixels_per_metre=api.pixels_per_metre),
        placement=PlacementParams(
            height=api.height,
            protection_angle_deg=api.protection_angle_deg,
            sample_resolution=api.sample_resolution,
        ),
    )
