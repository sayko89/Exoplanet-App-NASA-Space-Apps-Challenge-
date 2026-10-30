"""Build the three mission tables the app reads, from NASA Exoplanet Archive exports.

    python scripts/build_datasets.py

Inputs (data/raw/):
  kepler_koi_values_2020.csv    KOI cumulative table, all columns, real values
                                (Archive export, Jan 2020; DR25 fits, numbers unchanged since)
  kepler_koi_2025_labels.csv    names + dispositions from the team's Oct 2025 download
  toi_2025_median_imputed.csv   TESS TOI table (Oct 2025) as the team saved it, after
                                median imputation; imputed cells are turned back into NaN
  k2pandc_2025.10.02.csv        K2 Planets and Candidates (Oct 2025), raw export

Outputs (data/): kepler.csv, tess.csv, k2.csv with one shared schema (COLUMNS).
Nothing is invented: a value the archive does not have stays empty.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data'
PC_TO_LY = 3.26156

COLUMNS = [
    'name', 'host', 'mission', 'disposition', 'discovery_year', 'distance_ly',
    'radius_earth', 'mass_earth', 'temperature_k', 'orbital_period_days', 'insolation',
    'transit_duration_h', 'transit_depth_ppm', 'stellar_teff_k', 'stellar_radius_sun',
    'stellar_mass_sun', 'ra', 'dec', 'catalog_id',
]


def _finish(df: pd.DataFrame, mission: str) -> pd.DataFrame:
    df['mission'] = mission
    for c in COLUMNS:
        if c not in df:
            df[c] = np.nan
    df = df[COLUMNS].copy()
    df['discovery_year'] = df['discovery_year'].astype('Int64')
    return df.sort_values(['disposition', 'name']).reset_index(drop=True)


def kepler() -> pd.DataFrame:
    vals = pd.read_csv(RAW / 'kepler_koi_values_2020.csv', comment='#', low_memory=False)
    labels = pd.read_csv(RAW / 'kepler_koi_2025_labels.csv')
    assert (vals['kepoi_name'].values == labels['kepoi_name'].values).all(), 'KOI rows out of order'
    k = vals.drop(columns=['kepler_name', 'koi_disposition', 'koi_pdisposition']).join(
        labels[['kepler_name', 'koi_disposition', 'koi_pdisposition']])
    koi = 'KOI-' + k['kepoi_name'].str[1:].str.lstrip('0')
    out = pd.DataFrame({
        'name': k['kepler_name'].fillna(koi),
        'host': k['kepler_name'].str.rsplit(' ', n=1).str[0].fillna('KIC ' + k['kepid'].astype(str)),
        'disposition': k['koi_disposition'],
        'radius_earth': k['koi_prad'],
        'temperature_k': k['koi_teq'],
        'orbital_period_days': k['koi_period'],
        'insolation': k['koi_insol'],
        'transit_duration_h': k['koi_duration'],
        'transit_depth_ppm': k['koi_depth'],
        'stellar_teff_k': k['koi_steff'],
        'stellar_radius_sun': k['koi_srad'],
        'stellar_mass_sun': k['koi_smass'],
        'ra': k['ra'], 'dec': k['dec'],
        'catalog_id': koi,
    })
    return _finish(out, 'Kepler')


def _undo_median_imputation(df: pd.DataFrame, cols: list[str], min_repeats: int = 20) -> pd.DataFrame:
    """SimpleImputer(strategy='median') leaves a tell: one value repeated many times,
    exactly equal to the column median. Real measurements almost never repeat like that."""
    df = df.copy()
    for c in cols:
        med = df[c].median()
        hits = df[c] == med
        if hits.sum() >= min_repeats:
            df.loc[hits, c] = np.nan
    return df


def tess() -> pd.DataFrame:
    t = pd.read_csv(RAW / 'toi_2025_median_imputed.csv')
    t = _undo_median_imputation(t, ['pl_orbper', 'pl_trandurh', 'pl_trandep', 'pl_rade', 'pl_insol',
                                    'pl_eqt', 'st_dist', 'st_teff', 'st_logg', 'st_rad'])
    disp = t['tfopwg_disp'].map({'CP': 'CONFIRMED', 'KP': 'CONFIRMED', 'PC': 'CANDIDATE',
                                 'APC': 'CANDIDATE', 'FP': 'FALSE POSITIVE', 'FA': 'FALSE POSITIVE'})
    toi = 'TOI-' + t['toi'].map(lambda v: f'{v:.2f}')
    out = pd.DataFrame({
        'name': toi,
        'host': 'TIC ' + t['tid'].astype('int64').astype(str),
        'disposition': disp,
        'discovery_year': pd.to_datetime(t['toi_created'], errors='coerce').dt.year,
        'distance_ly': t['st_dist'] * PC_TO_LY,
        'radius_earth': t['pl_rade'],
        'temperature_k': t['pl_eqt'],
        'orbital_period_days': t['pl_orbper'],
        'insolation': t['pl_insol'],
        'transit_duration_h': t['pl_trandurh'],
        'transit_depth_ppm': t['pl_trandep'],
        'stellar_teff_k': t['st_teff'],
        'stellar_radius_sun': t['st_rad'],
        'ra': t['ra'], 'dec': t['dec'],
        'catalog_id': toi + ' (' + t['tfopwg_disp'] + ')',
    })
    return _finish(out, 'TESS')


def k2() -> pd.DataFrame:
    k = pd.read_csv(RAW / 'k2pandc_2025.10.02.csv', comment='#', low_memory=False)
    k = k[k['default_flag'] == 1]
    out = pd.DataFrame({
        'name': k['pl_name'],
        'host': k['hostname'],
        'disposition': k['disposition'].replace({'REFUTED': 'FALSE POSITIVE'}),
        'discovery_year': k['disc_year'],
        'distance_ly': k['sy_dist'] * PC_TO_LY,
        'radius_earth': k['pl_rade'],
        'mass_earth': k['pl_bmasse'],
        'temperature_k': k['pl_eqt'],
        'orbital_period_days': k['pl_orbper'],
        'insolation': k['pl_insol'],
        'stellar_teff_k': k['st_teff'],
        'stellar_radius_sun': k['st_rad'],
        'stellar_mass_sun': k['st_mass'],
        'ra': k['ra'], 'dec': k['dec'],
        'catalog_id': k['pl_name'],
    })
    return _finish(out, 'K2')


def main() -> None:
    for fn, name in [(kepler, 'kepler'), (tess, 'tess'), (k2, 'k2')]:
        df = fn()
        path = OUT / f'{name}.csv'
        df.to_csv(path, index=False, float_format='%.6g')
        filled = df[['radius_earth', 'temperature_k', 'distance_ly', 'mass_earth']].notna().mean().round(2).to_dict()
        print(f'{path.name:11s} {len(df):5d} rows  {df.disposition.value_counts().to_dict()}  filled={filled}')


if __name__ == '__main__':
    main()
