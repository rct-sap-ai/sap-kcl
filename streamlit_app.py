import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="SAPAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

html_path = Path(__file__).parent / "landing.html"
html = html_path.read_text()

# Split at the trust bar so we can insert the button after the hero
parts = html.split('<div class="sl-trust">')

# Render hero section
st.html(parts[0])

# Login button right under the hero
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("\U0001f52c Create Your SAP", type="primary", use_container_width=True):
        st.login()

# Render the rest
st.html('<div class="sl-trust">' + parts[1])
