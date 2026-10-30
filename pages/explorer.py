import streamlit as st

from backend import ui
from backend.data_manager import DISPOSITIONS, MISSION_BLURB, Mission, load

ui.theme()
ui.header('Exoplanet List', 'Pick a mission, narrow it down, then open any object for details.')

PER_PAGE = 30

# Mission: URL (?sat=TESS) > last choice > Kepler
qp = Mission.from_label(st.query_params.get('sat'))
if qp and qp.name != st.session_state.get('_url_sat'):  # arrived with ?sat=..., not our own write
    st.session_state['mission_pick'] = qp.name
elif 'mission_pick' not in st.session_state:
    st.session_state['mission_pick'] = st.session_state.get('mission', 'KEPLER')
choice = st.segmented_control('Mission', [m.name for m in Mission], key='mission_pick', required=True,
                              label_visibility='collapsed')
mission = Mission[choice or 'KEPLER']
st.session_state['mission'] = mission.name
st.query_params['sat'] = st.session_state['_url_sat'] = mission.name
st.caption(MISSION_BLURB[mission])

df = load(mission)

with st.container(border=True):
    c1, c2 = st.columns([2, 3])
    query = c1.text_input('Search by name or host', placeholder='e.g. Kepler-186, TOI-700, K2-18')
    status = c2.multiselect('Status', DISPOSITIONS, default=['CONFIRMED', 'CANDIDATE'])
    c3, c4, c5 = st.columns(3)
    rmax = float(min(df['radius_earth'].quantile(0.99), 30)) if df['radius_earth'].notna().any() else 30.0
    radius = c3.slider('Radius (Earth = 1)', 0.0, round(rmax, 1), (0.0, round(rmax, 1)), step=0.1)
    temp = c4.slider('Equilibrium temperature (K)', 0, 4000, (0, 4000), step=50)
    sort = c5.selectbox('Sort by', ['Name', 'Radius', 'Temperature', 'Closest to Earth-like'])
    habitable = st.toggle('Only temperate, roughly Earth-sized (0.5–2 × Earth radius, 180–310 K)')

view = df[df['disposition'].isin(status)] if status else df
if query:
    q = query.strip().lower()
    view = view[view['name'].str.lower().str.contains(q, regex=False) | view['host'].str.lower().str.contains(q, regex=False)]
# Sliders only filter rows that have the value; unknowns stay unless the range was narrowed.
if radius != (0.0, round(rmax, 1)):
    view = view[view['radius_earth'].between(*radius)]
if temp != (0, 4000):
    view = view[view['temperature_k'].between(*temp)]
if habitable:
    view = view[view['radius_earth'].between(0.5, 2) & view['temperature_k'].between(180, 310)]

if sort == 'Radius':
    view = view.sort_values('radius_earth', ascending=False, na_position='last')
elif sort == 'Temperature':
    view = view.sort_values('temperature_k', na_position='last')
elif sort == 'Closest to Earth-like':
    score = (view['radius_earth'] - 1).abs() + (view['temperature_k'] - 255).abs() / 100
    view = view.assign(_s=score).sort_values('_s', na_position='last').drop(columns='_s')

total = len(view)
pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
key = (mission.name, query, tuple(status), radius, temp, sort, habitable)
if st.session_state.get('list_key') != key:
    st.session_state['list_key'] = key
    st.session_state['page'] = 1
page = min(st.session_state.get('page', 1), pages)

st.markdown(f'**{total:,}** objects · page {page} / {pages}')
if total == 0:
    st.info('Nothing matches these filters.')
    st.stop()

chunk = view.iloc[(page - 1) * PER_PAGE: page * PER_PAGE]
grid = st.columns(3)
for i, (_, r) in enumerate(chunk.iterrows()):
    with grid[i % 3]:
        color = ui.DISPOSITION_COLORS.get(r['disposition'], '#6c757d')
        st.markdown(
            f'<div class="planet-card"><div class="t">{r["name"]} {ui.badge(r["disposition"].title(), color)}</div>'
            f'<div class="m">Radius {ui.fmt(r["radius_earth"])} × Earth · {ui.fmt(r["temperature_k"], 0)} K<br>'
            f'Period {ui.fmt(r["orbital_period_days"])} d · {ui.fmt(r["distance_ly"], 0)} ly</div></div>',
            unsafe_allow_html=True)
        if st.button('View details', key=f'd_{mission.name}_{r["name"]}', width="stretch"):
            st.session_state['planet'] = r['name']
            st.switch_page('pages/details.py', query_params={'sat': mission.name, 'planet': r['name']})

if pages > 1:
    st.divider()
    p1, p2, p3 = st.columns([1, 1, 2])
    if p1.button('◀ Previous', width="stretch", disabled=page <= 1):
        st.session_state['page'] = page - 1
        st.rerun()
    if p2.button('Next ▶', width="stretch", disabled=page >= pages):
        st.session_state['page'] = page + 1
        st.rerun()
