import streamlit as st
import os
import json
import pandas as pd
from auto_sap.classes.auto_code_api_classes import get_sap_code_from_json
st.set_page_config(
    page_title="SAPAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── URL of the public SAPAI Open deployment ───────────────────────────────────
SAPAI_OPEN_URL = "https://sapai-open.up.railway.app"  # TODO: update when live

# ── Logo ──────────────────────────────────────────────────────────────────────
logo_path = Path(__file__).parent / "sapai_logo.png"
if logo_path.exists():
    st.html(f'''
        <div style="text-align:center;padding:1rem 0 0;">
            <img src="data:image/png;base64,{__import__("base64").b64encode(logo_path.read_bytes()).decode()}" style="height:60px;">
        </div>
    ''')

# ── Load landing HTML, split at the hero paragraph ───────────────────────────
html_path = Path(__file__).parent / "landing.html"
html = html_path.read_text()
parts = html.split('<p class="sl-hero-sub">')

st.html(parts[0])

# ── Session state ─────────────────────────────────────────────────────────────
if "show_chooser" not in st.session_state:
    st.session_state.show_chooser = False

# ── Hero CTA area ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1.6, 1])

with col2:
    if not st.session_state.show_chooser:
        if st.button("Draft Your SAP", type="primary", use_container_width=True):
            st.session_state.show_chooser = True
            st.rerun()

    else:
        # ── Chooser card ──────────────────────────────────────────────────────
        st.html("""
        <div style="
            background:#fff;
            border:1px solid #e5e7eb;
            border-radius:16px;
            padding:2rem 1.8rem 1.5rem;
            box-shadow:0 4px 24px rgba(0,0,0,0.06);
            text-align:center;
            margin-bottom:0.5rem;
        ">
            <p style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:0.7rem;
                font-weight:700;
                text-transform:uppercase;
                letter-spacing:0.1em;
                color:#9ca3af;
                margin-bottom:0.5rem;
            ">Select your access type</p>
            <p style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:1.05rem;
                font-weight:700;
                color:#111;
                margin-bottom:0.25rem;
            ">How are you accessing SAPAI?</p>
            <p style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:0.82rem;
                color:#6b7280;
                margin-bottom:0;
            ">KCL users sign in with Google. Everyone else can use SAPAI Open with their own API key.</p>
        </div>
        """)

        btn_col1, btn_col2 = st.columns(2, gap="small")

        with btn_col1:
            st.html("""
            <p style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:0.72rem;
                font-weight:600;
                text-transform:uppercase;
                letter-spacing:0.08em;
                color:#2d6a4f;
                text-align:center;
                margin-bottom:0.3rem;
            ">KCL member</p>
            """)
            if st.button(
                "Sign in with Google →",
                type="primary",
                use_container_width=True,
                key="kcl_login",
                help="King's College London Clinical Trials Unit members"
            ):
                st.login()

        with btn_col2:
            st.html("""
            <p style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:0.72rem;
                font-weight:600;
                text-transform:uppercase;
                letter-spacing:0.08em;
                color:#6b7280;
                text-align:center;
                margin-bottom:0.3rem;
            ">External / Open access</p>
            """)
            st.link_button(
                "Go to SAPAI Open →",
                url=SAPAI_OPEN_URL,
                use_container_width=True,
                help="Use your own OpenAI API key — open to everyone"
            )

        st.html('<div style="height:0.6rem;"></div>')

        
        # Download button
        json_str = json.dumps(st.session_state.conversation.result, indent=2)
        st.download_button(
            label="💾 Download JSON",
            data=json_str,
            file_name="sap_autocode.json",
            mime="application/json"
        )

        st.download_button(
            label="💾 Get Code",
            data=get_sap_code_from_json(st.session_state.conversation.result),
            file_name="sap_autocode.zip",
            mime="application/zip"
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

# ── Rest of landing page ──────────────────────────────────────────────────────
st.html('<p class="sl-hero-sub">' + parts[1])
