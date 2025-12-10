"""
Simple Streamlit UI for SAP autocode extraction and conversational editing.

Usage (from repo root):

    pip install -r requirements.txt
    pip install streamlit

    streamlit run ui_autocode.py

Requirements:
- OPENAI_API_KEY set in your environment (or .env picked up by dotenv).
- The repo structure must be the standard sap-kcl layout:
  - Classes/
  - GenerateTemplates/
  - Protocols/
"""

import os
import tempfile
import json

import streamlit as st

# Make sure Python can see the local packages when running from elsewhere
# (if you run `streamlit run ui_autocode.py` from repo root, this is optional,
#  but harmless to keep)
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from Classes.protocol_classes import Protocol
from GenerateTemplates.generate_simple_template import (
    get_autocode_conversation_for_protocol,
)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def load_protocol_text_from_upload(uploaded_file) -> str | None:
    """
    Save the uploaded file to a temp location and pass through Protocol,
    so we reuse the existing PDF/TXT handling.
    """
    if uploaded_file is None:
        return None

    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    if suffix not in [".txt", ".pdf"]:
        st.error("Unsupported file type. Please upload a .txt or .pdf protocol.")
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    protocol = Protocol(tmp_path)
    return protocol.protocol_txt


def load_example_protocol_text() -> str:
    """
    Convenience helper to load the BOPPP example protocol
    that already lives in the repo.
    """
    example_path_txt = os.path.join(CURRENT_DIR, "Protocols", "boppp.txt")
    example_path_pdf = os.path.join(CURRENT_DIR, "Protocols", "boppp.pdf")

    if os.path.exists(example_path_txt):
        protocol = Protocol(example_path_txt)
    elif os.path.exists(example_path_pdf):
        protocol = Protocol(example_path_pdf)
    else:
        raise FileNotFoundError(
            "Could not find example BOPPP protocol in Protocols/boppp.txt or Protocols/boppp.pdf"
        )

    return protocol.protocol_txt


def ensure_conversation_state():
    """
    Initialise session_state keys we rely on.
    """
    if "convo" not in st.session_state:
        st.session_state["convo"] = None
    if "protocol_text" not in st.session_state:
        st.session_state["protocol_text"] = None
    if "last_error" not in st.session_state:
        st.session_state["last_error"] = None


# ----------------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------------


