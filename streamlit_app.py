import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="SAPAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    logo_path = Path(__file__).parent / "sapai_logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=280)

html_path = Path(__file__).parent / "landing.html"
html = html_path.read_text()

parts = html.split('<p class="sl-hero-sub">')

st.html(parts[0])

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Draft Your SAP", type="primary", use_container_width=True):
        st.login()

st.html('<p class="sl-hero-sub">' + parts[1])
