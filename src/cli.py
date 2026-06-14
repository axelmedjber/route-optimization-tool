"""Command-line interface for the route optimizer.

Usage:

    python -m src.cli data/stops_example.csv

The CSV must have the columns ``name``, ``lat``, ``lon``. The first row is
treated as the depot: the route starts and ends there.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .distance import distance_matrix
from .solver import nearest_neighbour, route_distance, solve


def load_stops(path: Path) -> tuple[list[str], list[tuple[float, float]]]:
    names: list[str] = []
    points: list[tuple[float, float]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"name", "lat", "lon"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV must have columns {sorted(required)}")
        for row in reader:
            names.append(row["name"])
            points.append((float(row["lat"]), float(row["lon"])))
    if len(points) < 2:
        raise ValueError("need at least 2 stops (a depot and one delivery)")
    return names, points


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Optimize a delivery route (TSP).")
    parser.add_argument("csv", type=Path, help="CSV with columns name,lat,lon")
    args = parser.parse_args(argv)

    names, points = load_stops(args.csv)
    matrix = distance_matrix(points)

    naive = nearest_neighbour(matrix)          # greedy starting point
    naive_km = route_distance(naive, matrix)
    best, best_km = solve(matrix)              # nearest neighbour + 2-opt

    print(f"Stops: {len(names)} (depot: {names[0]})\n")
    print("Optimized route:")
    for step, idx in enumerate(best, start=1):
        print(f"  {step:>2}. {names[idx]}")
    print(f"  {len(best) + 1:>2}. {names[best[0]]}  (return to depot)\n")

    saved = naive_km - best_km
    pct = (saved / naive_km * 100) if naive_km else 0.0
    print(f"Nearest-neighbour distance : {naive_km:7.1f} km")
    print(f"After 2-opt improvement    : {best_km:7.1f} km")
    print(f"Saved                      : {saved:7.1f} km ({pct:.1f}%)")


if __name__ == "__main__":
    main()
