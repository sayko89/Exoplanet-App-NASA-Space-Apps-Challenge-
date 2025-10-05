from __future__ import annotations

import os
from pathlib import Path
import streamlit as st
from backend.data_manager import SatelliteSource, data_manager

st.set_page_config(
    page_title="Exoplanet Explorer",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global soft blue background for the app
st.markdown(
    """
    <style>
      .stApp {
        background: linear-gradient(180deg, #d6e4ff 0%, #c7d8ff 100%);
      }
      /* Sidebar: dark blue theme */
      div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2e6fd8 0%, #1d4fb5 100%);
        color: #ffffff;
      }
      div[data-testid="stSidebar"] * {
        color: rgba(255,255,255,0.92) !important;
      }
      div[data-testid="stSidebar"] a {
        color: #eaf2ff !important;
      }
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

      /* Sidebar guide panel: darker blue than site theme */
      .sidebar-guide {
        background: linear-gradient(180deg, #081a33 0%, #06152a 100%);
        color: #eaf2ff;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.25);
      }
      .sidebar-guide h4 {
        margin: 0 0 8px 0;
        font-size: 1rem;
        font-weight: 800;
        color: #ffffff;
      }
      .sidebar-guide ul {
        padding-left: 18px;
        margin: 0;
      }
      .sidebar-guide li { 
        margin: 6px 0; 
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar header/logo
logo_path = Path("assets/logo.png")
if logo_path.exists():
    st.sidebar.image(str(logo_path), width=120)
st.sidebar.title("Exoplanet Explorer")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="sidebar-guide">
      <h4>Use the pages below to navigate.</h4>
      <ul>
        <li><strong>Exoplanet List (KEPLER/TESS/K2)</strong>: Filter by satellite, select year and distance ranges, pick a planet.</li>
        <li><strong>Exoplanet Details</strong>: In-depth charts and insights; shareable URL and direct opening supported.</li>
        <li><strong>Chatbot</strong>: Landbot integration; suggestions and Q&A.</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
      .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0.5rem 0 0.3rem 0;
        background: linear-gradient(90deg, #0d6efd 0%, #6f42c1 50%, #20c997 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        letter-spacing: 0.6px;
        text-shadow: 0 2px 18px rgba(13,110,253,0.35);
        text-align: center;
      }
      .hero-sub {
        color: #6c757d;
        font-size: 1.05rem;
        margin-bottom: 0.8rem;
        text-align: center;
      }
    </style>
    <div class="hero-title">Exoplanet Explorer</div>
    <div class="hero-sub">Browse KEPLER, TESS, and K2 exoplanets</div>
    """,
    unsafe_allow_html=True,
)

# Video section
# Video başlığını kaldırdık; çerçeve efekti için stil ekliyoruz
st.markdown(
    """
    <style>
      /* Video için belirgin çerçeve ve gölge efekti */
      div[data-testid="stVideo"], div[data-testid="stIFrame"] {
        padding: 16px;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(255,255,255,0.38) 0%, rgba(255,255,255,0.18) 100%);
        border: 1px solid rgba(11,46,97,0.25);
        box-shadow: 0 18px 40px rgba(11,46,97,0.35), 0 3px 8px rgba(0,0,0,0.12);
        width: min(100%, 900px);
        margin: 16px auto;
      }
      div[data-testid="stVideo"] video,
      div[data-testid="stIFrame"] iframe {
        border-radius: 12px;
        display: block;
        width: 100%;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Yerel giriş videosu: öncelik 1004.mp4, ardından demo.mp4; aksi halde YouTube
preferred_video = Path("assets/1004.mp4")
fallback_video = Path("assets/demo.mp4")

def _render_local_video(path: Path) -> bool:
    try:
        if path.exists() and path.stat().st_size > 1024:
            # Dosya yolunu doğrudan vererek tarayıcıya akış (stream) yap
            st.video(str(path))
            return True
    except Exception:
        pass
    return False

if not _render_local_video(preferred_video):
    if not _render_local_video(fallback_video):
        st.caption("Yerel giriş videosu bulunamadı; YouTube videosu gösteriliyor.")
        st.components.v1.iframe(
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            height=360
        )

st.markdown(
    '<div class="hero-sub">Use the sidebar to explore exoplanets, view detailed charts, and chat with Landbot.</div>',
    unsafe_allow_html=True,
)
