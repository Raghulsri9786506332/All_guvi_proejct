"""
NEW FILE: recommend.py (Robust path version)
Cosine similarity-based recommendation engine for Swiggy restaurants.
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

POSSIBLE_DIRS = [
    r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code\swiggy_recommendation\swiggy_recommendation",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
]

DATA_DIR = None
for d in POSSIBLE_DIRS:
    candidate = os.path.join(d, "data", "cleaned_data.csv")
    if os.path.exists(candidate):
        DATA_DIR = os.path.join(d, "data")
        MODEL_DIR = os.path.join(d, "models")
        break

if DATA_DIR is None:
    DATA_DIR = os.path.join(POSSIBLE_DIRS[0], "data")
    MODEL_DIR = os.path.join(POSSIBLE_DIRS[0], "models")

CLEANED_PATH = os.path.join(DATA_DIR, "cleaned_data.csv")
ENCODED_PATH = os.path.join(DATA_DIR, "encoded_data.csv")
ENCODER_PATH = os.path.join(MODEL_DIR, "encoder.pkl")

_cache: dict = {}


def load_data():
    """Load cleaned data, encoded data, and encoder (cached)."""
    if _cache:
        return _cache["cleaned"], _cache["encoded"], _cache["encoder"]

    if not os.path.exists(CLEANED_PATH):
        raise FileNotFoundError(f"cleaned_data.csv not found at {CLEANED_PATH}. Run preprocess.py first.")
    if not os.path.exists(ENCODED_PATH):
        raise FileNotFoundError(f"encoded_data.csv not found at {ENCODED_PATH}. Run preprocess.py first.")
    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(f"encoder.pkl not found at {ENCODER_PATH}. Run preprocess.py first.")

    cleaned = pd.read_csv(CLEANED_PATH)
    encoded = pd.read_csv(ENCODED_PATH)
    with open(ENCODER_PATH, "rb") as f:
        encoder = pickle.load(f)

    _cache["cleaned"] = cleaned
    _cache["encoded"] = encoded
    _cache["encoder"] = encoder
    return cleaned, encoded, encoder


def build_user_vector(user_input: dict, encoder, encoded_columns: list) -> np.ndarray:
    categorical_input = pd.DataFrame([[user_input["city"], user_input["cuisine"]]],
                                     columns=["city", "cuisine"])
    cat_encoded = encoder.transform(categorical_input)

    numerical = np.array([[
        user_input.get("rating", 3.5),
        user_input.get("rating_count", 100),
        user_input.get("cost", 300),
    ]])

    user_vector = np.hstack([numerical, cat_encoded])
    return user_vector


def get_recommendations(user_input: dict, top_n: int = 10) -> pd.DataFrame:
    cleaned, encoded, encoder = load_data()

    city = user_input.get("city", "")
    cuisine = user_input.get("cuisine", "")
    min_rating = user_input.get("rating", 0)
    max_cost = user_input.get("cost", float("inf"))
    min_rating_count = user_input.get("rating_count", 0)

    mask = pd.Series([True] * len(cleaned))
    if city:
        mask &= cleaned["city"].str.lower() == city.lower()
    if cuisine:
        mask &= cleaned["cuisine"].str.lower().str.contains(cuisine.lower(), na=False)
    mask &= cleaned["rating"] >= min_rating
    mask &= cleaned["cost"] <= max_cost
    mask &= cleaned["rating_count"] >= min_rating_count

    filtered_clean = cleaned[mask].copy()
    filtered_encoded = encoded[mask].copy()

    if filtered_clean.empty:
        return pd.DataFrame()

    user_vector = build_user_vector(user_input, encoder, encoded.columns.tolist())
    similarities = cosine_similarity(user_vector, filtered_encoded.values)[0]
    filtered_clean = filtered_clean.copy()
    filtered_clean["similarity_score"] = similarities

    result = filtered_clean.nlargest(top_n, "similarity_score")
    result = result.reset_index(drop=True)
    return result
