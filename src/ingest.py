"""Turn an arbitrary uploaded CSV into the canonical stops format.

The tool expects ``name, lat, lon`` (first row = depot). Real files often use
other column names, so this module maps any three columns onto that schema and
validates that the coordinates are numeric.
"""

from __future__ import annotations

import pandas as pd

REQUIRED = ["name", "lat", "lon"]

HINTS = {
    "name": ["name", "nom", "stop", "arret", "arrêt", "ville", "city", "label",
             "adresse", "address", "client", "site"],
    "lat": ["lat", "latitude"],
    "lon": ["lon", "lng", "long", "longitude"],
}


def guess_column(columns, field: str):
    """Best-guess column name for a canonical field, or None."""
    for col in columns:
        low = str(col).lower()
        if any(k in low for k in HINTS.get(field, [])):
            return col
    return None


def _finalize(df: pd.DataFrame) -> pd.DataFrame:
    df["name"] = df["name"].astype(str)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    return df[REQUIRED].reset_index(drop=True)


def coerce(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a frame that already has the required columns."""
    return _finalize(df.copy())


def apply_mapping(raw: pd.DataFrame, name_col: str, lat_col: str, lon_col: str) -> pd.DataFrame:
    """Map arbitrary columns to ``name, lat, lon``."""
    out = pd.DataFrame(
        {"name": raw[name_col], "lat": raw[lat_col], "lon": raw[lon_col]}
    )
    return _finalize(out)
