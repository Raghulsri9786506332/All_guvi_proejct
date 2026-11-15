"""
NEW FILE: utils.py (Robust path version)
Utility functions to load unique values from cleaned data for Streamlit UI.
Resolves data directory robustly regardless of current working directory.
"""

import os
import pandas as pd

# Find data/cleaned_data.csv by checking candidate locations
POSSIBLE_PATHS = [
    r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code\swiggy_recommendation\swiggy_recommendation\data\cleaned_data.csv",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cleaned_data.csv"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "swiggy_recommendation", "data", "cleaned_data.csv"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "swiggy_recommendation", "swiggy_recommendation", "data", "cleaned_data.csv"),
]

CLEANED_PATH = None
for p in POSSIBLE_PATHS:
    if p and os.path.exists(p):
        CLEANED_PATH = p
        break

if CLEANED_PATH is None:
    CLEANED_PATH = POSSIBLE_PATHS[0]


def _load_cleaned() -> pd.DataFrame:
    if not os.path.exists(CLEANED_PATH):
        raise FileNotFoundError(
            f"cleaned_data.csv not found at {CLEANED_PATH}. Run python src/preprocess.py first."
        )
    return pd.read_csv(CLEANED_PATH)


def get_unique_cities() -> list:
    """Return sorted list of unique cities from cleaned data."""
    df = _load_cleaned()
    return sorted(df["city"].dropna().unique().tolist())


def get_unique_cuisines() -> list:
    """Return sorted list of unique cuisines from cleaned data."""
    df = _load_cleaned()
    return sorted(df["cuisine"].dropna().unique().tolist())
