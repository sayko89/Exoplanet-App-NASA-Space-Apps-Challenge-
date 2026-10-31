"""Exoplanet Explorer — NASA Space Apps Challenge 2025.

    streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title='Exoplanet Explorer', page_icon='assets/logo.png', layout='wide',
                   initial_sidebar_state='expanded')

st.logo('assets/logo.png', size='large')

nav = st.navigation([
    st.Page('pages/home.py', title='Home', icon=':material/public:', default=True),
    st.Page('pages/explorer.py', title='Exoplanet List', icon=':material/travel_explore:', url_path='list'),
    st.Page('pages/details.py', title='Exoplanet Details', icon=':material/language:', url_path='details'),
    st.Page('pages/classifier.py', title='AI Classifier', icon=':material/neurology:', url_path='classifier'),
    st.Page('pages/chatbot.py', title='Chatbot', icon=':material/chat:', url_path='chatbot'),
])

st.sidebar.caption('Data: NASA Exoplanet Archive · Kepler KOI, TESS TOI, K2 P&C tables.')
st.sidebar.caption('Built for the NASA Space Apps Challenge 2025.')

nav.run()
