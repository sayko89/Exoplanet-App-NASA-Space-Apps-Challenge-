"""Shared look for every page: the team's blue theme, page headers and number formatting."""
from __future__ import annotations

import math

import streamlit as st

NAVY = '#0b2e61'
BLUE = '#0d6efd'
MISSION_COLORS = {'Kepler': '#0d6efd', 'TESS': '#6f42c1', 'K2': '#20c997'}
DISPOSITION_COLORS = {'CONFIRMED': '#198754', 'CANDIDATE': '#0d6efd', 'FALSE POSITIVE': '#adb5bd'}

_CSS = """
<style>
  .stApp { background: linear-gradient(180deg, #d6e4ff 0%, #c7d8ff 100%); }
  [data-testid="stSidebar"] { background: linear-gradient(180deg, #2e6fd8 0%, #1d4fb5 100%); }
  [data-testid="stSidebar"] * { color: rgba(255,255,255,0.94) !important; }
  [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(255,255,255,0.18); border-radius: 8px; }
  .page-title { text-align: center; font-weight: 800; color: #0b2e61; font-size: clamp(28px, 4vw, 42px); margin: 4px 0 6px; }
  .page-sub { text-align: center; color: rgba(10,32,64,0.8); font-size: clamp(14px, 2vw, 17px); margin: 0 0 18px; }
  .hero-title { font-size: clamp(36px, 6vw, 56px); font-weight: 800; text-align: center; margin: 0.4rem 0 0.2rem;
    background: linear-gradient(90deg, #0d6efd 0%, #6f42c1 50%, #20c997 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700;
    letter-spacing: 0.03em; color: #fff; }
  .stat { background: #0b2e61; color: #fff; border-radius: 14px; padding: 16px 18px; box-shadow: 0 4px 14px rgba(11,46,97,0.25); }
  .stat .v { font-size: 26px; font-weight: 800; line-height: 1.1; }
  .stat .l { font-size: 13px; opacity: 0.85; }
  .planet-card { background: rgba(255,255,255,0.55); border: 1px solid rgba(13,110,253,0.35); border-radius: 12px;
    padding: 12px 14px 10px; box-shadow: 0 2px 10px rgba(13,110,253,0.15); margin-bottom: 6px; }
  .planet-card .t { color: #0b2e61; font-weight: 800; font-size: 1.02rem; margin: 0 0 6px; }
  .planet-card .m { color: rgba(10,32,64,0.78); font-size: 13px; line-height: 1.55; }
  .round-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 6px 0 14px; }
  .round-item { text-align: center; }
  .round { width: 112px; height: 112px; border-radius: 50%; background: #0b2e61; color: #fff; display: inline-flex;
    align-items: center; justify-content: center; font-weight: 800; font-size: 18px; box-shadow: 0 6px 18px rgba(11,46,97,0.3); }
  .round-label { color: rgba(10,32,64,0.85); margin-top: 8px; font-weight: 600; }
  div[data-testid="stButton"] > button[kind="secondary"] { background: #0b2e61; color: #fff; border-color: #0b2e61; }
  div[data-testid="stButton"] > button[kind="secondary"]:hover { background: #0d3a7a; color: #fff; border-color: #0d3a7a; }
  @media (max-width: 640px) { .round-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
"""


def theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header(title: str, sub: str = '') -> None:
    st.markdown(f'<h1 class="page-title">{title}</h1>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<p class="page-sub">{sub}</p>', unsafe_allow_html=True)


def year(v) -> str:
    return fmt(v, 0).replace(',', '')


def fmt(v, digits: int = 2, unit: str = '') -> str:
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return '–'
        f = float(v)
    except (TypeError, ValueError):
        return str(v) if v else '–'
    if math.isnan(f):
        return '–'
    if abs(f) >= 1000:
        s = f'{f:,.0f}'
    elif f == int(f) and digits <= 2:
        s = f'{int(f)}'
    else:
        s = f'{f:.{digits}f}'
    return f'{s} {unit}'.strip()


def badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{text}</span>'
