import streamlit as st

st.set_page_config(
    page_title="SAP AutoCode",
    page_icon="📊",
    layout="wide"
)

st.title("🏥 KCL Clinical Trials Unit")
st.header("SAP AutoCode System")
st.markdown("Automated Statistical Analysis Plan translation and validation")

with st.sidebar:
    st.markdown("### About")
    st.markdown("This tool translates Statistical Analysis Plans into structured, machine readable formats.")

tab1, tab2 = st.tabs(["Upload SAP", "About"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload your Statistical Analysis Plan",
        type=['pdf', 'md', 'txt', 'docx'],
        help="Supported formats: PDF, Markdown, Text, Word"
    )
    
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        
        if st.button("Parse SAP", type="primary"):
            with st.spinner("Processing SAP..."):
                st.info("Processing functionality will be connected to the backend")
                
with tab2:
    st.markdown("""
    ### System Overview
    
    This system translates human written Statistical Analysis Plans into:
    - Structured, machine readable JSON
    - Analysis templates and skeleton code
    - Internal consistency checks
    
    **Developed by:** King's College London Clinical Trials Unit
    """)
