import streamlit as st
from openai import OpenAI
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SOX Compliance AI Assistant",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .main { background-color: #0f1117; }
    .block-container { padding-top: 2rem; max-width: 820px; }

    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #1a2332 0%, #0d1b2a 100%);
        border: 1px solid #2a3f5f;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-size: 22px;
        font-weight: 600;
        color: #e8f0fe;
        margin: 0 0 4px 0;
        letter-spacing: -0.3px;
    }
    .header-sub {
        font-size: 13px;
        color: #8899aa;
        margin: 0;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Stat pills */
    .stat-row { display: flex; gap: 10px; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .stat-pill {
        background: #1a2332;
        border: 1px solid #2a3f5f;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 12px;
        color: #7ba3d4;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Chat messages */
    .stChatMessage {
        background: #141921 !important;
        border: 1px solid #1e2d3d !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }
    .stChatMessage p { color: #c8d8e8 !important; line-height: 1.7 !important; }

    /* Input box */
    .stChatInputContainer {
        border-top: 1px solid #1e2d3d !important;
        padding-top: 1rem !important;
    }
    .stChatInput textarea {
        background: #141921 !important;
        border: 1px solid #2a3f5f !important;
        color: #e8f0fe !important;
        border-radius: 10px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0d1117 !important;
        border-right: 1px solid #1e2d3d !important;
    }
    [data-testid="stSidebar"] * { color: #a0b4c8 !important; }

    /* Example buttons */
    .stButton button {
        background: #141921 !important;
        border: 1px solid #2a3f5f !important;
        color: #7ba3d4 !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        text-align: left !important;
        width: 100% !important;
        padding: 8px 12px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        transition: all 0.2s !important;
        white-space: normal !important;
        height: auto !important;
    }
    .stButton button:hover {
        background: #1a2e42 !important;
        border-color: #4a7db5 !important;
        color: #a8c8f0 !important;
    }

    /* Section labels */
    .section-label {
        font-size: 11px;
        font-weight: 600;
        color: #4a6a8a;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Warning / info boxes */
    .stAlert { border-radius: 8px !important; }
    .clear-btn button {
        background: #1f1520 !important;
        border-color: #3d2040 !important;
        color: #c080d0 !important;
        font-size: 11px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── System prompt (your audit domain expertise baked in) ──────────────────────
SYSTEM_PROMPT = """You are a senior SOX Compliance and IT Audit expert with 10+ years of experience 
across BFSI, Manufacturing, and IT/SaaS sectors. You have deep expertise in:

AUDIT FRAMEWORKS & STANDARDS:
- SOX (Sarbanes-Oxley Act) Section 302 and 404 compliance
- ITGC (IT General Controls): Access Management, Change Management, Computer Operations, Program Development
- ITAC (IT Application Controls): Input, Processing, Output controls
- IPE (Information Produced by the Entity) testing
- COBIT 2019 framework
- CISA standards and IIA guidelines

CONTROL DOMAINS:
- Access Management: User provisioning/deprovisioning, privileged access, periodic access reviews, SoD (Segregation of Duties)
- Change Management: SDLC, patch management, emergency change procedures, change advisory boards
- Computer Operations: Job scheduling, incident management, backup/recovery, data center controls
- Business Process Controls: 3-way match, approval workflows, reconciliation controls

TECHNOLOGY PLATFORMS:
- SAP S/4HANA and SAP ECC control configurations
- Microsoft Dynamics 365
- Azure and AWS cloud control considerations
- SQL-based data extraction for audit testing

AUDIT METHODOLOGY:
- Risk-based audit planning and scoping
- Walkthrough procedures and evidence validation
- Control deficiency classification (deficiency, significant deficiency, material weakness)
- Remediation tracking and management action plans
- Audit documentation best practices

YOUR COMMUNICATION STYLE:
- Be precise and structured — use bullet points and numbered lists for complex topics
- Always connect abstract concepts to practical audit evidence and testing procedures
- When explaining controls, mention what evidence an auditor would collect
- Flag common pitfalls and red flags that indicate control weaknesses
- Use audit-specific terminology accurately (e.g., distinguish "exception" from "deficiency")
- When relevant, mention which SAP transaction codes or system configurations are relevant
- Keep answers focused and actionable — avoid vague generalities

If asked something outside audit/compliance scope, politely redirect to your area of expertise."""


# ── Initialise session state ───────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False


# ── Helper: call OpenAI API with full conversation history ─────────────────────
def get_ai_response(messages: list, api_key: str) -> str:
    """Send full conversation history to GPT-4o and return the response."""
    try:
        client = OpenAI(api_key=api_key)

        # Build messages list with system prompt prepended
        openai_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1500,
            messages=openai_messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        err = str(e)
        if "401" in err or "Incorrect API key" in err:
            return "❌ Invalid API key. Please check your OpenAI API key in the sidebar."
        elif "429" in err:
            return "⚠️ Rate limit hit. Please wait a moment and try again."
        else:
            return f"⚠️ Something went wrong: {err}"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ SOX AI Assistant")
    st.markdown("---")

    # API Key input
    st.markdown('<div class="section-label">API Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Get your key at platform.openai.com/api-keys",
        key="api_key_input"
    )

    if api_key:
        st.session_state.api_key_set = True
        st.success("✅ API key loaded", icon="🔑")
    else:
        st.warning("Enter your API key to begin", icon="⚠️")

    st.markdown("---")

    # Example questions
    st.markdown('<div class="section-label">Example Questions</div>', unsafe_allow_html=True)

    examples = [
        "What evidence do I collect for User Access Review testing?",
        "How do I classify a control deficiency vs material weakness?",
        "Walk me through Change Management ITGC testing steps",
        "What are key SoD conflicts to look for in SAP?",
        "How do I test IPE (Information Produced by Entity)?",
        "What are red flags in Privileged Access Management?",
        "Explain Computer Operations controls for SOX",
        "How do I document a walkthrough procedure?",
    ]

    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}"):
            st.session_state.pending_question = ex

    st.markdown("---")

    # Conversation stats
    msg_count = len(st.session_state.messages)
    st.markdown(f"""
    <div class="section-label">Session Info</div>
    <div style="font-family:'IBM Plex Mono',monospace; font-size:12px; color:#4a6a8a; line-height:2">
    Messages : {msg_count}<br>
    Model    : gpt-4o<br>
    Memory   : Full context
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Clear conversation
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear conversation", key="clear"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <p class="header-title">🛡️ SOX Compliance AI Assistant</p>
    <p class="header-sub">ITGC · ITAC · IPE · Access Management · Change Management · SoD</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stat-row">
    <div class="stat-pill">SOX § 302 & § 404</div>
    <div class="stat-pill">COBIT 2019</div>
    <div class="stat-pill">SAP S/4HANA & ECC</div>
    <div class="stat-pill">CISA Standards</div>
    <div class="stat-pill">BFSI · Manufacturing · IT/SaaS</div>
</div>
""", unsafe_allow_html=True)

# Welcome message when no conversation yet
if not st.session_state.messages:
    st.markdown("""
    <div style="background:#141921; border:1px solid #1e2d3d; border-radius:10px; padding:1.2rem 1.5rem; margin-bottom:1rem;">
        <p style="color:#7ba3d4; font-size:14px; margin:0 0 8px 0; font-weight:500;">👋 Welcome</p>
        <p style="color:#8899aa; font-size:13px; margin:0; line-height:1.7;">
        Ask me anything about SOX compliance, ITGC/ITAC testing, access management, change management, 
        control deficiencies, or audit evidence collection. Use the example questions in the sidebar to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle sidebar example button clicks
if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

    if not st.session_state.api_key_set:
        st.error("Please enter your OpenAI API key in the sidebar first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analysing..."):
                reply = get_ai_response(st.session_state.messages, api_key)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# Handle typed input
if user_input := st.chat_input("Ask a SOX / ITGC / audit question..."):
    if not st.session_state.api_key_set:
        st.error("Please enter your OpenAI API key in the sidebar first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analysing..."):
                reply = get_ai_response(st.session_state.messages, api_key)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()