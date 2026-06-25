"""Route Planner — shortest delivery round through a set of stops (nearest-neighbour + 2-opt)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

from src.distance import distance_matrix
from src.solver import nearest_neighbour, route_distance, solve
from src import ingest

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "stops_example.csv"

st.set_page_config(page_title="Route Planner", page_icon="🗺️", layout="wide")

st.markdown(
    """
<style>
  .stApp { background-color: #0a0a0a; color: #f0f0f0; }
  section[data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #1e1e1e; }
  section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p { color: #aaaaaa !important; }
  div[data-testid="stMetric"] {
      background: #141414; border: 1px solid #252525; border-radius: 12px; padding: 16px 20px;
  }
  div[data-testid="stMetric"] label { color: #666 !important; font-size: 12px !important; }
  div[data-testid="stMetric"] [data-testid="stMetricValue"] {
      color: #f0f0f0 !important; font-size: 26px !important; font-weight: 700 !important;
  }
  h1, h2, h3 { color: #f0f0f0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🗺️ Route Planner")
st.caption("Plans the shortest round through a set of stops (nearest-neighbour + 2-opt). First row = depot.")

# --- Data source ---------------------------------------------------------
uploaded = st.sidebar.file_uploader("Upload a stops CSV (name, lat, lon)", type="csv")
with open(DATA_FILE, "rb") as _f:
    st.sidebar.download_button(
        "⬇️ Download template / sample CSV",
        _f.read(),
        file_name="stops_template.csv",
        mime="text/csv",
        help="Columns: name, lat, lon. The first row is the depot.",
    )

st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="✂️ Back to Barber Finder", icon="⬅️")

if uploaded is None:
    df = ingest.coerce(pd.read_csv(DATA_FILE))
else:
    try:
        raw = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not read this file as CSV: {exc}")
        st.stop()

    if set(ingest.REQUIRED).issubset(raw.columns):
        df = ingest.coerce(raw)
    else:
        st.warning("Your CSV columns don't match the expected format. Map them below.")
        cols = list(raw.columns)

        def _idx(field: str) -> int:
            g = ingest.guess_column(cols, field)
            return cols.index(g) if g in cols else 0

        m1, m2, m3 = st.columns(3)
        name_col = m1.selectbox("Name column", cols, index=_idx("name"))
        lat_col  = m2.selectbox("Latitude column", cols, index=_idx("lat"))
        lon_col  = m3.selectbox("Longitude column", cols, index=_idx("lon"))
        df = ingest.apply_mapping(raw, name_col, lat_col, lon_col)

if len(df) < 2:
    st.error("Need at least 2 valid rows: a depot and one stop (first row = depot).")
    st.stop()

points = list(zip(df["lat"].astype(float), df["lon"].astype(float)))
matrix = distance_matrix(points)

naive = nearest_neighbour(matrix)
naive_km = route_distance(naive, matrix)
best, best_km = solve(matrix)
saved = naive_km - best_km
pct = (saved / naive_km * 100) if naive_km else 0.0

# --- Metrics -----------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Naive route", f"{naive_km:.0f} km")
c2.metric("Optimized route", f"{best_km:.0f} km")
c3.metric("Distance saved", f"{saved:.0f} km", f"-{pct:.1f}%")

# --- Map ---------------------------------------------------------------------
ordered = df.iloc[best].reset_index(drop=True)
ordered["order"] = range(1, len(ordered) + 1)

path = [[row.lon, row.lat] for row in ordered.itertuples()]
path.append([ordered.iloc[0].lon, ordered.iloc[0].lat])

path_layer = pdk.Layer(
    "PathLayer",
    data=[{"path": path}],
    get_path="path",
    get_width=4,
    width_min_pixels=3,
    get_color=[200, 169, 126],
)
points_layer = pdk.Layer(
    "ScatterplotLayer",
    data=ordered,
    get_position=["lon", "lat"],
    get_radius=2500,
    get_fill_color=[200, 169, 126, 220],
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

# --- Stop list ---------------------------------------------------------------
st.subheader("Optimized visiting order")
st.dataframe(ordered[["order", "name", "lat", "lon"]], hide_index=True)
