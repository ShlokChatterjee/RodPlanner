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
