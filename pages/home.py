from pathlib import Path

import plotly.express as px
import streamlit as st

from backend import ui
from backend.data_manager import ROOT, Mission, load, load_all

ui.theme()

st.markdown('<div class="hero-kicker">NASA SPACE APPS CHALLENGE 2025</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Exoplanet Explorer</div>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Browse every Kepler, TESS and K2 object of interest, '
            'and ask a machine-learning model whether a transit signal looks like a real planet.</p>',
            unsafe_allow_html=True)

# Intro video, when one is shipped with the repo (assets/intro.mp4).
video = ROOT / 'assets' / 'intro.mp4'
if video.exists() and video.stat().st_size > 1024:
    _, mid, _ = st.columns([1, 4, 1])
    mid.video(str(video))

all_ = load_all()
cols = st.columns(4)
stats = [
    (f'{len(all_):,}', 'objects of interest'),
    (f"{(all_['disposition'] == 'CONFIRMED').sum():,}", 'confirmed planets'),
    (f"{(all_['disposition'] == 'CANDIDATE').sum():,}", 'candidates still open'),
    ('3', 'missions: Kepler · TESS · K2'),
]
for c, (v, l) in zip(cols, stats):
    c.markdown(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

st.write('')
st.subheader('Where they are on the sky')
sky = all_.dropna(subset=['ra', 'dec'])
fig = px.scatter(sky, x='ra', y='dec', color='mission', hover_name='name',
                 color_discrete_map=ui.MISSION_COLORS, opacity=0.55, render_mode='webgl',
                 labels={'ra': 'Right ascension (°)', 'dec': 'Declination (°)', 'mission': 'Mission'})
fig.update_traces(marker=dict(size=3))
fig.update_layout(height=440, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor='rgba(2,4,12,.85)',
                  legend=dict(orientation='h', y=1.02, x=0, yanchor='bottom', title=None))
fig.update_xaxes(range=[360, 0], gridcolor='rgba(255,255,255,0.08)')
fig.update_yaxes(range=[-90, 90], gridcolor='rgba(255,255,255,0.08)')
st.plotly_chart(fig, width="stretch")
st.caption('Kepler stared at one patch of Cygnus–Lyra; K2 stepped along the ecliptic; TESS covers almost the whole sky.')

st.subheader('Start here')
a, b, c = st.columns(3)
with a:
    st.markdown('**🔭 Exoplanet List**  \nFilter by mission, status, size and temperature; open any object.')
    st.page_link('pages/explorer.py', label='Open the list', icon='🔭')
with b:
    st.markdown('**🌍 Exoplanet Details**  \nKey numbers, comparison charts and a side-by-side with Earth.')
    st.page_link('pages/details.py', label='Open details', icon='🌍')
with c:
    st.markdown('**🤖 AI Classifier**  \nLightGBM model: planet-like signal or false positive?')
    st.page_link('pages/classifier.py', label='Try the model', icon='🤖')
