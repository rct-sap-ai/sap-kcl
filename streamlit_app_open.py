"""
SAPAI Open — public-facing Statistical Analysis Plan generator.
Users bring their own OpenAI API key; no Google auth required.
Uses the validation / simple template (not the KCL-tailored template).
"""

import json
import tempfile
from pathlib import Path

import streamlit as st

from auto_sap.classes.protocol_classes import Protocol
from auto_sap.generate_templates.generate_simple_template import (
    get_autocode_conversation_for_protocol,
    get_sap_content_for_protocol,
    simple_template,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAPAI Open",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Shared styles ─────────────────────────────────────────────────────────────
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&family=Instrument+Serif:ital@0;1&display=swap');
[data-testid="stAppViewContainer"] { font-family: 'Plus Jakarta Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.open-hero { text-align:center; padding:3.5rem 2rem 2rem; background:linear-gradient(180deg,#f0faf4 0%,#fafafa 100%); position:relative; }
.open-hero::before { content:''; position:absolute; top:-200px; left:50%; transform:translateX(-50%); width:700px; height:700px; background:radial-gradient(circle,rgba(45,106,79,0.07) 0%,transparent 65%); pointer-events:none; }
.open-chip { display:inline-flex; align-items:center; gap:0.5rem; padding:0.28rem 0.9rem; background:#fff; border:1px solid #e5e7eb; border-radius:100px; font-size:0.68rem; font-weight:700; color:#2d6a4f; letter-spacing:0.07em; text-transform:uppercase; margin-bottom:1.5rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.open-chip-dot { width:6px; height:6px; border-radius:50%; background:#2d6a4f; display:inline-block; }
.open-hero h1 { font-size:clamp(2.2rem,4.5vw,3.2rem); font-weight:800; line-height:1.1; letter-spacing:-0.03em; color:#111; margin-bottom:0.9rem; }
.open-hero h1 span { color:#2d6a4f; }
.open-hero-sub { font-size:1rem; color:#6b7280; max-width:480px; margin:0 auto 0.5rem; line-height:1.8; }
.open-step-header { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#2d6a4f; margin-bottom:0.25rem; }
.open-card { background:#fff; border:1px solid #e5e7eb; border-radius:16px; padding:2rem; box-shadow:0 2px 12px rgba(0,0,0,0.04); }
.open-disclaimer { font-size:0.75rem; color:#9ca3af; line-height:1.6; text-align:center; margin-top:0.4rem; }
.section-divider { border:none; border-top:1px solid #f0f0f0; margin:2.5rem 0; }
.result-label { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#9ca3af; margin-bottom:0.5rem; }
</style>
""")

# ── Session state defaults ────────────────────────────────────────────────────
defaults = {
    "api_key": "",
    "api_key_confirmed": False,
    "model": "gpt-4o",
    "convo": None,
    "result": None,
    "sap_docx_bytes": None,
    "sap_title": "",
    "step": "setup",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def render_setup():
    logo_path = Path(__file__).parent / "sapai_logo.png"
    if logo_path.exists():
        st.html(f'''
            <div style="text-align:center;padding:1.5rem 0 0;">
                <img src="data:image/png;base64,{__import__("base64").b64encode(logo_path.read_bytes()).decode()}"
                     style="height:52px;">
            </div>
        ''')

    st.html("""
    <div class="open-hero">
        <div class="open-chip"><span class="open-chip-dot"></span>Open Access</div>
        <h1>Statistical Analysis Plans,<br><span>in Minutes</span></h1>
        <p class="open-hero-sub">
            Bring your own OpenAI API key and generate a draft SAP directly
            from your clinical trial protocol. No account required.
        </p>
    </div>
    """)

    st.html('<div style="height:1.5rem;"></div>')

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.html('<div class="open-step-header">Step 1 of 2 — Connect your OpenAI key</div>')

        key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            value=st.session_state.api_key,
            help="Your key is used only for this session and never stored.",
            label_visibility="collapsed",
        )

        model_choice = st.selectbox(
            "Model",
            options=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-5-nano"],
            index=0,
            help="gpt-4o gives the best results. gpt-4o-mini is faster and cheaper.",
        )

        st.html('<div style="height:0.4rem;"></div>')

        if st.button("Continue →", type="primary", use_container_width=True):
            if not key_input or not key_input.startswith("sk-"):
                st.error("Please enter a valid OpenAI API key (starts with sk-).")
            else:
                st.session_state.api_key = key_input
                st.session_state.model = model_choice
                st.session_state.api_key_confirmed = True
                st.session_state.step = "generate"
                st.rerun()

        st.html("""
        <p class="open-disclaimer">
            Your API key is held only in your browser session and is never
            logged or transmitted to our servers. Costs depend on your
            OpenAI usage — typically &lt;$0.50 per SAP with gpt-4o.
        </p>
        """)

    st.html('<div style="height:3rem;"></div>')
    st.html("""
    <div style="max-width:700px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);
                gap:1px;background:#e5e7eb;border-radius:16px;overflow:hidden;">
        <div style="background:#fff;padding:1.5rem 1rem;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#2d6a4f;">80%+</div>
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;color:#9ca3af;margin-top:0.25rem;">Accuracy</div>
        </div>
        <div style="background:#fff;padding:1.5rem 1rem;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#2d6a4f;">9</div>
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;color:#9ca3af;margin-top:0.25rem;">Trials Validated</div>
        </div>
        <div style="background:#fff;padding:1.5rem 1rem;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#2d6a4f;">27</div>
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;color:#9ca3af;margin-top:0.25rem;">SAPs Generated</div>
        </div>
        <div style="background:#fff;padding:1.5rem 1rem;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#2d6a4f;">3</div>
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;color:#9ca3af;margin-top:0.25rem;">LLMs Tested</div>
        </div>
    </div>
    <p style="text-align:center;font-size:0.72rem;color:#9ca3af;margin-top:1rem;font-family:'Plus Jakarta Sans',sans-serif;">
        Validated by independent trial statisticians at King's College London Clinical Trials Unit
        &middot; <a href="https://github.com/rct-sap-ai/sapai-jama-sap-validation" style="color:#2d6a4f;">Forbes et al.</a>
    </p>
    """)

    st.html("""
    <div style="text-align:center;padding:2rem;border-top:1px solid #f0f0f0;margin-top:3rem;">
        <p style="font-size:0.72rem;color:#9ca3af;font-family:'Plus Jakarta Sans',sans-serif;">
            &copy; 2025 SAPAI &middot; King's College London Clinical Trials Unit, IoPPN
        </p>
    </div>
    """)


def render_generate():
    logo_path = Path(__file__).parent / "sapai_logo.png"
    header_logo = ""
    if logo_path.exists():
        b64 = __import__("base64").b64encode(logo_path.read_bytes()).decode()
        header_logo = f'<img src="data:image/png;base64,{b64}" style="height:36px;">'

    st.html(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:1rem 2rem;border-bottom:1px solid #f0f0f0;background:#fff;">
        {header_logo}
        <div style="display:flex;align-items:center;gap:0.6rem;">
            <div style="width:8px;height:8px;border-radius:50%;background:#2d6a4f;"></div>
            <span style="font-size:0.72rem;font-weight:600;color:#6b7280;font-family:'Plus Jakarta Sans',sans-serif;">
                {st.session_state.model} &middot; key ending
                ···{st.session_state.api_key[-4:] if len(st.session_state.api_key) >= 4 else '****'}
            </span>
        </div>
    </div>
    """)

    st.html('<div style="height:1.5rem;"></div>')

    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        st.html('<div class="open-step-header">Step 2 of 2 — Upload your protocol</div>')

        uploaded = st.file_uploader(
            "Upload protocol (.pdf or .txt)",
            type=["pdf", "txt"],
            label_visibility="collapsed",
        )

        if uploaded:
            protocol = Protocol(uploaded)
            protocol_text = protocol.protocol_txt

            st.html(f"""
            <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;
                        padding:1rem 1.2rem;margin:0.8rem 0;font-size:0.78rem;
                        color:#6b7280;font-family:'Plus Jakarta Sans',sans-serif;line-height:1.6;">
                <span style="font-weight:600;color:#111;">📄 {uploaded.name}</span>
                &nbsp;&middot;&nbsp;{len(protocol_text):,} characters extracted
            </div>
            """)

            with st.expander("Preview extracted text", expanded=False):
                st.text(protocol_text[:1500] + (" …" if len(protocol_text) > 1500 else ""))

            st.html('<div style="height:0.6rem;"></div>')

            if st.button("🚀 Generate SAP", type="primary", use_container_width=True):
                with st.spinner("Running extraction across all SAP sections — this takes 1–3 minutes…"):
                    try:
                        convo = get_autocode_conversation_for_protocol(
                            protocol_txt=protocol_text,
                            model=st.session_state.model,
                            validate=False,
                            api_key=st.session_state.api_key,
                        )
                        st.session_state.convo = convo
                        st.session_state.result = convo.result
                        docx_bytes = simple_template.populate_to_bytes()
                        st.session_state.sap_docx_bytes = docx_bytes
                        st.session_state.sap_title = (
                            simple_template.sap_content.get("trial_acronym", "")
                            or simple_template.sap_content.get("title", "SAP")
                        )
                        st.session_state.step = "results"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
                        if "Incorrect API key" in str(e) or "401" in str(e):
                            st.warning("Your API key appears to be invalid. Go back and check it.")
        else:
            st.html("""
            <div style="text-align:center;padding:2.5rem;color:#9ca3af;
                        font-size:0.85rem;font-family:'Plus Jakarta Sans',sans-serif;">
                Upload a PDF or TXT file to get started
            </div>
            """)

        st.html('<div style="height:1rem;"></div>')
        if st.button("← Change API key / model", key="back_to_setup"):
            st.session_state.step = "setup"
            st.session_state.api_key_confirmed = False
            st.rerun()


def render_results():
    logo_path = Path(__file__).parent / "sapai_logo.png"
    header_logo = ""
    if logo_path.exists():
        b64 = __import__("base64").b64encode(logo_path.read_bytes()).decode()
        header_logo = f'<img src="data:image/png;base64,{b64}" style="height:36px;">'

    st.html(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:1rem 2rem;border-bottom:1px solid #f0f0f0;background:#fff;">
        {header_logo}
        <div style="background:#d1fae5;border-radius:100px;padding:0.3rem 1rem;
                    font-size:0.7rem;font-weight:700;color:#2d6a4f;
                    font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:0.06em;">
            ✓ Generation complete
        </div>
    </div>
    """)

    st.html('<div style="height:1.5rem;"></div>')

    st.html("""
    <div style="max-width:900px;margin:0 auto;padding:0 1rem;">
        <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:#2d6a4f;margin-bottom:0.4rem;
                    font-family:'Plus Jakarta Sans',sans-serif;">Downloads</div>
        <h2 style="font-size:1.6rem;font-weight:800;letter-spacing:-0.02em;color:#111;margin-bottom:0.3rem;
                   font-family:'Plus Jakarta Sans',sans-serif;">Your SAP is ready</h2>
        <p style="font-size:0.88rem;color:#6b7280;margin-bottom:1.5rem;
                  font-family:'Plus Jakarta Sans',sans-serif;">
            Review carefully with a qualified statistician before use in a live trial.
        </p>
    </div>
    """)

    dl_col1, dl_col2, _ = st.columns([1, 1, 1.5])
    sap_name = (st.session_state.sap_title or "SAP").replace(" ", "_")

    with dl_col1:
        if st.session_state.sap_docx_bytes:
            st.download_button(
                label="⬇ Download SAP (.docx)",
                data=st.session_state.sap_docx_bytes,
                file_name=f"{sap_name}_SAPAI_draft.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary",
            )

    with dl_col2:
        if st.session_state.result:
            st.download_button(
                label="⬇ Download Autocode (.json)",
                data=json.dumps(st.session_state.result, indent=2),
                file_name=f"{sap_name}_autocode.json",
                mime="application/json",
                use_container_width=True,
            )

    st.html('<hr class="section-divider">')

    if st.session_state.result:
        tc, vc, ac = st.columns(3, gap="medium")
        with tc:
            st.html('<div class="result-label">Timepoints</div>')
            st.json(st.session_state.result.get("timepoints", []), expanded=True)
        with vc:
            st.html('<div class="result-label">Variables</div>')
            st.json(st.session_state.result.get("variables", []), expanded=True)
        with ac:
            st.html('<div class="result-label">Analyses</div>')
            st.json(st.session_state.result.get("analyses", []), expanded=True)

    st.html('<hr class="section-divider">')

    st.html("""
    <div style="max-width:900px;margin:0 auto;padding:0 1rem 0.5rem;">
        <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:#6b7280;margin-bottom:0.25rem;
                    font-family:'Plus Jakarta Sans',sans-serif;">Human-in-the-loop corrections</div>
        <p style="font-size:0.82rem;color:#9ca3af;font-family:'Plus Jakarta Sans',sans-serif;">
            Describe any changes in plain English.
        </p>
    </div>
    """)

    if st.session_state.convo:
        chat_col, _ = st.columns([2, 1])
        with chat_col:
            user_msg = st.text_area(
                "Your instruction",
                placeholder='e.g. "Remove the 6-month timepoint"',
                label_visibility="collapsed",
                height=90,
            )
            if st.button("Apply correction", type="primary"):
                if user_msg.strip():
                    with st.spinner("Updating…"):
                        try:
                            new_json = st.session_state.convo.chat(user_msg)
                            st.session_state.result = new_json
                            st.success("JSON updated — scroll up to review.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")

    st.html('<hr class="section-divider">')

    fc1, fc2, _ = st.columns([1, 1, 3])
    with fc1:
        if st.button("← Process another protocol", use_container_width=True):
            st.session_state.convo = None
            st.session_state.result = None
            st.session_state.sap_docx_bytes = None
            st.session_state.sap_title = ""
            st.session_state.step = "generate"
            st.rerun()
    with fc2:
        if st.button("Start over", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

    st.html("""
    <div style="text-align:center;padding:2rem 1rem;margin-top:1rem;border-top:1px solid #f0f0f0;">
        <p style="font-size:0.7rem;color:#9ca3af;font-family:'Plus Jakarta Sans',sans-serif;">
            &copy; 2025 SAPAI Open &middot; King's College London Clinical Trials Unit, IoPPN
            &middot; Always review AI-generated SAPs with a qualified statistician.
        </p>
    </div>
    """)


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.step == "setup":
    render_setup()
elif st.session_state.step == "generate":
    render_generate()
elif st.session_state.step == "results":
    render_results()
