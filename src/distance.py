"""Geographic distance helpers.

Distances are computed with the haversine formula, which gives the
great-circle distance between two latitude/longitude points on the Earth.
Accurate enough for delivery planning and free of external dependencies.
"""

from __future__ import annotations

import math
from typing import Sequence, Tuple

EARTH_RADIUS_KM = 6371.0088

Point = Tuple[float, float]  # (latitude, longitude) in decimal degrees


def haversine(a: Point, b: Point) -> float:
    """Great-circle distance between two (lat, lon) points, in kilometres."""
    lat1, lon1 = a
    lat2, lon2 = b
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    h = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def distance_matrix(points: Sequence[Point]) -> list[list[float]]:
    """Symmetric matrix of pairwise haversine distances (km)."""
    n = len(points)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine(points[i], points[j])
            matrix[i][j] = d
            matrix[j][i] = d
    return matrix
