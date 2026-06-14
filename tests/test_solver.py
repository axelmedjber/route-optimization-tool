from src.distance import distance_matrix
from src.solver import nearest_neighbour, two_opt, route_distance, solve


def square_matrix():
    # Four points on a unit square; the optimal tour follows the perimeter.
    points = [(0, 0), (0, 1), (1, 1), (1, 0)]
    return distance_matrix(points)


def test_nearest_neighbour_visits_all_stops_once():
    m = square_matrix()
    route = nearest_neighbour(m, start=0)
    assert sorted(route) == [0, 1, 2, 3]
    assert route[0] == 0


def test_two_opt_never_worsens_route():
    m = square_matrix()
    initial = [0, 2, 1, 3]  # a deliberately crossed (bad) tour
    improved = two_opt(initial, m)
    assert route_distance(improved, m) <= route_distance(initial, m)


def test_solve_finds_perimeter_on_square():
    m = square_matrix()
    route, dist = solve(m)
    # The optimal tour on a square follows the perimeter (visiting corners in
    # order); any crossed tour is strictly longer.
    perimeter = route_distance([0, 1, 2, 3], m)
    crossed = route_distance([0, 2, 1, 3], m)
    assert abs(dist - perimeter) < 1e-9
    assert dist < crossed
    assert sorted(route) == [0, 1, 2, 3]


def test_solve_is_at_least_as_good_as_nearest_neighbour():
    points = [(50.45, 3.95), (50.85, 4.35), (50.41, 4.44),
              (50.63, 5.58), (51.05, 3.72), (51.22, 4.40)]
    m = distance_matrix(points)
    nn = route_distance(nearest_neighbour(m), m)
    _, optimized = solve(m)
    assert optimized <= nn + 1e-9
