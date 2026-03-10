import streamlit as st
import os
import json
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="SAPAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check if user has entered API key via session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'show_app' not in st.session_state:
    st.session_state.show_app = False

# LANDING PAGE
if not st.session_state.show_app:
    html_path = Path(__file__).parent / "landing.html"
    if html_path.exists():
        st.html(html_path.read_text())

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if st.button("\U0001f52c Try SAPAI", type="primary", use_container_width=True):
            if api_key:
                st.session_state.api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
                st.session_state.show_app = True
                st.rerun()
            else:
                st.error("Please enter your OpenAI API key first")
    st.stop()

# === APP (only shows after clicking Try SAPAI) ===

os.environ["OPENAI_API_KEY"] = st.session_state.api_key

try:
    from auto_sap.generate_templates.generate_simple_template import get_autocode_conversation_for_protocol
    backend_available = True
except ImportError as e:
    backend_available = False

st.title("SAPAI")
st.markdown("Automated Statistical Analysis Plan generation from trial protocols")

if 'conversation' not in st.session_state:
    st.session_state.conversation = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

tab1, tab2, tab3 = st.tabs(["Generate SAP", "Refine & Chat", "About"])

with tab1:
    st.markdown("### Upload Protocol")
    st.info("Upload your clinical trial protocol to generate a Statistical Analysis Plan")

    uploaded_file = st.file_uploader(
        "Upload Clinical Trial Protocol",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, Word, Text"
    )

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        st.warning("**Cost Estimate:** Generating a SAP typically costs $0.50 to $2.00 depending on protocol length.")

        if st.button("Generate SAP JSON", type="primary", disabled=not backend_available):
            with st.spinner("Processing protocol with LLM... This may take 2 to 5 minutes"):
                try:
                    if uploaded_file.type == "text/plain":
                        protocol_txt = uploaded_file.read().decode("utf-8")
                    elif uploaded_file.type == "application/pdf":
                        from PyPDF2 import PdfReader
                        import io
                        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                        protocol_txt = "\n".join(page.extract_text() for page in pdf_reader.pages)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        from docx import Document
                        import io
                        doc = Document(io.BytesIO(uploaded_file.read()))
                        protocol_txt = "\n".join(p.text for p in doc.paragraphs)
                    else:
                        st.error("Unsupported file type")
                        st.stop()

                    from auto_sap.generate_templates.generate_simple_template import get_autocode_conversation_for_protocol

                    st.info("Calling auto code extraction pipeline...")
                    conversation = get_autocode_conversation_for_protocol(protocol_txt)

                    st.session_state.conversation = conversation
                    st.session_state.protocol_name = uploaded_file.name

                    st.success("SAP JSON generated successfully!")
                    st.balloons()

                    with st.expander("View Generated JSON", expanded=True):
                        st.json(conversation.result)

                except Exception as e:
                    st.error(f"Error generating SAP: {str(e)}")
                    st.exception(e)

with tab2:
    st.markdown("### Refine SAP JSON")

    if st.session_state.conversation is not None:
        st.success(f"Working on: {st.session_state.get('protocol_name', 'Protocol')}")

        if "last_editor" not in st.session_state:
            st.session_state.last_editor = None

        def load_dfs_from_json():
            data = st.session_state.conversation.result
            st.session_state.timepoints_df = pd.DataFrame(data["timepoints"])
            st.session_state.variables_df = pd.DataFrame(data["variables"])
            st.session_state.analyses_df = pd.DataFrame(data["analyses"])

        if "timepoints_df" not in st.session_state or st.session_state.last_editor == "chat":
            load_dfs_from_json()
            st.session_state.last_editor = None

        with st.expander("Timepoints", expanded=False):
            st.session_state.timepoints_df = st.data_editor(
                st.session_state.timepoints_df, num_rows="dynamic", use_container_width=True, key="timepoints_editor")

        with st.expander("Variables", expanded=False):
            st.session_state.variables_df = st.data_editor(
                st.session_state.variables_df, num_rows="dynamic", use_container_width=True, key="variables_editor")

        with st.expander("Analyses", expanded=False):
            st.session_state.analyses_df = st.data_editor(
                st.session_state.analyses_df, num_rows="dynamic", use_container_width=True, key="analyses_editor")

        if not st.session_state.timepoints_df.empty:
            st.session_state.conversation.result["timepoints"] = st.session_state.timepoints_df.to_dict("records")
        if not st.session_state.variables_df.empty:
            st.session_state.conversation.result["variables"] = st.session_state.variables_df.to_dict("records")
        if not st.session_state.analyses_df.empty:
            st.session_state.conversation.result["analyses"] = st.session_state.analyses_df.to_dict("records")

        st.session_state.last_editor = "table"

        json_str = json.dumps(st.session_state.conversation.result, indent=2)
        st.download_button(label="Download JSON", data=json_str, file_name="sap_autocode.json", mime="application/json")

        st.markdown("### Refine via Chat")
        st.info("Ask questions or request edits (e.g., 'remove timepoint Visit 6')")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if user_input := st.chat_input("Type your message..."):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            with st.spinner("Processing..."):
                try:
                    st.session_state.conversation.chat(user_input)
                    st.session_state.last_editor = "chat"
                    response = "Updated! Check the JSON above to see changes."
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Generate a SAP first in the 'Generate SAP' tab")

with tab3:
    html_path = Path(__file__).parent / "landing.html"
    if html_path.exists():
        st.html(html_path.read_text())
