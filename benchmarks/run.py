"""
rodplanner benchmark runner.

Usage (from repo root, with package installed):
    python benchmarks/run.py

Measures wall-clock time for each pipeline stage across all benchmark shapes
and prints a comparison table.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure the repo root is on sys.path so both
# `python benchmarks/run.py` and `python -m benchmarks.run` work.
sys.path.insert(0, str(Path(__file__).parent.parent))

from rodplanner.geometry.polygon import make_polygon
from rodplanner.geometry.sampling import sample_grid
from rodplanner.placement.greedy import place_rods
from rodplanner.placement.metrics import coverage_fraction
from rodplanner.placement.models import PlacementParams

from benchmarks.shapes import SHAPES

# ── parameters ────────────────────────────────────────────────────────────────

PARAMS = PlacementParams(height=3.0, protection_angle_deg=45.0, sample_resolution=1.0)
MANUAL_HOURS = 2.0  # conservative estimate: manual layout on paper


# ── helpers ───────────────────────────────────────────────────────────────────

def _ms(seconds: float) -> str:
    return f"{seconds * 1000:.1f} ms"


def _run_one(shape_polygon: list[tuple[float, float]]) -> dict[str, object]:
    """Run the full pipeline and return timing + results."""
    t0 = time.perf_counter()

    polygon = make_polygon(shape_polygon)

    t1 = time.perf_counter()
    sample_pts = sample_grid(polygon, PARAMS.sample_resolution)

    t2 = time.perf_counter()
    rods = place_rods(polygon, PARAMS)

    t3 = time.perf_counter()
    frac = coverage_fraction(rods, sample_pts)

    t4 = time.perf_counter()

    return {
        "polygon_ms":   (t1 - t0) * 1000,
        "sample_ms":    (t2 - t1) * 1000,
        "placement_ms": (t3 - t2) * 1000,
        "metrics_ms":   (t4 - t3) * 1000,
        "total_ms":     (t4 - t0) * 1000,
        "rod_count":    len(rods),
        "coverage":     frac,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  rodplanner - placement benchmark")
    print("  " + "-" * 66)
    print(f"  {'shape':<18} {'area':>7}  {'rods':>5}  {'ref':>4}  {'cov':>7}  {'time':>8}")
    print("  " + "-" * 66)

    total_times: list[float] = []

    for shape in SHAPES:
        r = _run_one(shape.polygon)
        total_times.append(r["total_ms"])  # type: ignore[arg-type]

        cov_str = f"{r['coverage'] * 100:.1f} %"  # type: ignore[operator]
        time_str = f"{r['total_ms']:.1f} ms"      # type: ignore[operator]
        ref_str = f"({shape.reference_rod_count})"

        print(
            f"  {shape.name:<18} {shape.area_m2:>5.0f} m2"
            f"  {r['rod_count']:>5}"
            f"  {ref_str:>6}"
            f"  {cov_str:>7}"
            f"  {time_str:>8}"
        )

    print("  " + "-" * 66)

    mean_ms = sum(total_times) / len(total_times)
    manual_ms = MANUAL_HOURS * 3600 * 1000
    speedup = manual_ms / mean_ms

    print(f"  mean pipeline time : {mean_ms:.1f} ms")
    print(f"  manual layout time : ~{MANUAL_HOURS:.0f} hours")
    print(f"  speedup            : x{speedup:,.0f}")
    print()
    print("  columns: rods = our algorithm,  ref = hand-estimate in ()")
    print()


if __name__ == "__main__":
    main()
