import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="SAPAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

html_path = Path(__file__).parent / "landing.html"
if html_path.exists():
    st.html(html_path.read_text())

st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("\U0001f52c Create Your SAP", type="primary", use_container_width=True):
        st.login()
