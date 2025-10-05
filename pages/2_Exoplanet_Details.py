import streamlit as st
import pandas as pd
import plotly.express as px
import math
from pathlib import Path
from backend.data_manager import SatelliteSource, data_manager

st.set_page_config(page_title="Exoplanet Details", layout="wide")

# Global soft blue background for the page
st.markdown(
    """
    <style>
      .stApp {
        background: linear-gradient(180deg, #d6e4ff 0%, #c7d8ff 100%);
      }
      div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2e6fd8 0%, #1d4fb5 100%);
        color: #ffffff;
      }
      div[data-testid="stSidebar"] * { color: rgba(255,255,255,0.92) !important; }
      div[data-testid="stSidebar"] a { color: #eaf2ff !important; }
      div[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.18); }
      /* Page navigation block inside sidebar */
      nav[data-testid="stSidebarNav"] {
        background: linear-gradient(180deg, #2e6fd8 0%, #1d4fb5 100%);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 12px;
        padding: 10px 12px;
        margin: 8px 6px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.20);
      }
      nav[data-testid="stSidebarNav"] * {
        color: #ffffff !important;
      }
      /* Centered title, subtitle and meta for details page */
      .details-title {
        text-align: center;
        font-weight: 800;
        color: #0b2e61;
        font-size: clamp(28px, 4vw, 42px);
        margin: 4px 0 10px 0;
      }
      .details-sub {
        text-align: center;
        color: rgba(10,32,64,0.85);
        font-size: clamp(14px, 2.2vw, 18px);
        margin: 0 0 18px 0;
      }
      .details-meta {
        text-align: center;
        color: rgba(10,32,64,0.75);
        margin: 4px 0;
      }

      /* Additional Metrics card grid */
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 10px 0 0 0;
      }
      .metric-card {
        background: #0b2e61;
        color: #ffffff;
        border: 1px solid rgba(13,110,253,0.25);
        border-radius: 14px;
        height: 160px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(11,46,97,0.28);
        text-align: center;
      }
      .metric-emoji { font-size: 34px; line-height: 1; margin-bottom: 8px; }
      .metric-value { font-size: 20px; font-weight: 700; margin: 0; }
      .metric-label { font-size: 13px; opacity: 0.9; margin: 2px 0 0 0; }

      /* Core metrics as round dark-blue buttons */
      .metric-round-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        align-items: start;
        margin: 6px 0 12px 0;
      }
      .metric-round-item { text-align: center; }
      .round-btn {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: #0b2e61;
        color: #ffffff;
        border: 1px solid rgba(13,110,253,0.25);
        box-shadow: 0 6px 18px rgba(11,46,97,0.32);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 0.2px;
        transition: background 0.2s ease, transform 0.15s ease;
      }
      .round-btn:hover { background: #0d3a7a; transform: translateY(-1px); }
      .round-label { color: rgba(10,32,64,0.85); margin-top: 8px; font-weight: 600; }

      
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="details-title">Exoplanet Details</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="details-sub">Select a planet from the chosen satellite to view key metrics and comparison charts.</p>',
    unsafe_allow_html=True,
)

# Uydu seçimi
sat_labels = ["KEPLER", "TESS", "K2"]
label_to_enum = {"KEPLER": SatelliteSource.KEPLER, "TESS": SatelliteSource.TESS, "K2": SatelliteSource.COROT}
enum_to_label = {SatelliteSource.KEPLER: "KEPLER", SatelliteSource.TESS: "TESS", SatelliteSource.COROT: "K2"}

# URL parametreleri (yalnızca st.query_params)
def _qp_get(name: str):
    val = st.query_params.get(name)
    if isinstance(val, (list, tuple)):
        return val[0] if val else None
    return val

qp_sat_label = _qp_get("sat") or _qp_get("satellite")
default_label = qp_sat_label if (qp_sat_label in sat_labels) else st.session_state.get("selected_satellite", "KEPLER")
selected_label = default_label
st.session_state["selected_satellite"] = selected_label
st.markdown(f'<p class="details-meta">Satellite: {selected_label}</p>', unsafe_allow_html=True)

# Veri yükleme
df = data_manager.load_satellite_data(label_to_enum[selected_label]).copy()
# CoRoT verisini K2 etiketi ile göster
df["satellite_source"] = df.get("satellite_source", enum_to_label[label_to_enum[selected_label]])
df["satellite_source"] = df["satellite_source"].replace({"CoRoT": "K2"})

# Gezegen adı listesi
name_col = "name"
planet_names = sorted(df[name_col].dropna().astype(str).unique())

# Geçmiş seçim ve URL parametresi
qp_planet = _qp_get("planet")
default_planet = qp_planet if (qp_planet in planet_names) else st.session_state.get("selected_planet")
selected_planet = default_planet if (default_planet in planet_names) else (planet_names[0] if planet_names else None)
st.session_state["selected_planet"] = selected_planet
if selected_planet:
    st.query_params.update({"sat": selected_label, "planet": selected_planet})
    st.markdown(f'<p class="details-meta">Planet: {selected_planet}</p>', unsafe_allow_html=True)
else:
    st.info("Bir gezegen seçilmedi. Lütfen Exoplanet Listesi sayfasından bir gezegen kartındaki 'Detaya Git' ile gelin.")
    st.stop()

# Seçilen gezegen satırı
row = df[df[name_col] == selected_planet].iloc[0] if selected_planet in planet_names else None

st.divider()

def fmt(v):
    try:
        if pd.isna(v):
            return "-"
        if isinstance(v, (int, float)):
            return f"{v:.2f}"
        return str(v)
    except Exception:
        return "-"

yr_txt = fmt(row.get("discovery_year", row.get("year", None)))
dist_txt = fmt(row.get("distance_ly", row.get("distance", None)))
rad_txt = fmt(row.get("radius_earth", row.get("radius", None)))
mass_txt = fmt(row.get("mass_earth", row.get("mass", None)))

st.markdown(
    f"""
    <div class="metric-round-grid">
      <div class="metric-round-item">
        <div class="round-btn">{yr_txt}</div>
        <div class="round-label">Year</div>
      </div>
      <div class="metric-round-item">
        <div class="round-btn">{dist_txt}</div>
        <div class="round-label">Distance (ly)</div>
      </div>
      <div class="metric-round-item">
        <div class="round-btn">{rad_txt}</div>
        <div class="round-label">Radius (Earth)</div>
      </div>
      <div class="metric-round-item">
        <div class="round-btn">{mass_txt}</div>
        <div class="round-label">Mass (Earth)</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col5, col6 = st.columns(2)
# Kapsam düzeltmesi: rcol/mcol tek yerde hesaplanır
rcol = "radius_earth"
mcol = "mass_earth"
with col5:
    st.subheader("Mass vs Radius Distribution")
    if rcol and mcol:
        fig = px.scatter(
            df,
            x=mcol,
            y=rcol,
            hover_name=name_col,
            color="satellite_source" if "satellite_source" in df.columns else None,
            labels={mcol: "Mass (Earth)", rcol: "Radius (Earth)"},
        )
        # Seçili gezegeni vurgula
        sel = df[df[name_col] == selected_planet]
        if not sel.empty:
            fig.add_scatter(
                x=sel[mcol],
                y=sel[rcol],
                mode="markers",
                marker=dict(size=14, color="red", symbol="star"),
                name="Selected Planet",
                hovertext=sel[name_col],
            )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Mass and radius columns not found in the dataset.")

with col6:
    st.subheader("Radius Comparison")
    if rcol:
        top = df[[name_col, rcol]].dropna().sort_values(rcol, ascending=False).head(15)
        fig2 = px.bar(top, x=name_col, y=rcol, labels={name_col: "Planet", rcol: "Radius (Earth)"})
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Radius column not found in the dataset.")

st.subheader("Raw Record")
st.dataframe(row.to_frame().T, use_container_width=True)

# Ek metrikler: Sıcaklık, Yoğunluk ve Transit Süresi
st.divider()
st.subheader("Additional Metrics")

def safe_float(v):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return None
        return float(v)
    except Exception:
        return None

temp_val = row.get("temperature_k", row.get("equilibrium_temp", None))
mass_e = row.get("mass_earth", row.get("planet_mass", None))
radius_e = row.get("radius_earth", row.get("planet_radius", None))
orbital_period_days = row.get("orbital_period", row.get("period", None))
stellar_radius_solar = row.get("stellar_radius", None)
stellar_mass_solar = row.get("stellar_mass", None)

mass_e_f = safe_float(mass_e)
radius_e_f = safe_float(radius_e)
temp_f = safe_float(temp_val)
P_days_f = safe_float(orbital_period_days)
Rstar_solar_f = safe_float(stellar_radius_solar)
Mstar_solar_f = safe_float(stellar_mass_solar)

# Yoğunluk hesapları
density_earth_units = None
density_g_cm3 = None
if mass_e_f is not None and radius_e_f is not None and radius_e_f > 0:
    density_earth_units = mass_e_f / (radius_e_f ** 3)
    density_g_cm3 = 5.51 * density_earth_units  # Dünya ortalama yoğunluğu ~5.51 g/cm³

# Transit süresi (yaklaşık): T ≈ (P/π) * (R* / a)
transit_hours = None
if P_days_f is not None and Rstar_solar_f is not None and Mstar_solar_f is not None and P_days_f > 0 and Mstar_solar_f > 0:
    P_years = P_days_f / 365.25
    # Yarı büyük eksen a (AU) ~ (M*)^(1/3) * (P_years)^(2/3)
    a_AU = (Mstar_solar_f ** (1/3)) * (P_years ** (2/3))
    P_hours = P_days_f * 24.0
    Rstar_AU = Rstar_solar_f * 0.00465047  # 1 R_sun ≈ 0.00465047 AU
    if a_AU > 0:
        transit_hours = (P_hours / math.pi) * (Rstar_AU / a_AU)

temp_txt = fmt(temp_f) if temp_f is not None else "-"
den_e_txt = fmt(density_earth_units) if density_earth_units is not None else "-"
den_g_txt = fmt(density_g_cm3) if density_g_cm3 is not None else "-"
tran_txt = fmt(transit_hours) if transit_hours is not None else "-"
peri_txt = fmt(P_days_f) if P_days_f is not None else "-"

st.markdown(
    f"""
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-emoji">🌡️</div>
        <p class="metric-value">{temp_txt}</p>
        <p class="metric-label">Temperature (K)</p>
      </div>
      <div class="metric-card">
        <div class="metric-emoji">⚖️</div>
        <p class="metric-value">{den_e_txt}</p>
        <p class="metric-label">Density (Earth=1)</p>
      </div>
      <div class="metric-card">
        <div class="metric-emoji">🧪</div>
        <p class="metric-value">{den_g_txt}</p>
        <p class="metric-label">Density (g/cm³)</p>
      </div>
      <div class="metric-card">
        <div class="metric-emoji">⏱️</div>
        <p class="metric-value">{tran_txt}</p>
        <p class="metric-label">Transit Duration (hours)</p>
      </div>
      <div class="metric-card">
        <div class="metric-emoji">🕰️</div>
        <p class="metric-value">{peri_txt}</p>
        <p class="metric-label">Orbital Period (days)</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dünya animasyonu (isteğe bağlı gösterim)
st.divider()
st.subheader("Earth Comparisons")



# Paneli açma butonu (yalnızca Dünya ile Karşılaştırma butonu)
if st.button("Compare with Earth", key="btn_show_compare", use_container_width=False):
    st.session_state["show_compare_panel"] = True

# Karşılaştırma paneli: Dünya vs Seçili Gezegen (Kütle, Sıcaklık, Yoğunluk)
if st.session_state.get("show_compare_panel", False):
    st.divider()
    st.subheader("Earth Comparison Panel")
    st.caption("The comparison panel is shown below.")

    earth_vals = {
        "mass_earth": 1.0,            # Dünya kütlesi (Dünya birimi)
        "temperature_k": 288.0,       # Dünya ortalama sıcaklık ~288K
        "density_g_cm3": 5.51,        # Dünya ortalama yoğunluk ~5.51 g/cm³
    }

    c1, c2, c3 = st.columns(3)

    # Kütle karşılaştırması
    with c1:
        st.markdown("**Mass Comparison**")
        if mass_e_f is not None:
            df_mass = pd.DataFrame({
                "Category": ["Earth", "Selected Planet"],
                "Mass (Earth)": [earth_vals["mass_earth"], mass_e_f],
            })
            fig_m = px.bar(df_mass, x="Category", y="Mass (Earth)", color="Category")
            fig_m.update_layout(showlegend=False)
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.info("Mass information is missing; the comparison chart could not be created.")

    # Sıcaklık karşılaştırması
    with c2:
        st.markdown("**Temperature Comparison**")
        if temp_f is not None:
            df_temp = pd.DataFrame({
                "Category": ["Earth", "Selected Planet"],
                "Temperature (K)": [earth_vals["temperature_k"], temp_f],
            })
            fig_t = px.bar(df_temp, x="Category", y="Temperature (K)", color="Category")
            fig_t.update_layout(showlegend=False)
            st.plotly_chart(fig_t, use_container_width=True)
        else:
            st.info("Temperature information is missing; the comparison chart could not be created.")

    # Yoğunluk karşılaştırması
    with c3:
        st.markdown("**Density Comparison**")
        if density_g_cm3 is not None:
            df_den = pd.DataFrame({
                "Category": ["Earth", "Selected Planet"],
                "Density (g/cm³)": [earth_vals["density_g_cm3"], density_g_cm3],
            })
            fig_d = px.bar(df_den, x="Category", y="Density (g/cm³)", color="Category")
            fig_d.update_layout(showlegend=False)
            st.plotly_chart(fig_d, use_container_width=True)
        else:
            st.info("Density information is missing; the comparison chart could not be created.")

    st.caption("Note: Comparisons are simple and visibility-focused; Earth averages ~288K for temperature and ~5.51 g/cm³ for density.")