def main():
    st.set_page_config(page_title="SAP Autocode UI", layout="wide")
    st.title("🧪 SAP Autocode Extraction & Chatbot")

    ensure_conversation_state()

    st.sidebar.header("Protocol source")

    protocol_source = st.sidebar.radio(
        "Select protocol input:",
        ("Upload file", "Use example BOPPP protocol"),
    )

    uploaded_file = None
    if protocol_source == "Upload file":
        uploaded_file = st.sidebar.file_uploader(
            "Upload protocol (.txt or .pdf)",
            type=["txt", "pdf"],
        )

    model = st.sidebar.selectbox(
        "Model",
        options=["gpt-5-nano", "gpt-5"],
        index=0,
        help="Model passed through to the underlying Template & chat classes.",
    )

    validate = st.sidebar.checkbox(
        "Enable validation step", value=False, help="Runs the ValidationBot if enabled."
    )

    # ------------------------------------------------------------------
    # Step 1: Load / choose protocol
    # ------------------------------------------------------------------
    st.subheader("1️⃣ Load protocol text")

    if protocol_source == "Use example BOPPP protocol":
        if st.button("Load BOPPP example", type="primary"):
            try:
                protocol_txt = load_example_protocol_text()
                st.session_state["protocol_text"] = protocol_txt
                st.session_state["convo"] = None
                st.session_state["last_error"] = None
                st.success("Loaded example BOPPP protocol.")
            except Exception as e:
                st.session_state["last_error"] = str(e)
                st.error(f"Error loading example protocol: {e}")
    else:
        if uploaded_file is not None:
            if st.button("Use uploaded protocol", type="primary"):
                try:
                    protocol_txt = load_protocol_text_from_upload(uploaded_file)
                    if protocol_txt:
                        st.session_state["protocol_text"] = protocol_txt
                        st.session_state["convo"] = None
                        st.session_state["last_error"] = None
                        st.success(
                            f"Loaded uploaded protocol ({len(protocol_txt):,} characters)."
                        )
                except Exception as e:
                    st.session_state["last_error"] = str(e)
                    st.error(f"Error loading uploaded protocol: {e}")

    if st.session_state["protocol_text"]:
        with st.expander("Show protocol text (first 4,000 characters)", expanded=False):
            preview = st.session_state["protocol_text"][:4000]
            st.text(preview)

    # ------------------------------------------------------------------
    # Step 2: Generate SAP + autocode JSON
    # ------------------------------------------------------------------
    st.subheader("2️⃣ Generate SAP and autocode JSON")

    if st.session_state["protocol_text"] is None:
        st.info("Load a protocol first (via sidebar) to enable SAP/autocode generation.")
    else:
        if st.button("Run SAP generation + autocode extraction", type="primary"):
            try:
                st.session_state["last_error"] = None
                with st.spinner("Running SAP template + autocode pipeline..."):
                    convo = get_autocode_conversation_for_protocol(
                        protocol_txt=st.session_state["protocol_text"],
                        model=model,
                        validate=validate,
                    )
                st.session_state["convo"] = convo
                st.success("Autocode extraction complete.")
            except Exception as e:
                st.session_state["convo"] = None
                st.session_state["last_error"] = str(e)
                st.error(f"Error running autocode pipeline: {e}")

    # ------------------------------------------------------------------
    # Step 3: View current JSON
    # ------------------------------------------------------------------
    if st.session_state["convo"] is not None:
        convo = st.session_state["convo"]
        result = getattr(convo, "result", {})

        st.subheader("3️⃣ Current autocode JSON")

        timepoints = result.get("timepoints", [])
        variables = result.get("variables", [])
        analyses = result.get("analyses", [])

        tab_tp, tab_vars, tab_an = st.tabs(["Timepoints", "Variables", "Analyses"])

        with tab_tp:
            st.caption(f"{len(timepoints)} timepoints extracted")
            st.json(timepoints)

        with tab_vars:
            st.caption(f"{len(variables)} variables extracted")
            st.json(variables)

        with tab_an:
            st.caption(f"{len(analyses)} analyses extracted")
            st.json(analyses)

        # ------------------------------------------------------------------
        # Step 4: Conversational editing
        # ------------------------------------------------------------------
        st.subheader("4️⃣ Chat with the autocode bot")

        st.markdown(
            "Type natural language instructions to adjust the JSON, e.g.: "
            "`Remove the 12-month timepoint and keep only baseline and 3-year`."
        )

        user_message = st.text_area(
            "Your message to the bot",
            key="chat_input",
            placeholder="e.g. No, you've added an extra timepoint at 6 months; please remove it and keep only baseline and 3-year.",
            height=100,
        )

        if st.button("Send message", key="send_message"):
            if not user_message.strip():
                st.warning("Please enter a message before sending.")
            else:
                try:
                    with st.spinner("Asking the bot to update the JSON..."):
                        # chat() should update convo.result internally and may also return the new result
                        updated_result = convo.chat(user_message.strip())

                    # Keep the conversation object in session_state
                    st.session_state["convo"] = convo

                    st.success("Updated JSON based on your instructions.")
                except Exception as e:
                    st.error(f"Error during conversational update: {e}")

        # Optional: show raw JSON if desired
        with st.expander("Show full result JSON", expanded=False):
            st.json(result)

        # ------------------------------------------------------------------
        # Step 5: Download/export JSON
        # ------------------------------------------------------------------
        st.subheader("5️⃣ Export autocode JSON")

        json_bytes = json.dumps(result, indent=2).encode("utf-8")
        st.download_button(
            label="Download autocode JSON",
            data=json_bytes,
            file_name="autocode_result.json",
            mime="application/json",
        )

    # ------------------------------------------------------------------
    # Error display
    # ------------------------------------------------------------------
    if st.session_state["last_error"]:
        with st.expander("Last error (debug)", expanded=False):
            st.code(st.session_state["last_error"])


if __name__ == "__main__":
    main()
