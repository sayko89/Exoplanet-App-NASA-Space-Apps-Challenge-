"""Smoke and data tests. Run with: pytest -q"""
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
PAGES = ['pages/home.py', 'pages/explorer.py', 'pages/details.py', 'pages/classifier.py', 'pages/chatbot.py']


def run(page: str | None = None, **query) -> AppTest:
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60)
    for k, v in query.items():
        at.query_params[k] = v
    at.run()
    if page:
        at.switch_page(page)
        at.run()
    assert not at.exception, [e.message for e in at.exception]
    return at


@pytest.mark.parametrize('page', PAGES)
def test_every_page_renders(page):
    run(page)


@pytest.mark.parametrize('mission', ['KEPLER', 'TESS', 'K2'])
def test_explorer_lists_each_mission(mission):
    at = run('pages/explorer.py', sat=mission)
    assert any('objects · page' in m.value for m in at.markdown)


def test_details_deep_link():
    at = run('pages/details.py', sat='K2', planet='K2-18 b')
    assert at.selectbox[1].value == 'K2-18 b'
    assert any('>2.37<' in m.value and 'Radius' in m.value for m in at.markdown)


@pytest.mark.parametrize('name', ['kepler', 'tess', 'k2'])
def test_datasets_are_physical(name):
    df = pd.read_csv(ROOT / 'data' / f'{name}.csv')
    assert len(df) > 1000
    assert df['name'].is_unique or name == 'k2'
    assert (df['radius_earth'].dropna() > 0).all()
    assert (df['temperature_k'].dropna() > 0).all()
    assert (df['distance_ly'].dropna() > 0).all()
    assert set(df['disposition'].unique()) <= {'CONFIRMED', 'CANDIDATE', 'FALSE POSITIVE'}


def test_known_planets_have_archive_values():
    k = pd.read_csv(ROOT / 'data' / 'kepler.csv').set_index('name')
    assert k.loc['Kepler-186 f', 'radius_earth'] == pytest.approx(1.18, abs=0.01)
    t = pd.read_csv(ROOT / 'data' / 'tess.csv').set_index('name')
    assert t.loc['TOI-700.04', 'disposition'] == 'CONFIRMED'


def test_classifier_metrics_and_inference():
    from backend.classifier import KeplerClassifier
    clf = KeplerClassifier(ROOT / 'models' / 'kepler_lgbm.json', ROOT / 'models' / 'kepler_metrics.json')
    m = json.loads((ROOT / 'models' / 'kepler_metrics.json').read_text())
    assert m['auc_mean'] > 0.85
    p = clf.predict({})  # all medians
    assert 0 <= p <= 1
    # an obvious eclipsing binary: huge, deep, hot
    eb = clf.predict({'koi_prad': 30, 'koi_depth': 50000, 'koi_teq': 3000, 'koi_model_snr': 500})
    assert eb < 0.5
