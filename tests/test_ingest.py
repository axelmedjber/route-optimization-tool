import pandas as pd

from src.ingest import REQUIRED, apply_mapping, coerce, guess_column


def test_guess_column_french_headers():
    cols = ["Ville", "Latitude", "Longitude"]
    assert guess_column(cols, "name") == "Ville"
    assert guess_column(cols, "lat") == "Latitude"
    assert guess_column(cols, "lon") == "Longitude"


def test_apply_mapping_normalizes():
    raw = pd.DataFrame(
        {
            "Ville": ["Mons", "Bruxelles"],
            "Latitude": ["50.45", "50.85"],
            "Longitude": ["3.95", "4.35"],
        }
    )
    df = apply_mapping(raw, "Ville", "Latitude", "Longitude")
    assert list(df.columns) == REQUIRED
    assert df["lat"].tolist() == [50.45, 50.85]
    assert df["name"].tolist() == ["Mons", "Bruxelles"]


def test_coerce_drops_rows_without_coordinates():
    raw = pd.DataFrame(
        {
            "name": ["A", "B"],
            "lat": [50.0, "nope"],
            "lon": [4.0, 4.5],
        }
    )
    df = coerce(raw)
    assert len(df) == 1
    assert df.iloc[0]["name"] == "A"
