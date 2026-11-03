# Learning log

A running record of checkpoints: what was built, why, what was rejected, and
vocabulary to know. Updated at the end of every checkpoint.

---

## Checkpoint 0 — Project setup and design decisions

**Date:** 2026-11-02

### What we built

| File / folder | Purpose |
|---------------|---------|
| `src/rodplanner/` | The Python package, split into four sub-modules |
| `src/rodplanner/geometry/` | Polygon helpers and coverage sampling (Checkpoint 1) |
| `src/rodplanner/placement/` | Rod placement algorithms (Checkpoint 2) |
| `src/rodplanner/vision/` | Floor plan image processing (Checkpoint 3) |
| `src/rodplanner/api/` | FastAPI endpoints (Checkpoint 4) |
| `tests/` | Mirror of the source tree; one sub-folder per module |
| `pyproject.toml` | Single config file for build, dependencies, and all tools |
| `docs/adr/` | Architecture Decision Records |
| `README.md` | Project overview with the required disclaimer |
| `LEARNING_LOG.md` | This file |

### Key decisions and why

**1. src layout (ADR 0001)**  
The package lives at `src/rodplanner/`, not at the repo root. This forces you
to install the package before importing it, which prevents a whole class of
"it works on my machine" bugs where tests pass because Python is silently
importing the source directory rather than the installed package.

*What we rejected:* flat layout (package at root). Simpler to start, but the
hidden import path is a trap that real teams have been burned by.

**2. pyproject.toml as the single config file**  
`pyproject.toml` is the modern Python standard (PEP 517/518). It replaces
`setup.py`, `setup.cfg`, `.flake8`, `mypy.ini`, and `pytest.ini` with one
file. Less noise, one place to look.

**3. ruff over flake8 + black + isort (ADR 0002)**  
One tool written in Rust that does the job of three. Same rules, much faster,
one config section. In a real team this matters because lint runs in CI on
every push; slow CI is CI people start skipping.

*What we rejected:* flake8 + black + isort. Still common in older codebases,
so it's worth knowing they exist, but for a new project ruff is the default
choice today.

**4. mypy strict**  
Type annotations in Python are optional. Setting `strict = true` in mypy
means the type checker enforces them on every function. This slows initial
writing but catches bugs before tests run and makes code easier to reason
about. It is much harder to add types to an existing codebase than to write
them from the start.

**5. Four separate modules (ADR 0003)**  
Splitting the pipeline into `geometry/`, `placement/`, `vision/`, and `api/`
means each stage can be built and tested independently. Geometry and placement
will be working (Checkpoints 1 and 2) before vision exists (Checkpoint 3).
The 3D viewer (Checkpoint 5) is JavaScript and lives outside this package
entirely.

### Vocabulary to know

| Term | Meaning |
|------|---------|
| **src layout** | Placing your package inside a `src/` folder so it can only be imported after installation |
| **editable install** | `pip install -e .` installs the package so that changes to source files take effect immediately without reinstalling |
| **ADR** | Architecture Decision Record — a short document that freezes a technical decision and the reasoning behind it |
| **pyproject.toml** | The modern single-file Python project config (PEP 517/518) |
| **ruff** | A fast Python linter and formatter written in Rust |
| **mypy** | A static type checker for Python |
| **strict mode (mypy)** | Every function must have type annotations; mypy checks them all |
| **pytest** | The standard Python test runner |
| **conftest.py** | A special pytest file for shared fixtures (setup code that tests can reuse) |

### What to do before Checkpoint 1

```bash
pip install -e ".[dev]"   # install the package and dev tools
pytest                     # should show 1 passed (the smoke test)
ruff check .               # should show no errors
```

---

## Checkpoint 1 — Geometry core

**Date:** 2026-11-02

### What we built

| File | Purpose |
|------|---------|
| `src/rodplanner/geometry/polygon.py` | Create and validate polygons; extract corners |
| `src/rodplanner/geometry/sampling.py` | Fill a polygon with a grid of sample points |
| `src/rodplanner/geometry/coverage.py` | Compute a rod's protection radius; check which sample points it covers |
| `tests/geometry/test_polygon.py` | 8 tests |
| `tests/geometry/test_sampling.py` | 6 tests |
| `tests/geometry/test_coverage.py` | 11 tests |

