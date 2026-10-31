import streamlit as st
import streamlit.components.v1 as components

from backend import ui

ui.theme()
ui.header('Chatbot', 'Our Landbot assistant for questions about Kepler, TESS and K2.')

# Published Landbot bot, embedded as-is.
components.html(
    """
<script type="module" src="https://cdn.landbot.io/landbot-3/landbot-3.0.0.mjs"></script>
<div id="myLandbot" style="width: 100%; height: 520px"></div>
<script type="module">
  var myLandbot = new Landbot.Container({
    container: '#myLandbot',
    configUrl: 'https://storage.googleapis.com/landbot.online/v3/H-3164358-NCBI36YJPEJWV7Y0/index.json',
  });
</script>
    """,
    height=540,
)
st.caption('The assistant is hosted by Landbot; if it does not load, a browser extension may be blocking it.')
