"""Barber search and filtering utilities."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .distance import haversine

_DATA_PATH = Path(__file__).parent.parent / "data" / "barbers_sample.csv"

_AVATAR_COLORS = [
    "#C8A97E", "#4A6FA5", "#4A8C5C", "#C15F3C",
    "#7B5EA7", "#3CA6A6", "#A54A6F", "#5E7BC1",
]


def load_barbers(path: str | None = None) -> pd.DataFrame:
    p = Path(path) if path else _DATA_PATH
    df = pd.read_csv(p)
    df["available"] = df["available"].astype(str).str.lower() == "true"
    return df


def add_distances(df: pd.DataFrame, user_lat: float, user_lon: float) -> pd.DataFrame:
    df = df.copy()
    df["distance_km"] = df.apply(
        lambda r: round(haversine((user_lat, user_lon), (r["lat"], r["lon"])), 1),
        axis=1,
    )
    return df.sort_values("distance_km").reset_index(drop=True)


def filter_barbers(
    df: pd.DataFrame,
    max_distance: float | None = None,
    min_rating: float = 0.0,
    price_levels: list[int] | None = None,
    services: list[str] | None = None,
    available_only: bool = False,
) -> pd.DataFrame:
    if max_distance is not None and "distance_km" in df.columns:
        df = df[df["distance_km"] <= max_distance]
    if min_rating:
        df = df[df["rating"] >= min_rating]
    if price_levels:
        df = df[df["price_range"].isin(price_levels)]
    if available_only:
        df = df[df["available"]]
    if services:
        mask = df["services"].apply(
            lambda s: any(svc.strip() in s for svc in services)
        )
        df = df[mask]
    return df.reset_index(drop=True)


def all_services(df: pd.DataFrame) -> list[str]:
    seen: set[str] = set()
    for cell in df["services"]:
        seen.update(s.strip() for s in cell.split(","))
    return sorted(seen)


def avatar_color(idx: int) -> str:
    return _AVATAR_COLORS[idx % len(_AVATAR_COLORS)]


def initials(name: str) -> str:
    parts = name.split()
    return "".join(p[0].upper() for p in parts[:2])


def rating_color(rating: float) -> list[int]:
    if rating >= 4.7:
        return [46, 213, 115, 230]
    if rating >= 4.4:
        return [255, 193, 7, 230]
    return [255, 107, 74, 230]
