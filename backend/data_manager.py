"""Loads the three mission tables built by scripts/build_datasets.py.

All three share one schema (see COLUMNS there), so every page can treat Kepler, TESS and K2
the same way. A value the NASA archive does not provide is NaN, never a placeholder.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
MODELS = ROOT / 'models'


class Mission(Enum):
    KEPLER = 'Kepler'
    TESS = 'TESS'
    K2 = 'K2'

    @property
    def file(self) -> Path:
        return DATA / f'{self.name.lower()}.csv'

    @classmethod
    def from_label(cls, label: str | None) -> 'Mission | None':
        for m in cls:
            if label and label.strip().upper() == m.name:
                return m
        return None


MISSION_BLURB = {
    Mission.KEPLER: 'Kepler Objects of Interest (2009–2018). The archive table has no distances or masses.',
    Mission.TESS: 'TESS Objects of Interest, all-sky survey since 2018. Names are TOI numbers.',
    Mission.K2: "K2, Kepler's second mission (2014–2018): planets and candidates.",
}

DISPOSITIONS = ['CONFIRMED', 'CANDIDATE', 'FALSE POSITIVE']


@st.cache_data(show_spinner=False)
def load(mission: Mission) -> pd.DataFrame:
    df = pd.read_csv(mission.file)
    if mission is Mission.KEPLER and (DATA / 'kepler_ai.csv').exists():
        ai = pd.read_csv(DATA / 'kepler_ai.csv')
        df = df.merge(ai, on='catalog_id', how='left')
    order = {d: i for i, d in enumerate(DISPOSITIONS)}
    df['_order'] = df['disposition'].map(order)
    return df.sort_values(['_order', 'name']).drop(columns='_order').reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_all() -> pd.DataFrame:
    return pd.concat([load(m) for m in Mission], ignore_index=True)


def find(mission: Mission, name: str | None) -> pd.Series | None:
    if not name:
        return None
    df = load(mission)
    hit = df[df['name'].str.lower() == str(name).strip().lower()]
    return None if hit.empty else hit.iloc[0]
