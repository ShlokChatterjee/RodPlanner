# rodplanner

Automatic lightning rod placement from building plan images.

Takes a floor plan or roof plan (PNG/JPG), detects the building footprint, and
computes where lightning rods should be placed so the entire roof is covered
under the protection-cone model.

## Pipeline

```
plan image → polygon extraction → rod placement → 2D overlay + 3D viewer
```

## Quickstart

```bash
pip install -e ".[dev]"   # one-time setup
pytest                     # run tests
ruff check .               # lint
ruff format .              # format
```

## Status

Work in progress. See `Claude/Context.md` for the full build plan.

## Limitations and disclaimer

**This tool is not a certified lightning protection design system and does not
replace a code-compliance review by a qualified engineer.** It is a learning
project that demonstrates the placement algorithm; outputs should not be used
for real installations without independent verification.

Current scope:
- Flat roofs only
- Single building footprint per image
- Protection-cone model (v1); IEC 62305 rolling-sphere method is a stretch goal
