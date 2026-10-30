import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend import ui
from backend.data_manager import Mission, find, load

ui.theme()
ui.header('Exoplanet Details', 'Key numbers, comparison charts and a side-by-side with Earth.')

# Which object: URL (?sat=K2&planet=K2-18 b) > last opened > first in the list.
# A URL value is applied only when it differs from what this page last wrote there,
# so the pickers below keep working after the first load.
S = st.session_state
url_sat = Mission.from_label(st.query_params.get('sat'))
if url_sat and url_sat.name != S.get('_url_sat_d'):
    S['mission_d'] = url_sat.name
S.setdefault('mission_d', S.get('mission', 'KEPLER'))

c1, c2 = st.columns([1, 3])
mission = Mission[c1.selectbox('Mission', [m.name for m in Mission], key='mission_d')]
df = load(mission)
names = df['name'].tolist()

url_planet = st.query_params.get('planet')
if url_planet in names and url_planet != S.get('_url_planet'):
    S['planet_d'] = url_planet
if S.get('planet_d') not in names:
    S['planet_d'] = S.get('planet') if S.get('planet') in names else names[0]
name = c2.selectbox('Object', names, key='planet_d')

S['mission'], S['planet'] = mission.name, name
S['_url_sat_d'], S['_url_planet'] = mission.name, name
st.query_params.update({'sat': mission.name, 'planet': name})

row = find(mission, name)
f = lambda col: row.get(col) if pd.notna(row.get(col)) else None  # noqa: E731

dcolor = ui.DISPOSITION_COLORS.get(row['disposition'], '#6c757d')
st.markdown(
    f'<p style="text-align:center;margin:6px 0 2px;font-size:28px;font-weight:800;color:{ui.NAVY}">{name}</p>'
    f'<p style="text-align:center">{ui.badge(mission.value, ui.MISSION_COLORS[mission.value])} '
    f'{ui.badge(row["disposition"].title(), dcolor)} '
    f'<span style="color:rgba(10,32,64,.75)">host: {row["host"]}</span></p>',
    unsafe_allow_html=True)

st.markdown(f"""
<div class="round-grid">
  <div class="round-item"><div class="round">{ui.year(f('discovery_year'))}</div><div class="round-label">Year</div></div>
  <div class="round-item"><div class="round">{ui.fmt(f('distance_ly'), 0)}</div><div class="round-label">Distance (ly)</div></div>
  <div class="round-item"><div class="round">{ui.fmt(f('radius_earth'))}</div><div class="round-label">Radius (Earth)</div></div>
  <div class="round-item"><div class="round">{ui.fmt(f('mass_earth'))}</div><div class="round-label">Mass (Earth)</div></div>
</div>""", unsafe_allow_html=True)

# Model verdict (Kepler only): out-of-fold, so the model never saw this star while training.
if mission is Mission.KEPLER and f('ai_planet_prob') is not None:
    p = float(f('ai_planet_prob'))
    verdict = 'looks like a planet' if p >= 0.5 else 'looks like a false positive'
    st.info(f'🤖 **AI Classifier:** {p:.0%} planet-like — the signal {verdict}. '
            f'The archive says **{row["disposition"].lower()}**.')
    st.page_link('pages/classifier.py', label='How the model works', icon='🤖')

st.divider()
left, right = st.columns(2)

with left:
    st.subheader('Size vs orbit')
    plot = df.dropna(subset=['radius_earth', 'orbital_period_days'])
    plot = plot[plot['radius_earth'] > 0]
    fig = px.scatter(plot, x='orbital_period_days', y='radius_earth', color='disposition', hover_name='name',
                     log_x=True, log_y=True, opacity=0.45, render_mode='webgl',
                     color_discrete_map=ui.DISPOSITION_COLORS,
                     labels={'orbital_period_days': 'Orbital period (days)', 'radius_earth': 'Radius (Earth)',
                             'disposition': ''})
    if f('radius_earth') and f('orbital_period_days'):
        fig.add_trace(go.Scatter(x=[f('orbital_period_days')], y=[f('radius_earth')], mode='markers',
                                 marker=dict(size=16, color='red', symbol='star', line=dict(width=1, color='white')),
                                 name=name))
    fig.update_traces(marker=dict(size=4), selector=dict(mode='markers', type='scattergl'))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation='h', y=1.08))
    st.plotly_chart(fig, width='stretch')
    if mission is Mission.K2 and f('mass_earth') and f('radius_earth'):
        st.caption('Mass is known for this one, see the density card below.')

