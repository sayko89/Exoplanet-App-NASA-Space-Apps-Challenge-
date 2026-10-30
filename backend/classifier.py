"""Pure-Python inference for the Kepler LightGBM classifier.

The model is trained with LightGBM (training/train_kepler_classifier.py) and exported as a
compact JSON tree dump. Walking those trees needs nothing but the standard library, so the
same code runs locally and in the in-browser demo, where LightGBM is not available.
"""
from __future__ import annotations

import json
import math
from pathlib import Path


class KeplerClassifier:
    def __init__(self, model_path: str | Path, metrics_path: str | Path):
        model = json.loads(Path(model_path).read_text())
        self.features: list[str] = model['features']
        self.trees: list[dict] = model['trees']
        self.metrics: dict = json.loads(Path(metrics_path).read_text())
        self.medians: dict = self.metrics['medians']

    def _row(self, values: dict) -> list[float]:
        row = []
        for f in self.features:
            v = values.get(f)
            try:
                v = float(v)
            except (TypeError, ValueError):
                v = math.nan
            row.append(self.medians[f] if math.isnan(v) else v)  # same as the training imputer
        return row

    def predict(self, values: dict) -> float:
        """Probability that the signal is planet-like (confirmed or candidate)."""
        x = self._row(values)
        score = 0.0
        for t in self.trees:
            i = 0
            f, thr, left, right = t['f'], t['t'], t['l'], t['r']
            while f[i] >= 0:
                i = left[i] if x[f[i]] <= thr[i] else right[i]
            score += t['v'][i]
        return 1.0 / (1.0 + math.exp(-score))