**Total: 26 tests, all passing. Lint: clean.**

### Key decisions and why

**1. Shapely for polygon math**  
Shapely is the standard Python library for 2D geometry. It handles containment checks,
area computation, boundary sampling, and more. The alternative (writing the geometry from
scratch) would be hundreds of lines of error-prone math. Shapely 2.x added vectorised
operations (e.g. `contains_xy`) that are implemented in C — much faster than calling
Python methods in a loop.

**2. (N, 2) NumPy arrays for point collections**  
All collections of points are represented as NumPy arrays of shape `(N, 2)`, not as
lists of tuples. This lets us do math on all N points at once ("vectorised"). For
example, `dx = sample_points[:, 0] - rod_x` subtracts the rod's x-coordinate from
every point's x in one line, with no for-loop. The alternative (iterating in Python)
is roughly 100× slower on a large roof.

**3. Cell-centred grid sampling**  
We offset the grid by `resolution / 2` so each sample point sits at the centre of a
grid cell, not on the cell boundary. Without this, points on the polygon edges are not
counted as "inside" (Shapely's `contains` is strict), which would under-count coverage
near the walls — exactly where rods matter most.

**4. Squared-distance comparison in coverage check**  
`(dx² + dy²) ≤ radius²` avoids computing a square root. `sqrt` is slow; squaring both
sides gives the same True/False result. This is a standard micro-optimisation in
computational geometry.

**5. Geometry separated from placement**  
`coverage.py` only answers "does one rod cover these points?" It does not decide where
to place rods. That decision lives in `placement/` (Checkpoint 2). The separation means
we can swap the placement algorithm (greedy → rolling sphere) without touching the
coverage math, and we can unit-test the coverage function alone.

### Vocabulary to know

| Term | Meaning |
|------|---------|
| **Shapely Polygon** | A 2D shape defined by a closed ring of (x, y) points |
| **`polygon.bounds`** | The axis-aligned bounding box: `(min_x, min_y, max_x, max_y)` |
| **`polygon.exterior`** | The outer ring of the polygon (as opposed to holes) |
| **Vectorised operation** | A NumPy operation applied to an entire array at once, compiled in C — no Python loop |
| **`(N, 2)` array** | A NumPy array with N rows and 2 columns; each row is one (x, y) point |
| **Boolean mask** | A NumPy array of `True`/`False` values used to select elements from another array |
| **Cell-centred sampling** | Placing grid points at cell centres (offset by half the spacing) so none fall exactly on boundaries |
| **`pytest.approx`** | A pytest helper for comparing floating-point numbers with a small tolerance |
| **Protection cone model** | A rod at height h protects a circle of radius r = h × tan(α) on the roof surface |

---

## Checkpoint 2 — Placement algorithm (greedy set cover)

**Date:** 2026-11-02

### What we built

| File | Purpose |
|------|---------|
| `src/rodplanner/placement/models.py` | `Rod` and `PlacementParams` dataclasses |
| `src/rodplanner/placement/greedy.py` | `place_rods()` — greedy set cover algorithm |
| `src/rodplanner/placement/metrics.py` | `coverage_fraction()` — measures how well rods cover the roof |
| `tests/placement/test_greedy.py` | 7 tests |
| `tests/placement/test_metrics.py` | 6 tests |

**Total: 39 tests passing. Lint: clean.**

### Key decisions and why

**1. Greedy set cover (not optimal, but good enough)**
At each step: place the rod that covers the most currently-uncovered points.
Repeat until everything is covered. Greedy set cover is guaranteed to achieve
full coverage and runs fast. It may use ~63% more rods than the theoretical minimum
in the worst case, but in practice on building roofs it is close to optimal.

*What we rejected:*
- **ILP (Integer Linear Programming)**: finds the true minimum rod count, but requires
  a solver library and is much slower. Overkill for v1.
- **Random/Monte Carlo**: non-deterministic — two runs on the same roof give different
  results. Bad for a reproducible design tool.

**2. Precomputed coverage matrix**
We compute the full `(N_candidates x N_points)` boolean grid once before the loop.
Each greedy iteration then only sums a row (fast) instead of recomputing distances
for every candidate on every step. Trade-off: more memory upfront. For a 50x50m roof
at 1m resolution: ~2500 x 2500 = ~6MB — acceptable for v1.

**3. Corners as explicit candidates**
Polygon corner vertices are added to the candidate list alongside the interior grid.
This ensures a rod can be placed exactly at a corner, the most exposed point on the
building outline.

**4. Frozen dataclasses**
`@dataclass(frozen=True)` makes `Rod` and `PlacementParams` immutable after creation.
Right for result data that should not change. Also makes them hashable (usable in
sets and as dict keys).

**5. `coverage_fraction` separate from placement**
Measuring how well rods cover the roof is a distinct concern from placing them.
Keeping it in `metrics.py` means we can validate hand-placed layouts (Checkpoint 6)
without touching the placement algorithm.

### Vocabulary to know

| Term | Meaning |
|------|---------|
| **Set cover** | Find the fewest sets whose union covers all elements |
| **Greedy algorithm** | Makes the locally best choice at each step; fast but not always globally optimal |
| **Coverage matrix** | 2D boolean array: `[i, j] = True` means candidate i covers sample point j |
| **ILP** | Integer Linear Programming — mathematically optimal but computationally expensive |
| **Frozen dataclass** | Python dataclass where all fields are read-only after creation (`frozen=True`) |
| **`coverage_fraction`** | Fraction of roof sample points protected by at least one rod (0.0-1.0) |

---

## Checkpoint 3 — Vision pipeline (classical OpenCV)

**Date:** 2026-11-02

### What we built

| File | Purpose |
|------|---------|
| `src/rodplanner/vision/models.py` | `VisionParams` frozen dataclass |
| `src/rodplanner/vision/extractor.py` | `extract_footprint()` and `load_and_extract()` |
| `tests/vision/test_extractor.py` | 8 tests using synthetic in-memory images |

**Total: 47 tests passing. Lint: clean.**

### The pipeline

```
image (grayscale or BGR)
  → grayscale conversion
  → Gaussian blur          (reduce noise)
  → Otsu threshold         (auto binarise: building=white, background=black)
  → morphological close    (fill wall gaps / doorways)
  → find external contours (outermost shapes only)
  → largest contour        (= building outline)
  → Douglas-Peucker        (simplify jagged pixel boundary to clean polygon)
  → scale pixels → metres
  → Shapely Polygon
```

### Key decisions and why

**1. Otsu's threshold over a fixed value**
Otsu automatically finds the best threshold by analysing the image's pixel
intensity histogram. A fixed value (e.g. 127) would fail on dim scans,
high-contrast plans, or images with different lighting. Otsu works on any image
where the building and background form two distinct peaks in the histogram.

**2. Morphological close**
`cv2.MORPH_CLOSE` is a dilation followed by an erosion. It fills small dark
gaps (doorways, scan artefacts) in the bright wall boundaries. Without it, a
wall with a gap splits into two separate contours and the algorithm may pick
the wrong one as the building outline.

**3. Douglas-Peucker simplification**
The raw pixel contour has hundreds of vertices — one per boundary pixel. The
algorithm reduces these to the fewest vertices that stay within `epsilon`
pixels of the original curve. This converts a jagged digital boundary into a
clean polygon suitable for the geometry/placement modules.

*What we rejected:*
- **Canny edge detection + Hough lines**: good for finding straight walls but
  requires assembling detected line segments back into a closed polygon, which
  is fragile for irregular shapes.
- **Neural segmentation model (CubiCasa5K)**: more accurate on messy real-world
  plans but requires a trained model, GPU inference, and dataset licensing.
  Planned as a future upgrade; classical CV is sufficient for clean plans.

**4. Tests use synthetic in-memory images**
We draw rectangles and L-shapes directly as NumPy arrays instead of loading
image files. No binary files in the repo, no file I/O in tests, fast execution.

### Vocabulary to know

| Term | Meaning |
|------|---------|
| **Grayscale** | Single-channel image where each pixel is a brightness value (0-255) |
| **BGR** | OpenCV's default colour format: Blue-Green-Red (not RGB) |
| **Otsu's threshold** | Algorithm that automatically finds the best binary threshold from the pixel histogram |
| **Morphological close** | Dilation then erosion: fills small holes and gaps in a binary image |
| **Contour** | A curve joining all continuous points of the same intensity boundary in a binary image |
| **`RETR_EXTERNAL`** | Find only outermost contours (skips internal shapes like rooms) |
| **Douglas-Peucker** | Algorithm that simplifies a polyline to fewer points within a tolerance |
| **`pixels_per_metre`** | Scale factor: how many image pixels represent one real-world metre |

---

## Checkpoint 4 — API layer (FastAPI)

**Date:** 2026-11-02

### What we built

| File | Purpose |
|------|---------|
| `src/rodplanner/api/models.py` | Pydantic request/response models (`RodOut`, `AnalyseResponse`, `AnalyseParams`) |
| `src/rodplanner/api/pipeline.py` | `run_pipeline()` — orchestrates all four modules end-to-end |
| `src/rodplanner/api/routes.py` | FastAPI router: `GET /health`, `POST /analyse` |
| `src/rodplanner/api/app.py` | FastAPI app creation |
| `tests/api/test_pipeline.py` | 8 unit tests for the pipeline function |
| `tests/api/test_routes.py` | 8 HTTP integration tests via TestClient |

**Total: 63 tests passing. Lint: clean.**

### How the full pipeline flows

```
POST /analyse (image file + params)
  → decode image bytes → NumPy array (cv2.imdecode)
  → extract_footprint()     [vision]
  → place_rods()            [placement]
  → sample_grid()           [geometry]
  → coverage_fraction()     [placement/metrics]
  → AnalyseResponse (JSON)
```

For the first time all four modules connect. The API layer owns none of the
domain logic — it wires the modules together and translates between HTTP concepts
(files, form fields, status codes) and domain concepts (images, polygons, rods).

### Key decisions and why

**1. Pydantic for request/response**
`Field(gt=0)` on `height` means FastAPI returns a clear 422 if the caller sends
`height=-1`. Without this, bad input silently propagates and causes a cryptic error
deep inside the geometry code.

*What we rejected:* plain dicts or dataclasses — no automatic JSON serialisation,
no OpenAPI schema, no validation.

**2. `Depends()` for query parameters**
`params: AnalyseParams = Depends()` reads all fields of `AnalyseParams` from the
query string as a unit. The alternative (one `Query()` per field) duplicates the
field definitions in the route signature.

**3. Domain errors → HTTP 422**
`ValueError` from the pipeline is caught in the route and re-raised as
`HTTPException(422)`. The pipeline stays ignorant of HTTP; the route translates.

**4. `python-multipart` as a runtime dependency**
FastAPI needs it to handle file uploads. It belongs in runtime dependencies
(not just dev) because the deployed server needs it, not just the test suite.

**5. TestClient for HTTP tests**
Runs the full FastAPI app in-process — no real server, no ports. Tests send real
HTTP requests and get real JSON at unit-test speed.

### Vocabulary to know

| Term | Meaning |
|------|---------|
| **Pydantic** | Data validation library; powers FastAPI's request/response handling |
| **`BaseModel`** | Pydantic's base class; validates fields automatically on creation |
| **`Field(gt=0)`** | Field constraint: "greater than 0"; enforced at parse time |
| **`UploadFile`** | FastAPI type for file uploads; provides filename, content-type, async `read()` |
| **`Depends()`** | FastAPI dependency injection; validates a group of parameters automatically |
| **`HTTPException`** | FastAPI's way to return HTTP error responses |
| **422 Unprocessable Entity** | HTTP status: "I understood the request but the data is invalid" |
| **TestClient** | Runs FastAPI HTTP requests in-process without a real server |
| **`python-multipart`** | Required for parsing multipart form data (file uploads) in FastAPI |

---
