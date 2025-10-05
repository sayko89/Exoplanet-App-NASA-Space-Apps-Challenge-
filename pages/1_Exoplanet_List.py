import streamlit as st
import pandas as pd
from backend.data_manager import SatelliteSource, data_manager

st.set_page_config(page_title="Exoplanet List", layout="wide")

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

      /* Centered title and subtitle for the list page */
      .page-title { 
        text-align: center; 
        font-weight: 800; 
        color: #0b2e61; 
        font-size: clamp(28px, 4vw, 42px);
        margin: 4px 0 10px 0;
      }
      .page-sub { 
        text-align: center; 
        color: rgba(10,32,64,0.85);
        font-size: clamp(14px, 2.2vw, 18px);
        margin: 0 0 18px 0;
      }

      /* Dark blue buttons with readable white text */
      div[data-testid="stButton"] > button {
        background-color: #0b2e61 !important;
        color: #ffffff !important;
        border-color: #0b2e61 !important;
      }
      div[data-testid="stButton"] > button:hover {
        background-color: #0d3a7a !important;
        border-color: #0d3a7a !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Centered page title and caption
st.markdown('<h1 class="page-title">Exoplanet List</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Click KEPLER, TESS, or K2; open details from the planet card.</p>', unsafe_allow_html=True)

# Güvenli URL parametre okuma (yalnızca st.query_params)
def _get_query_param(name: str):
    val = st.query_params.get(name)
    if isinstance(val, (list, tuple)):
        return val[0] if val else None
    return val

sat_labels = ["TESS", "K2", "KEPLER"]
label_to_enum = {"KEPLER": SatelliteSource.KEPLER, "TESS": SatelliteSource.TESS, "K2": SatelliteSource.COROT}

# Başlangıç uydu belirleme: URL veya session
qp_sat = _get_query_param("sat")
initial_sat = None
if isinstance(qp_sat, str) and qp_sat.upper() in sat_labels:
    initial_sat = qp_sat.upper()
elif isinstance(st.session_state.get("selected_satellite"), str) and st.session_state.get("selected_satellite") in sat_labels:
    initial_sat = st.session_state.get("selected_satellite")

# Üç butonlu uydu seçimi
cols = st.columns(3)
with cols[0]:
    if st.button("TESS", use_container_width=True):
        st.session_state["selected_satellite"] = "TESS"
        initial_sat = "TESS"
with cols[1]:
    if st.button("K2", use_container_width=True):
        st.session_state["selected_satellite"] = "K2"
        initial_sat = "K2"
with cols[2]:
    if st.button("KEPLER", use_container_width=True):
        st.session_state["selected_satellite"] = "KEPLER"
        initial_sat = "KEPLER"

if not initial_sat:
    st.info("Select a satellite (TESS, K2, or KEPLER) and view planets.")
    st.stop()

# Seçilen uydu verisini yükle
try:
    df = data_manager.load_satellite_data(label_to_enum[initial_sat]).copy()
    # CoRoT verisini K2 etiketi ile normalleştir
    df["satellite_source"] = df.get("satellite_source", initial_sat)
    df["satellite_source"] = df["satellite_source"].replace({"CoRoT": "K2"})
    # TESS kartlarındaki gezegenlerden 4506 tanesini sil
    if initial_sat == "TESS":
        remove_n = 4506
        if len(df) > remove_n:
            df = df.iloc[:-remove_n].copy()
        else:
            df = df.iloc[0:0].copy()
    # KEPLER kartlarındaki "Unknown" gezegenleri filtrele
    if initial_sat == "KEPLER" and "name" in df.columns:
        df = df[~df["name"].astype(str).str.strip().str.lower().eq("unknown")].copy()
except Exception as e:
    st.error(f"Veri yüklenirken hata: {e}")
    st.stop()

if df.empty or "name" not in df.columns:
    st.warning("Seçilen uydu için gezegen listesi bulunamadı.")
    st.stop()

name_col = "name"

# Gezegen kartları: seçimi kaldır, butonla detay sayfasına yönlendir

def fmt(v):
    try:
        import pandas as pd
        if pd.isna(v):
            return "-"
        if isinstance(v, (int, float)):
            return f"{v:.2f}"
        return str(v)
    except Exception:
        return "-"

# Gösterilecek alanları hazırla
cols_to_show = [c for c in [name_col, "discovery_year", "distance_ly", "radius_earth", "mass_earth"] if c in df.columns]
df_view = df[cols_to_show].copy()
df_view = df_view.dropna(subset=[name_col]).reset_index(drop=True)

# Kartları 3 kolonlu grid halinde göster (sayfalama veya tümünü göster)
st.subheader("Planet Cards")
st.markdown(
    """
    <style>
      .planet-card { 
        background: rgba(13,110,253,0.08);
        border: 1px solid #0d6efd;
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 2px 10px rgba(13,110,253,0.22);
      }
      .planet-card .planet-title {
        color: #0d6efd;
        font-weight: 700;
        font-size: 1.05rem;
        margin: 0 0 10px 0;
      }
      .planet-card .planet-btn {
        display: inline-block;
        background: #0d6efd;
        color: #fff;
        text-decoration: none;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 600;
      }
      .planet-card .planet-btn:hover { background: #0b5ed7; }
    </style>
    """,
    unsafe_allow_html=True,
)

items_per_page = st.session_state.get("items_per_page", 30)
total_items = len(df_view)

current_page = st.session_state.get("current_page", 1)
if items_per_page <= 0:
    items_per_page = 30
total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
current_page = max(1, min(current_page, total_pages))
start_idx = (current_page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, total_items)
st.session_state["items_per_page"] = items_per_page
st.session_state["current_page"] = current_page

grid_cols = st.columns(3)
for i in range(start_idx, end_idx):
    row = df_view.iloc[i]
    col = grid_cols[(i - start_idx) % 3]
    with col:
        name = fmt(row.get(name_col))
        # Gerçek kart görünümü (mavi tema), küçük punto bilgileri kaldırıldı
        st.markdown(
            f"""
            <div class=\"planet-card\"> 
              <div class=\"planet-title\">{name}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Details", key=f"go_detail_{current_page}_{i}", use_container_width=True):
            st.session_state["selected_satellite"] = initial_sat
            st.session_state["selected_planet"] = name
            st.query_params.update({"sat": initial_sat, "planet": name})
            st.switch_page("pages/2_Exoplanet_Details.py")

# Sayfalama kontrolleri
if total_pages > 1:
    st.divider()
    pcols = st.columns([1, 1, 2])
    with pcols[0]:
        if st.button("◀️ Previous", use_container_width=True) and st.session_state["current_page"] > 1:
            st.session_state["current_page"] -= 1
            st.rerun()
    with pcols[1]:
        if st.button("Next ▶️", use_container_width=True) and st.session_state["current_page"] < total_pages:
            st.session_state["current_page"] += 1
            st.rerun()
    with pcols[2]:
        st.caption(f"Page {st.session_state['current_page']} / {total_pages} • Total {total_items} planets")

# Alt tablo kaldırıldı; gezegenler kart görünümünde gösterilmeye devam ediyor.