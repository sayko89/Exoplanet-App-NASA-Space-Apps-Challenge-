import pandas as pd
import plotly.express as px
import streamlit as st

from backend import ui
from backend.classifier import KeplerClassifier
from backend.data_manager import MODELS, Mission, load

ui.theme()
ui.header('AI Classifier', 'Is a Kepler transit signal a real planet, or a false positive? A LightGBM model trained on 9,564 Kepler objects answers.')


@st.cache_resource(show_spinner=False)
def model() -> KeplerClassifier:
    return KeplerClassifier(MODELS / 'kepler_lgbm.json', MODELS / 'kepler_metrics.json')


clf = model()
m = clf.metrics

a, b, c, d = st.columns(4)
for col, v, l in [(a, f"{m['auc_mean']:.3f}", 'ROC AUC (5-fold CV)'), (b, f"{m['ap_mean']:.3f}", 'Average precision'),
                  (c, f"{m['accuracy_at_0_5']:.1%}", 'Accuracy at 0.5'), (d, f"{m['n_objects']:,}", 'training objects')]:
    col.markdown(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

st.write('')
st.caption('Cross-validation is grouped by star, so planets of the same star are never on both sides of a split. '
           'The model only sees transit and stellar measurements, not the archive\'s vetting score or flags.')

tab1, tab2, tab3 = st.tabs(['Check a Kepler object', 'Try your own numbers', 'How it works'])

LABELS = {
    'koi_period': ('Orbital period', 'days'), 'koi_duration': ('Transit duration', 'hours'),
    'koi_depth': ('Transit depth', 'ppm'), 'koi_model_snr': ('Signal-to-noise ratio', ''),
    'koi_num_transits': ('Number of transits', ''), 'koi_teq': ('Equilibrium temperature', 'K'),
    'koi_prad': ('Planet radius', 'Earth radii'), 'koi_sma': ('Orbit size (semi-major axis)', 'AU'),
    'koi_steff': ('Star temperature', 'K'), 'koi_srad': ('Star radius', 'Sun = 1'), 'koi_smass': ('Star mass', 'Sun = 1'),
}


def gauge(p: float) -> None:
    color = '#5eead4' if p >= 0.5 else '#94a3b8'
    word = 'planet-like signal' if p >= 0.5 else 'likely false positive'
    st.markdown(
        f'<div class="stat" style="text-align:center"><div class="v" style="font-size:44px;color:{color}">{p:.0%}</div>'
        f'<div class="l">{word}</div></div>', unsafe_allow_html=True)
    st.progress(p)


with tab1:
    kep = load(Mission.KEPLER).dropna(subset=['ai_planet_prob'])
    status = st.radio('Show', ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE'], horizontal=True,
                      format_func=str.title)
    pool = kep[kep['disposition'] == status].sort_values('ai_planet_prob', ascending=status == 'FALSE POSITIVE')
    pick = st.selectbox('Kepler object', pool['name'].tolist())
    r = pool[pool['name'] == pick].iloc[0]
    l, rr = st.columns([1, 2])
    with l:
        gauge(float(r['ai_planet_prob']))
    with rr:
        st.markdown(f"**{pick}** · archive status: **{r['disposition'].lower()}**")
        st.markdown(f"Radius {ui.fmt(r['radius_earth'])} × Earth · {ui.fmt(r['temperature_k'], 0)} K · "
                    f"period {ui.fmt(r['orbital_period_days'])} d · depth {ui.fmt(r['transit_depth_ppm'], 0)} ppm")
        st.caption('This score is out-of-fold: it comes from a model that never saw this star during training.')
        if st.button('Open details', key='to_details'):
            st.switch_page('pages/details.py', query_params={'sat': 'KEPLER', 'planet': pick})
    if status == 'CANDIDATE':
        top = pool.head(10)[['name', 'ai_planet_prob', 'radius_earth', 'temperature_k', 'orbital_period_days']]
        st.markdown('**Most planet-like open candidates**')
        st.dataframe(top.rename(columns={'name': 'Object', 'ai_planet_prob': 'Planet-like', 'radius_earth': 'Radius (× Earth)',
                                         'temperature_k': 'Temp (K)', 'orbital_period_days': 'Period (d)'}),
                     hide_index=True, width='stretch',
                     column_config={'Planet-like': st.column_config.ProgressColumn(format='percent', min_value=0, max_value=1)})

with tab2:
    st.write('Start from a typical Kepler object (the median of every feature) and move the sliders.')
    med = clf.medians
    ranges = {
        'koi_period': (0.3, 700.0), 'koi_duration': (0.2, 24.0), 'koi_depth': (10.0, 50000.0),
        'koi_model_snr': (1.0, 500.0), 'koi_num_transits': (1.0, 2000.0), 'koi_teq': (100.0, 4000.0),
        'koi_prad': (0.3, 30.0), 'koi_sma': (0.005, 2.0), 'koi_steff': (3000.0, 9000.0),
        'koi_srad': (0.1, 5.0), 'koi_smass': (0.1, 2.5),
    }
    values = {}
    cols = st.columns(2)
    for i, feat in enumerate(clf.features):
        lo, hi = ranges[feat]
        label, unit = LABELS[feat]
        values[feat] = cols[i % 2].slider(f'{label} ({unit})' if unit else label, lo, hi,
                                          float(min(max(med[feat], lo), hi)), key=f's_{feat}')
    st.write('')
    gauge(clf.predict(values))

with tab3:
    st.markdown(f"""
**Task.** {m['label'].capitalize()}. Kepler's pipeline flags thousands of periodic dips in starlight;
most are planets, many are eclipsing binaries or instrument noise. The model learns which transit shapes and host
stars tend to be real.

**Data.** Kepler Objects of Interest cumulative table (NASA Exoplanet Archive), {m['n_objects']:,} objects,
{m['n_positive']:,} confirmed or candidate.

**Model.** LightGBM gradient-boosted trees ({m['n_trees']} trees), balanced class weights, median imputation.
Evaluation: {m['cv']}.
""")
    imp = pd.DataFrame({'feature': [LABELS[k][0] for k in m['importance_gain']],
                        'importance': list(m['importance_gain'].values())}).sort_values('importance')
    fig = px.bar(imp, x='importance', y='feature', orientation='h', labels={'importance': 'Share of total gain', 'feature': ''})
    fig.update_traces(marker_color='#5eead4')
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width='stretch')
    cm = m['confusion_matrix']
    st.markdown('**Confusion matrix (out-of-fold, threshold 0.5)**')
    st.dataframe(pd.DataFrame(cm, index=['actual false positive', 'actual planet-like'],
                              columns=['predicted false positive', 'predicted planet-like']), width='stretch')
