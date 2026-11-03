# ADR 0001 — Python src layout

**Status:** Accepted  
**Date:** 2026-11-02

## Context

Python packages can be placed two ways:

| Layout | Structure |
|--------|-----------|
| Flat   | `rodplanner/` at the repo root |
| src    | `src/rodplanner/` one level down |

With the flat layout, `import rodplanner` works from the repo root even when
the package is *not* installed, because Python adds the current directory to
`sys.path`. This sounds convenient but hides bugs: code that imports fine
locally can fail in CI or after packaging if the install step is broken.

With the src layout, the package is only importable after `pip install -e .`
(editable install). That step must be done once, but from then on imports
behave identically in development, CI, and production.

## Decision

Use the src layout: `src/rodplanner/`.

## Consequences

- Run `pip install -e ".[dev]"` once after cloning before running tests.
- `pytest` finds tests correctly because the installed package is on `sys.path`.
- Import errors in CI are real errors, not layout accidents.
