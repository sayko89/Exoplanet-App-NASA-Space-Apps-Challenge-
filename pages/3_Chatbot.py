import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chatbot", layout="wide")

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
      div[data-testid="stSidebar"] * { color: rgba(255,255,255,0.92) !important; }
      div[data-testid="stSidebar"] a { color: #eaf2ff !important; }
      div[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.18); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Chatbot")
st.caption("Simple placeholder chat.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Mesajları göster
for role, content in st.session_state.chat_messages:
    with st.chat_message(role):
        st.markdown(content)

# Landbot embed (published code)
components.html(
    """
<script type="module" src="https://cdn.landbot.io/landbot-3/landbot-3.0.0.mjs"></script>
<div id="myLandbot" style="width: 100%; height: 500px"></div>
<script type="module">
  var myLandbot = new Landbot.Container({
    container: '#myLandbot',
    configUrl: 'https://storage.googleapis.com/landbot.online/v3/H-3164358-NCBI36YJPEJWV7Y0/index.json',
  });
</script>
    """,
    height=520,
)