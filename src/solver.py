"""Travelling Salesman Problem (TSP) heuristics for delivery routing.

The route always starts and ends at the depot (index 0) and visits every
other stop exactly once. Two classic heuristics are combined:

1. **Nearest neighbour** builds a quick initial route by always going to the
   closest unvisited stop.
2. **2-opt** then improves that route by repeatedly reversing segments
   whenever doing so shortens the total distance.

This is not guaranteed optimal, but for small delivery rounds it gets very
close while staying fast and easy to understand.
"""

from __future__ import annotations

from typing import Sequence

Matrix = Sequence[Sequence[float]]


def route_distance(route: Sequence[int], matrix: Matrix) -> float:
    """Total length of a closed route (returns to the start)."""
    total = 0.0
    for i in range(len(route) - 1):
        total += matrix[route[i]][route[i + 1]]
    total += matrix[route[-1]][route[0]]  # back to depot
    return total


def nearest_neighbour(matrix: Matrix, start: int = 0) -> list[int]:
    """Build an initial route greedily from ``start``."""
    n = len(matrix)
    unvisited = set(range(n))
    unvisited.remove(start)
    route = [start]
    current = start
    while unvisited:
        nxt = min(unvisited, key=lambda j: matrix[current][j])
        route.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    return route


def two_opt(route: list[int], matrix: Matrix) -> list[int]:
    """Improve a route with the 2-opt local search until no swap helps.

    The depot (first stop) is kept fixed; only the order of the remaining
    stops is optimised.
    """
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                # Reverse the segment between i and j.
                candidate = best[:i] + best[i : j + 1][::-1] + best[j + 1 :]
                if route_distance(candidate, matrix) < route_distance(best, matrix) - 1e-9:
                    best = candidate
                    improved = True
    return best


def solve(matrix: Matrix, start: int = 0) -> tuple[list[int], float]:
    """Return an optimised route and its total distance.

    Combines nearest-neighbour construction with 2-opt improvement.
    """
    initial = nearest_neighbour(matrix, start=start)
    improved = two_opt(initial, matrix)
    return improved, route_distance(improved, matrix)
