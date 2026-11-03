"""
Benchmark shapes with known geometry and reference rod counts.

reference_rod_count: a reasonable estimate of how many rods a careful human
would place for full coverage at height=3m / radius=3m.  Our greedy algorithm
may use more; that is expected and acceptable.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkShape:
    name: str
    description: str
    polygon: list[tuple[float, float]]
    area_m2: float
    reference_rod_count: int


SHAPES: list[BenchmarkShape] = [
    BenchmarkShape(
        name="rect_10x10",
        description="Simple 10 × 10 m square",
        polygon=[(0, 0), (10, 0), (10, 10), (0, 10)],
        area_m2=100.0,
        reference_rod_count=6,
    ),
    BenchmarkShape(
        name="rect_20x15",
        description="Rectangular 20 × 15 m building",
        polygon=[(0, 0), (20, 0), (20, 15), (0, 15)],
        area_m2=300.0,
        reference_rod_count=12,
    ),
    BenchmarkShape(
        name="l_shape",
        description="L-shaped building (10 × 10 m with 4 × 4 m corner removed)",
        polygon=[
            (0, 0), (10, 0), (10, 6), (4, 6), (4, 10), (0, 10),
        ],
        area_m2=76.0,
        reference_rod_count=7,
    ),
    BenchmarkShape(
        name="u_shape",
        description="U-shaped building (outer 14 × 10 m, inner notch 6 × 5 m)",
        polygon=[
            (0, 0), (14, 0), (14, 10),
            (10, 10), (10, 5), (4, 5), (4, 10),
            (0, 10),
        ],
        area_m2=110.0,
        reference_rod_count=9,
    ),
    BenchmarkShape(
        name="warehouse_30x20",
        description="Large warehouse 30 × 20 m",
        polygon=[(0, 0), (30, 0), (30, 20), (0, 20)],
        area_m2=600.0,
        reference_rod_count=22,
    ),
]
