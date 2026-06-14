# Route Optimization Tool

A small, dependency-free Python tool that plans the shortest delivery round
through a set of stops (a Travelling Salesman Problem). Give it a list of
addresses with coordinates; it returns an optimised visiting order and the
distance saved versus a naive route.

The solver itself uses **only the Python standard library** — no NumPy, no
external solver — so it's easy to read and audit.

## Web demo

An interactive map (Streamlit) shows the optimised round and the distance saved:

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens in your browser with the bundled Belgian sample; you can also upload
your own `name, lat, lon` CSV from the sidebar.

> **Deploy a public demo (free):** push this repo to GitHub, go to
> [share.streamlit.io](https://share.streamlit.io), click *New app*, select the
> repo and set the main file to `app.py`. You get a public URL to share.

## How it works

1. **Nearest neighbour** builds a quick first route (always go to the closest
   unvisited stop).
2. **2-opt local search** then improves it: it repeatedly reverses route
   segments whenever that shortens the total distance.

Distances use the **haversine** great-circle formula, accurate enough for
real delivery planning.

## Quick start

```bash
pip install -r requirements.txt   # only needed to run the tests
python -m src.cli data/stops_example.csv
```

Example output (12 Belgian cities, depot in Mons):

```
Stops: 12 (depot: Depot Mons)

Optimized route:
   1. Depot Mons
   2. Tournai
   3. Gent
   ...
  13. Depot Mons  (return to depot)

Nearest-neighbour distance :   582.7 km
After 2-opt improvement    :   460.0 km
Saved                      :   122.7 km (21.1%)
```

## Input format

A CSV with three columns. The **first row is the depot** — the route starts
and ends there.

```csv
name,lat,lon
Depot Mons,50.4542,3.9523
Bruxelles,50.8503,4.3517
Charleroi,50.4108,4.4446
```

## Use it as a library

```python
from src.distance import distance_matrix
from src.solver import solve

points = [(50.45, 3.95), (50.85, 4.35), (50.41, 4.44)]
route, total_km = solve(distance_matrix(points))
```

## Tests

```bash
pytest
```

## Project layout

```
route-optimization-tool/
├── src/
│   ├── distance.py   # haversine distance + distance matrix
│   ├── solver.py     # nearest neighbour + 2-opt
│   └── cli.py        # command-line entry point
├── data/
│   └── stops_example.csv
├── tests/            # unit tests (pytest)
└── requirements.txt
```

## License

MIT
