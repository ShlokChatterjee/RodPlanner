# ADR 0002 — Tooling choices

**Status:** Accepted  
**Date:** 2026-11-02

## Context

Three recurring tasks need tooling: formatting/linting, testing, and static
type checking.

### Linting and formatting

| Option | What it does | Speed |
|--------|-------------|-------|
| flake8 + black + isort | three separate tools, each does one job | slower (three passes) |
| ruff | replaces all three, written in Rust | ~10–100× faster |

Ruff is now the default in most new Python projects. It supports the same
rule sets as flake8 and the same formatting as black.

### Testing

pytest is the industry standard. `unittest` (built-in) is more verbose and
offers no practical benefit here.

### Static typing

mypy checks type annotations without running the code. `strict = true` in
mypy turns on every check — good to establish early because retrofitting types
onto untyped code is painful.

## Decision

- **ruff** for lint and formatting (replaces flake8, black, isort)  
- **pytest** for tests  
- **mypy** (strict) for type checking

All three are configured in `pyproject.toml` so there is one config file to
read and one place to change settings.

## Consequences

- A single `pyproject.toml` section configures the whole toolchain.
- `ruff check .` lints; `ruff format .` formats. Both run fast enough to use
  as a pre-commit check.
- mypy strict means every function needs type annotations from the start.
  This slows first-draft writing slightly but prevents a whole class of bugs.
