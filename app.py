"""BarberFind — discover top-rated barbers near you, inspired by theCut."""
from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from src.barber_finder import (
    add_distances,
    all_services,
    avatar_color,
    filter_barbers,
    initials,
    load_barbers,
    rating_color,
)

st.set_page_config(
    page_title="BarberFind",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
  .stApp { background-color: #0a0a0a; color: #f0f0f0; }

  section[data-testid="stSidebar"] {
      background-color: #111111;
      border-right: 1px solid #1e1e1e;
  }
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p { color: #aaaaaa !important; }

  div[data-testid="stMetric"] {
      background: #141414;
      border: 1px solid #252525;
      border-radius: 12px;
      padding: 16px 20px;
  }
  div[data-testid="stMetric"] label { color: #666 !important; font-size: 12px !important; }
  div[data-testid="stMetric"] [data-testid="stMetricValue"] {
      color: #f0f0f0 !important; font-size: 26px !important; font-weight: 700 !important;
  }

  h1, h2, h3 { color: #f0f0f0 !important; }
  .stMarkdown p { color: #aaaaaa; }

  .barber-card {
      background: #141414;
      border: 1px solid #252525;
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 14px;
      transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
  }
  .barber-card:hover {
      border-color: #C8A97E;
      box-shadow: 0 6px 24px rgba(200,169,126,0.12);
      transform: translateY(-2px);
  }
  .card-top { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 12px; }
  .avatar {
      width: 46px; height: 46px; min-width: 46px;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 15px; color: white;
  }
  .barber-name { font-weight: 700; font-size: 15px; color: #f0f0f0; line-height: 1.3; }
  .card-rating { font-size: 13px; margin-top: 3px; color: #C8A97E; }
  .rating-num { font-weight: 600; color: #f0f0f0; }
  .review-cnt { color: #555; }
  .card-city { color: #666; font-size: 11px; margin-top: 3px; }
  .avail-badge {
      margin-left: auto; font-size: 10px; font-weight: 600;
      padding: 3px 10px; border-radius: 20px; white-space: nowrap;
  }
  .avail-yes { background: rgba(46,213,115,0.12); color: #2ed573; border: 1px solid rgba(46,213,115,0.25); }
  .avail-no  { background: rgba(255,107,107,0.1); color: #ff6b6b; border: 1px solid rgba(255,107,107,0.2); }
  .svc-tags  { margin: 10px 0; display: flex; flex-wrap: wrap; gap: 6px; }
  .svc-tag {
      background: #1e1e1e; border: 1px solid #2e2e2e;
      border-radius: 20px; padding: 3px 10px;
      font-size: 11px; color: #C8A97E;
  }
  .card-meta {
      display: flex; gap: 14px; font-size: 12px;
      color: #666; margin: 10px 0; align-items: center;
  }
  .c-dist { color: #aaa; font-weight: 500; }
  .c-price { color: #C8A97E; font-weight: 600; letter-spacing: 1px; }
  .card-about { font-size: 11px; color: #555; margin-bottom: 14px; font-style: italic; }
  .card-actions { display: flex; gap: 8px; }
  .btn-book {
      flex: 1; background: #C8A97E; color: #0a0a0a;
      border-radius: 8px; padding: 9px 0;
      font-weight: 700; font-size: 13px; text-align: center; cursor: pointer;
  }
  .btn-profile {
      flex: 1; background: transparent; color: #888;
      border: 1px solid #2e2e2e; border-radius: 8px; padding: 9px 0;
      font-size: 13px; text-align: center; cursor: pointer;
  }
  .hero { padding: 12px 0 20px; }
  .hero h1 { font-size: 34px !important; font-weight: 800 !important; margin: 0; }
  .hero p  { font-size: 15px; color: #666; margin-top: 6px; }
  .gold { color: #C8A97E; }
  .section-title { font-size: 18px; font-weight: 700; color: #f0f0f0; margin: 20px 0 12px; }
  .empty-state {
      text-align: center; padding: 48px 20px; color: #555;
      background: #111; border-radius: 14px; border: 1px solid #1e1e1e;
  }
  .empty-state .icon { font-size: 40px; margin-bottom: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
CITIES: dict[str, tuple[float, float]] = {
    "Brussels":  (50.8503, 4.3517),
    "Antwerp":   (51.2194, 4.4025),
    "Ghent":     (51.0543, 3.7174),
    "Bruges":    (51.2093, 3.2247),
    "Leuven":    (50.8798, 4.7005),
    "Liège":     (50.6326, 5.5797),
    "Namur":     (50.4669, 4.8674),
    "Mons":      (50.4542, 3.9523),
    "Charleroi": (50.4108, 4.4446),
    "Mechelen":  (51.0281, 4.4801),
}


@st.cache_data
def _load() -> pd.DataFrame:
    return load_barbers()


barbers_df = _load()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ✂️ BarberFind")
    st.markdown("---")

    st.markdown("### 📍 Your Location")
    city_choice = st.selectbox("City", list(CITIES.keys()) + ["Custom coordinates"])
    if city_choice == "Custom coordinates":
        user_lat = st.number_input("Latitude", value=50.8503, format="%.4f")
        user_lon = st.number_input("Longitude", value=4.3517, format="%.4f")
    else:
        user_lat, user_lon = CITIES[city_choice]

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    max_dist = st.slider("Max distance (km)", 1, 150, 50)
    min_rating = st.slider("Min rating ⭐", 4.0, 5.0, 4.0, step=0.1, format="%.1f")

    price_opts = st.multiselect(
        "Price range",
        options=["€", "€€", "€€€"],
        default=["€", "€€", "€€€"],
    )
    price_map = {"€": 1, "€€": 2, "€€€": 3}
    price_levels = [price_map[p] for p in price_opts] if price_opts else None

    service_options = all_services(barbers_df)
    selected_services = st.multiselect("Services offered", service_options)

    available_only = st.checkbox("Available now only")

    st.markdown("---")
    st.page_link("pages/Route_Planner.py", label="🗺️ Plan a Multi-Stop Route", icon="➡️")

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
  <h1>✂️ Barber<span class="gold">Find</span></h1>
  <p>Discover top-rated barbers near you — book in seconds</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Compute distances & apply filters
# ---------------------------------------------------------------------------
df = add_distances(barbers_df, user_lat, user_lon)
df = filter_barbers(df, max_dist, min_rating, price_levels, selected_services, available_only)

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Barbers Found", len(df))
if len(df) > 0:
    c2.metric("Avg Rating", f"⭐ {df['rating'].mean():.1f}")
    c3.metric("Nearest", f"📍 {df['distance_km'].min():.1f} km")
    c4.metric("Available Now", df["available"].sum())
else:
    c2.metric("Avg Rating", "—")
    c3.metric("Nearest", "—")
    c4.metric("Available Now", "—")

st.markdown("")

# ---------------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------------
if len(df) > 0:
    map_data = df[["lat", "lon", "name", "rating", "review_count", "distance_km", "city", "available"]].copy()
    map_data["color"] = map_data["rating"].apply(rating_color)
    map_data["position"] = map_data.apply(lambda r: [r["lon"], r["lat"]], axis=1)

    barber_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="position",
        get_fill_color="color",
        get_radius=220,
        radius_min_pixels=7,
        radius_max_pixels=18,
        pickable=True,
    )
    user_layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"position": [user_lon, user_lat], "name": "You are here", "rating": "", "review_count": "", "distance_km": "", "city": ""}],
        get_position="position",
        get_fill_color=[200, 169, 126, 255],
        get_radius=300,
        radius_min_pixels=10,
        radius_max_pixels=22,
        stroked=True,
        get_line_color=[255, 255, 255, 200],
        line_width_min_pixels=2,
        pickable=True,
    )

    view = pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=10, pitch=0)
    st.pydeck_chart(
        pdk.Deck(
            layers=[barber_layer, user_layer],
            initial_view_state=view,
            map_style=None,
            tooltip={"text": "{name}\n⭐ {rating} ({review_count} reviews)\n📍 {distance_km} km · {city}"},
        )
    )

# ---------------------------------------------------------------------------
# Barber cards
# ---------------------------------------------------------------------------
if len(df) == 0:
    st.markdown(
        """
<div class="empty-state">
  <div class="icon">🔍</div>
  <p><strong style="color:#aaa">No barbers match your filters.</strong><br>
  Try increasing the max distance or relaxing other filters.</p>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="section-title">Barbers Near You</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    grid = [col_a, col_b, col_c]

    for i, row in df.iterrows():
        color = avatar_color(i)
        inits = initials(row["name"])
        full = int(row["rating"])
        star_str = "★" * full + "☆" * (5 - full)
        price_str = "€" * int(row["price_range"])
        avail_cls = "avail-yes" if row["available"] else "avail-no"
        avail_txt = "● Available" if row["available"] else "○ Busy"
        svc_tags = "".join(
            f'<span class="svc-tag">{s.strip()}</span>'
            for s in row["services"].split(",")[:4]
        )

        card = f"""
<div class="barber-card">
  <div class="card-top">
    <div class="avatar" style="background:{color}">{inits}</div>
    <div>
      <div class="barber-name">{row['name']}</div>
      <div class="card-rating">
        {star_str}&nbsp;<span class="rating-num">{row['rating']}</span>&nbsp;<span class="review-cnt">({row['review_count']:,})</span>
      </div>
      <div class="card-city">{row['city']}</div>
    </div>
    <div class="avail-badge {avail_cls}">{avail_txt}</div>
  </div>
  <div class="svc-tags">{svc_tags}</div>
  <div class="card-meta">
    <span>⏱ ~{row['wait_time']} min</span>
    <span>·</span>
    <span class="c-dist">📍 {row['distance_km']} km</span>
    <span class="c-price">{price_str}</span>
  </div>
  <div class="card-about">{row['about']}</div>
  <div class="card-actions">
    <div class="btn-book">Book Now</div>
    <div class="btn-profile">View Profile</div>
  </div>
</div>"""

        with grid[i % 3]:
            st.markdown(card, unsafe_allow_html=True)
