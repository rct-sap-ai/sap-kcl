import streamlit as st
import os
import json
import pandas as pd

st.set_page_config(
    page_title="SAP AutoCode",
    page_icon="📊",
    layout="wide"
)

st.title("🏥 IoPPN Clinical Trials Unit")
st.header("SAP AutoCode System")
st.markdown("Automated Statistical Analysis Plan generation from trial protocols")
# Sidebar for API key

with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
    )
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("✅ API key configured")
        
        # Try to import backend
        try:
            from auto_sap.generate_templates.generate_simple_template import get_autocode_conversation_for_protocol
            backend_available = True
            st.success("✅ Backend loaded")
        except ImportError as e:
            backend_available = False
            st.error(f"❌ Backend error: {e}")
    else:
        st.warning("⚠️ Please enter your OpenAI API key to continue")
        backend_available = False
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Upload a clinical trial protocol and generate a structured SAP JSON.")
    st.markdown("**Validation:** 82% accuracy on first draft")
    st.markdown("\n[Get OpenAI API Key](https://platform.openai.com/api-keys)")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Show instructions if no API key
if not api_key:
    st.info("👈 Please enter your OpenAI API key in the sidebar to get started")
    st.markdown("""
    ### Getting Started
    
    1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
    2. Enter it in the sidebar
    3. Upload your clinical trial protocol
    4. Generate your SAP!
    
    **Your API key is only used for this session and is never stored.**
    """)
    st.stop()

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
        
        # Show cost estimate
        st.warning("⚠️ **Cost Estimate:** Generating a SAP typically costs $0.50 to $2.00 depending on protocol length. This will be charged to your OpenAI account.")
        
        if st.button("Generate SAP JSON", type="primary", disabled=not backend_available):
            with st.spinner("Processing protocol with LLM... This may take 2-5 minutes"):
                try:
                    # Read protocol text
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
                    
                    # Import here after API key is set
                    from auto_sap.generate_templates.generate_simple_template import get_autocode_conversation_for_protocol
                    
                    # Generate SAP using your actual backend
                    st.info("Calling auto code extraction pipeline...")
                    conversation = get_autocode_conversation_for_protocol(protocol_txt)
                    
                    # Store in session state
                    st.session_state.conversation = conversation
                    st.session_state.protocol_name = uploaded_file.name
                    
                    st.success("✅ SAP JSON generated successfully!")
                    st.balloons()
                    
                    # Show preview
                    with st.expander("📊 View Generated JSON", expanded=True):
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

        with st.expander("📊 Timepoints", expanded=False):
            st.session_state.timepoints_df = st.data_editor(
                st.session_state.timepoints_df,
                num_rows="dynamic",
                use_container_width=True,
                key="timepoints_editor"
            )

        with st.expander("📊 Variables", expanded=False):
            st.session_state.variables_df = st.data_editor(
                st.session_state.variables_df,
                num_rows="dynamic",
                use_container_width=True,
                key="variables_editor"
            )

        with st.expander("📊 Analyses", expanded=False):
            st.session_state.analyses_df = st.data_editor(
                st.session_state.analyses_df,
                num_rows="dynamic",
                use_container_width=True,
                key="analyses_editor"
            )

        if not st.session_state.timepoints_df.empty:
            st.session_state.conversation.result["timepoints"] = (
                st.session_state.timepoints_df.to_dict("records")
            )

        if not st.session_state.variables_df.empty:
            st.session_state.conversation.result["variables"] = (
                st.session_state.variables_df.to_dict("records")
            )

        if not st.session_state.analyses_df.empty:
            st.session_state.conversation.result["analyses"] = (
                st.session_state.analyses_df.to_dict("records")
        )
        
        st.session_state.last_editor = "table"

        
        # Download button
        json_str = json.dumps(st.session_state.conversation.result, indent=2)
        st.download_button(
            label="💾 Download JSON",
            data=json_str,
            file_name="sap_autocode.json",
            mime="application/json"
        )
        
        # Chat interface
        st.markdown("### 💬 Refine via Chat")
        st.info("Ask questions or request edits (e.g., 'remove timepoint Visit 6' or 'what would you suggest for outcomes?')")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # Chat input
        if user_input := st.chat_input("Type your message..."):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.spinner("Processing..."):
                try:
                    # Use conversation.chat() to refine
                    st.session_state.conversation.chat(user_input)
                    st.session_state.last_editor = "chat"

                    
                    # Show updated JSON
                    response = f"✅ Updated! Check the JSON above to see changes."
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    with st.chat_message("assistant"):
                        st.write(response)
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Generate a SAP first in the 'Generate SAP' tab")

with tab3:
    st.markdown("""
    ### System Overview
    
    This system automatically generates Statistical Analysis Plans (SAPs) from clinical trial protocols using Large Language Models.
    
    **Process:**
    1. Enter your OpenAI API key
    2. Upload your trial protocol (PDF, Word, or Text)
    3. System extracts key information using specialized prompts
    4. Generates structured JSON with:
       - Timepoints
       - Variables & Outcomes  
       - Statistical Methods
       - Analysis Populations
       - And more...
    5. Refine interactively via chat
    
    **Cost:**
    - Typical cost: $0.50 - $2.00 per protocol
    - Charged to your OpenAI account
    - You maintain full control
    
    **Validation Results:**
    - 82% items generated correctly on first draft
    - 12% minor errors (easily correctable)
    - 6% major errors (require manual review)
    
    **Privacy:**
    - Your API key is only used during your session
    - Never stored or logged
    - Your protocols are processed securely
    
    **Developed by:** King's College London Clinical Trials Unit
    """)