with right:
    st.subheader('Radius comparison')
    ref = pd.DataFrame({'Body': ['Earth', 'Neptune', 'Jupiter'], 'Radius (Earth)': [1.0, 3.88, 11.21]})
    if f('radius_earth'):
        ref = pd.concat([ref, pd.DataFrame({'Body': [name], 'Radius (Earth)': [f('radius_earth')]})])
    ref = ref.sort_values('Radius (Earth)')
    fig2 = px.bar(ref, x='Body', y='Radius (Earth)', color='Body',
                  color_discrete_map={'Earth': '#2e6fd8', 'Neptune': '#20c997', 'Jupiter': '#d4a373', name: '#dc3545'})
    fig2.update_layout(height=380, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, width='stretch')

# Additional metrics
st.divider()
st.subheader('Additional metrics')
mass, radius, temp = f('mass_earth'), f('radius_earth'), f('temperature_k')
density = 5.51 * mass / radius ** 3 if mass and radius else None  # Earth mean density 5.51 g/cm³

transit = f('transit_duration_h')
transit_note = 'measured'
if transit is None and f('orbital_period_days') and f('stellar_radius_sun') and f('stellar_mass_sun'):
    # T ≈ (P/π)·(R*/a), a from Kepler's third law: rough central-transit estimate
    P = f('orbital_period_days')
    a_au = f('stellar_mass_sun') ** (1 / 3) * (P / 365.25) ** (2 / 3)
    transit = (P * 24 / math.pi) * (f('stellar_radius_sun') * 0.00465047 / a_au)
    transit_note = 'estimated'

cards = [
    ('🌡️', ui.fmt(temp, 0), 'Equilibrium temperature (K)'),
    ('⚖️', ui.fmt(density), 'Density (g/cm³)'),
    ('⏱️', ui.fmt(transit), f'Transit duration (h, {transit_note})'),
    ('🕰️', ui.fmt(f('orbital_period_days')), 'Orbital period (days)'),
    ('☀️', ui.fmt(f('insolation')), 'Insolation (Earth = 1)'),
    ('⭐', ui.fmt(f('stellar_teff_k'), 0), 'Host star temperature (K)'),
]
html = '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px">'
for emoji, v, label in cards:
    html += (f'<div class="stat" style="text-align:center;padding:20px 12px"><div style="font-size:30px">{emoji}</div>'
             f'<div class="v" style="margin-top:6px">{v}</div><div class="l">{label}</div></div>')
st.markdown(html + '</div>', unsafe_allow_html=True)

# Earth comparison
st.divider()
st.subheader('Earth comparison')
if st.button('Compare with Earth', key='btn_compare'):
    st.session_state['show_compare'] = True
if st.session_state.get('show_compare'):
    pairs = [('Radius (Earth)', 1.0, radius), ('Temperature (K)', 255.0, temp),
             ('Insolation (Earth = 1)', 1.0, f('insolation')), ('Density (g/cm³)', 5.51, density)]
    cols = st.columns(4)
    for col, (label, earth, val) in zip(cols, pairs):
        with col:
            st.markdown(f'**{label}**')
            if val is None:
                st.caption('Not available for this object.')
                continue
            d = pd.DataFrame({'': ['Earth', name], label: [earth, val]})
            fig3 = px.bar(d, x='', y=label, color='', color_discrete_sequence=['#2e6fd8', '#dc3545'])
            fig3.update_layout(height=260, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig3, width='stretch')
    st.caption("Earth's equilibrium temperature is about 255 K (its surface averages ~288 K thanks to the atmosphere).")

with st.expander('Raw record'):
    st.dataframe(row.to_frame().T, width='stretch', hide_index=True)
