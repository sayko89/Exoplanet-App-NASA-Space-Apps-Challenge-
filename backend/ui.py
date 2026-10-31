"""Shared look for every page: dark space theme, plot template, headers and number formatting."""
from __future__ import annotations

import math

import streamlit as st

NAVY = '#0b1430'
ACCENT = '#5eead4'
MISSION_COLORS = {'Kepler': '#60a5fa', 'TESS': '#c084fc', 'K2': '#2dd4bf'}
DISPOSITION_COLORS = {'CONFIRMED': '#22c55e', 'CANDIDATE': '#60a5fa', 'FALSE POSITIVE': '#64748b'}

# Deep-space theme: near-black navy, faint star field, glassy cards, cyan/violet accents.
_CSS = """
<style>
  .stApp {
    background:
      radial-gradient(1px 1px at 12% 18%, rgba(255,255,255,.55) 50%, transparent 51%),
      radial-gradient(1px 1px at 68% 9%, rgba(255,255,255,.45) 50%, transparent 51%),
      radial-gradient(1.5px 1.5px at 82% 42%, rgba(255,255,255,.5) 50%, transparent 51%),
      radial-gradient(1px 1px at 33% 61%, rgba(255,255,255,.35) 50%, transparent 51%),
      radial-gradient(1px 1px at 91% 77%, rgba(255,255,255,.4) 50%, transparent 51%),
      radial-gradient(1px 1px at 7% 88%, rgba(255,255,255,.35) 50%, transparent 51%),
      radial-gradient(900px 500px at 85% -10%, rgba(124,58,237,.22), transparent 60%),
      radial-gradient(800px 500px at -10% 30%, rgba(14,165,233,.14), transparent 60%),
      linear-gradient(180deg, #050816 0%, #070b1d 100%);
    background-attachment: fixed;
  }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a1027 0%, #070b1d 100%); border-right: 1px solid rgba(148,163,184,.12); }
  [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(94,234,212,.12); border-radius: 8px; }
  .page-title { text-align: center; font-weight: 800; color: #f1f5ff; font-size: clamp(28px, 4vw, 42px); margin: 4px 0 6px; letter-spacing: -.01em; }
  .page-sub { text-align: center; color: #94a3c4; font-size: clamp(14px, 2vw, 17px); margin: 0 0 18px; }
  .hero-kicker { text-align: center; font: 600 12px/1 ui-monospace, Menlo, monospace; letter-spacing: .28em; color: #5eead4; margin-top: .6rem; }
  .hero-title { font-size: clamp(38px, 6vw, 60px); font-weight: 800; text-align: center; margin: 0.5rem 0 0.2rem; letter-spacing: -.02em;
    background: linear-gradient(90deg, #93c5fd 0%, #c4b5fd 50%, #5eead4 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700;
    letter-spacing: 0.03em; color: #050816; }
  .stat { background: rgba(15,23,52,.72); border: 1px solid rgba(148,163,184,.16); color: #f1f5ff; border-radius: 14px;
    padding: 16px 18px; backdrop-filter: blur(6px); }
  .stat .v { font-size: 26px; font-weight: 800; line-height: 1.1; color: #f8fafc; }
  .stat .l { font-size: 13px; color: #94a3c4; }
  .planet-card { background: rgba(15,23,52,.66); border: 1px solid rgba(96,165,250,.22); border-radius: 12px;
    padding: 12px 14px 10px; margin-bottom: 6px; }
  .planet-card .t { color: #f1f5ff; font-weight: 800; font-size: 1.02rem; margin: 0 0 6px; }
  .planet-card .m { color: #94a3c4; font-size: 13px; line-height: 1.55; }
  .round-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 6px 0 14px; }
  .round-item { text-align: center; }
  .round { width: 112px; height: 112px; border-radius: 50%; color: #f8fafc; display: inline-flex; align-items: center;
    justify-content: center; font-weight: 800; font-size: 18px;
    background: radial-gradient(circle at 32% 28%, #1e3a8a 0%, #0b1430 70%);
    box-shadow: 0 0 0 1px rgba(94,234,212,.35), 0 0 28px rgba(94,234,212,.18); }
  .round-label { color: #94a3c4; margin-top: 8px; font-weight: 600; }
  .obj-name { text-align: center; margin: 6px 0 2px; font-size: 28px; font-weight: 800; color: #f1f5ff; }
  .muted { color: #94a3c4; }
  div[data-testid="stButton"] > button[kind="secondary"] { background: rgba(30,58,138,.55); color: #e2e8f0;
    border: 1px solid rgba(96,165,250,.35); }
  div[data-testid="stButton"] > button[kind="secondary"]:hover { background: rgba(37,99,235,.6); color: #fff; border-color: #60a5fa; }
  @media (max-width: 640px) { .round-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
"""


def _plotly_template() -> None:
    import plotly.graph_objects as go
    import plotly.io as pio
    if 'space' in pio.templates:
        return
    t = go.layout.Template(pio.templates['plotly_dark'])
    t.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    t.layout.plot_bgcolor = 'rgba(8,13,34,.65)'
    t.layout.font = dict(color='#cbd5e1')
    t.layout.xaxis.gridcolor = t.layout.yaxis.gridcolor = 'rgba(148,163,184,.12)'
    t.layout.xaxis.zerolinecolor = t.layout.yaxis.zerolinecolor = 'rgba(148,163,184,.2)'
    pio.templates['space'] = t
    pio.templates.default = 'space'


def theme() -> None:
    _plotly_template()
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
