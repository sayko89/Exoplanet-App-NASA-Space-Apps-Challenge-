"""
Prediction utilities for Exoplanet Explorer.

This module intentionally avoids any training or heavy preprocessing. It provides
a lightweight interface to "predict" habitability-like scores using simple
heuristics over the sample CSV. Replace the `predict_habitability_score` logic
with real model inference when available.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import pandas as pd


@dataclass
class PredictionResult:
    name: str
    score: float
    rationale: str


def _load_dataset(csv_path: str) -> pd.DataFrame:
    """Load the exoplanet CSV with caching-friendly semantics."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def predict_habitability_score(planet_name: str, csv_path: str = "data/exoplanets.csv") -> PredictionResult:
    """
    Simulate a habitability score using simple heuristics based on temperature,
    radius, and mass. This is a placeholder for real model inference.
    """
    df = _load_dataset(csv_path)
    row = df[df["name"].str.lower() == planet_name.strip().lower()]
    if row.empty:
        return PredictionResult(name=planet_name, score=0.0, rationale="Planet not found in dataset.")

    r = row.iloc[0]

    # Heuristic scoring (0 to 1): closer to Earth-like radius/mass and temperate zone
    temp = float(r.get("temperature_k", 0) or 0)
    radius = float(r.get("radius_earth", 0) or 0)
    mass = float(r.get("mass_earth", 0) or 0)

    temp_score = max(0.0, 1.0 - abs(temp - 288) / 100)  # 288K ~ Earth avg; ±100K tolerance
    radius_score = max(0.0, 1.0 - abs(radius - 1.0) / 0.5)  # Earth radius ±0.5
    mass_score = max(0.0, 1.0 - abs(mass - 1.0) / 0.7)    # Earth mass ±0.7

    score = round(0.5 * temp_score + 0.25 * radius_score + 0.25 * mass_score, 3)

    rationale = (
        f"Temp={temp}K (score={temp_score:.2f}), "
        f"Radius={radius} R_earth (score={radius_score:.2f}), "
        f"Mass={mass} M_earth (score={mass_score:.2f})."
    )
    return PredictionResult(name=str(r.get("name", planet_name)), score=score, rationale=rationale)
