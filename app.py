"""Route Optimization Tool -- interactive web demo (Streamlit).

Run locally with:

    streamlit run app.py

Upload a CSV of stops (name, lat, lon) -- or use the bundled Belgian sample --
and the app shows the optimised delivery round on a map, with the distance
saved versus a naive route. The optimisation logic lives in src/ and is unit
tested independently of this UI.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

from src.distance import distance_matrix
from src.solver import nearest_neighbour, route_distance, solve

DATA_FILE = Path(__file__).resolve().parent / "data" / "stops_example.csv"

st.set_page_config(page_title="Route Optimization Tool", page_icon="🗺️", layout="wide")
st.title("🗺️ Route Optimization Tool")
st.caption(
    "Plans the shortest delivery round through a set of stops "
    "(nearest-neighbour + 2-opt). First row of the CSV is the depot."
)

# --- Data source ---------------------------------------------------------
uploaded = st.sidebar.file_uploader(
    "Upload a stops CSV (name, lat, lon)", type="csv"
)
df = pd.read_csv(uploaded if uploaded is not None else DATA_FILE)
required = {"name", "lat", "lon"}
if not required.issubset(df.columns):
    st.error(f"CSV must have columns {sorted(required)}. Found: {list(df.columns)}")
    st.stop()

points = list(zip(df["lat"].astype(float), df["lon"].astype(float)))
matrix = distance_matrix(points)

naive = nearest_neighbour(matrix)
naive_km = route_distance(naive, matrix)
best, best_km = solve(matrix)
saved = naive_km - best_km
pct = (saved / naive_km * 100) if naive_km else 0.0

# --- Headline metrics ----------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Naive route", f"{naive_km:.0f} km")
c2.metric("Optimized route", f"{best_km:.0f} km")
c3.metric("Distance saved", f"{saved:.0f} km", f"-{pct:.1f}%")

# --- Map -----------------------------------------------------------------
ordered = df.iloc[best].reset_index(drop=True)
ordered["order"] = range(1, len(ordered) + 1)

path = [[row.lon, row.lat] for row in ordered.itertuples()]
path.append([ordered.iloc[0].lon, ordered.iloc[0].lat])  # return to depot

path_layer = pdk.Layer(
    "PathLayer",
    data=[{"path": path}],
    get_path="path",
    get_width=4,
    width_min_pixels=3,
    get_color=[0, 120, 240],
)
points_layer = pdk.Layer(
    "ScatterplotLayer",
    data=ordered,
    get_position=["lon", "lat"],
    get_radius=2500,
    get_fill_color=[230, 60, 60],
    pickable=True,
)
text_layer = pdk.Layer(
    "TextLayer",
    data=ordered,
    get_position=["lon", "lat"],
    get_text="order",
    get_size=16,
    get_color=[20, 20, 20],
    get_alignment_baseline="'bottom'",
)

view = pdk.ViewState(
    latitude=float(df["lat"].mean()),
    longitude=float(df["lon"].mean()),
    zoom=7,
)
st.pydeck_chart(
    pdk.Deck(
        layers=[path_layer, points_layer, text_layer],
        initial_view_state=view,
        map_style=None,
        tooltip={"text": "{order}. {name}"},
    )
)

# --- Ordered stop list ---------------------------------------------------
st.subheader("Optimized visiting order")
st.dataframe(
    ordered[["order", "name", "lat", "lon"]],
    width="stretch",
    hide_index=True,
)
