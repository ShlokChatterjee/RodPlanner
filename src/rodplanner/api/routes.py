from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from .models import AnalyseParams, AnalyseResponse
from .pipeline import params_from_api, run_pipeline

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyse", response_model=AnalyseResponse)
async def analyse(
    image: UploadFile = File(..., description="Floor plan image (PNG or JPG)"),
    params: AnalyseParams = Depends(),
) -> AnalyseResponse:
    """
    Extract the building footprint from a floor plan image and compute
    lightning rod positions that achieve full roof coverage.
    """
    raw = await image.read()
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise HTTPException(
            status_code=422,
            detail="Could not decode image — is it a valid PNG or JPG?",
        )

    try:
        result = run_pipeline(img, params_from_api(params))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return result
