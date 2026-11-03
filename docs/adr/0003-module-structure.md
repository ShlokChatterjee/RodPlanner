# ADR 0003 — Module structure

**Status:** Accepted  
**Date:** 2026-11-02

## Context

The pipeline has four distinct stages with different dependencies and
different rates of change:

| Stage | Input → Output | Key library |
|-------|---------------|-------------|
| vision | image → polygon | OpenCV |
| geometry | polygon → coverage grid | Shapely |
| placement | coverage grid → rod positions | NumPy |
| api | HTTP request → JSON response | FastAPI |

The question is whether to keep these in one module or split them.

**One module** is simpler to start but couples the stages. Changing the CV
approach (e.g. swapping classical OpenCV for a neural net) would live in the
same file as the geometry math, making diffs noisy and tests harder to isolate.

**Separate modules** add a little boilerplate but let each stage be tested
and replaced independently. It also matches the structure of the pipeline,
so the code layout tells you how the system works.

## Decision

Four sub-packages under `src/rodplanner/`:  
`geometry/`, `placement/`, `vision/`, `api/`

Data flows one way: `vision → geometry → placement → api`. No module imports
from a module further down that chain.

## Consequences

- Each module has its own test directory (`tests/geometry/`, etc.).
- Geometry and placement can be tested with synthetic polygons before the
  vision module exists (Checkpoint 1 runs before Checkpoint 3).
- A future upgrade from classical CV to a segmentation model touches only
  `vision/`; geometry and placement tests stay green.
