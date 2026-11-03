import numpy as np
import pytest

from rodplanner.api.models import AnalyseParams
from rodplanner.api.pipeline import PipelineParams, params_from_api, run_pipeline


def _rect_image(h: int = 100, w: int = 100) -> np.ndarray:
    img = np.full((h, w), 255, dtype=np.uint8)
    img[10:90, 10:90] = 0
    return img


# ── run_pipeline ──────────────────────────────────────────────────────────────

def test_run_pipeline_returns_response() -> None:
    from rodplanner.api.models import AnalyseResponse
    result = run_pipeline(_rect_image(), PipelineParams())
    assert isinstance(result, AnalyseResponse)


def test_run_pipeline_full_coverage() -> None:
    result = run_pipeline(_rect_image(), PipelineParams())
    assert result.coverage_fraction == pytest.approx(1.0)


def test_run_pipeline_rod_count_positive() -> None:
    result = run_pipeline(_rect_image(), PipelineParams())
    assert result.rod_count > 0
    assert len(result.rods) == result.rod_count


def test_run_pipeline_polygon_is_list_of_pairs() -> None:
    result = run_pipeline(_rect_image(), PipelineParams())
    assert all(len(pt) == 2 for pt in result.polygon)


def test_run_pipeline_area_positive() -> None:
    result = run_pipeline(_rect_image(), PipelineParams())
    assert result.area_m2 > 0


def test_blank_image_raises_value_error() -> None:
    blank = np.full((100, 100), 255, dtype=np.uint8)
    with pytest.raises(ValueError):
        run_pipeline(blank, PipelineParams())


# ── params_from_api ───────────────────────────────────────────────────────────

def test_params_from_api_maps_height() -> None:
    api = AnalyseParams(height=5.0)
    pp = params_from_api(api)
    assert pp.placement.height == pytest.approx(5.0)


def test_params_from_api_maps_scale() -> None:
    api = AnalyseParams(pixels_per_metre=20.0)
    pp = params_from_api(api)
    assert pp.vision.pixels_per_metre == pytest.approx(20.0)
