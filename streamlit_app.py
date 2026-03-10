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

# Split after the tagline, before the hero-sub paragraph
parts = html.split('<p class="sl-hero-sub">')

# Render hero up to tagline
st.html(parts[0])

# Login button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Draft Your SAP", type="primary", use_container_width=True):
        st.login()

# Render the rest
st.html('<p class="sl-hero-sub">' + parts[1])
