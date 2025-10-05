"""
Simple validation for Exoplanet Explorer environment.
Checks core imports and key files exist.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path

REQUIRED_FILES = [
    "app.py",
    "pages/1_Exoplanets_List.py",
    "pages/2_Planet_Details.py",
    "pages/3_Chatbot.py",
    "pages/4_Video.py",
    "backend/predict.py",
    "data/exoplanets.csv",
    "assets/logo.png",
    "requirements.txt",
    ".env.example",
]

def main() -> int:
    # Import checks
    try:
        import streamlit  # noqa: F401
        import pandas  # noqa: F401
        import plotly  # noqa: F401
        import requests  # noqa: F401
    except Exception as e:
        print("Import error:", e)
        return 1

    # File checks
    missing = [p for p in REQUIRED_FILES if not Path(p).exists()]
    if missing:
        print("Missing files:", missing)
        return 2

    print("Environment looks good. All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
