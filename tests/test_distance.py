import math

from src.distance import haversine, distance_matrix


def test_haversine_zero_distance():
    assert haversine((50.0, 4.0), (50.0, 4.0)) == 0.0


def test_haversine_known_distance():
    # Brussels to Paris is roughly 264 km.
    brussels = (50.8503, 4.3517)
    paris = (48.8566, 2.3522)
    d = haversine(brussels, paris)
    assert math.isclose(d, 264, abs_tol=5)


def test_haversine_is_symmetric():
    a, b = (50.45, 3.95), (51.21, 4.40)
    assert math.isclose(haversine(a, b), haversine(b, a))


def test_distance_matrix_shape_and_diagonal():
    points = [(50.0, 4.0), (51.0, 4.0), (50.5, 4.5)]
    m = distance_matrix(points)
    assert len(m) == 3 and all(len(row) == 3 for row in m)
    for i in range(3):
        assert m[i][i] == 0.0
    # symmetric
    assert m[0][1] == m[1][0]
