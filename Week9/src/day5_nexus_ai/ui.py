"""
NEXUS AI — Streamlit UI
Run from day5_nexus_ai/: streamlit run ui.py
"""

import asyncio
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import OUTPUT_DIR, LOG_DIR, LOG_FILE_PATH
from tools import create_log_entry

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEXUS AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@400;600;800&display=swap" rel="stylesheet">

<style>
/* ── Base ── */
html, body, [data-testid="stApp"] {
    background-color: #060a0f !important;
    color: #e2f0ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 16px !important;
}

/* ── Disable sidebar resize handle ── */
[data-testid="stSidebarResizeHandle"],
[data-testid="stSidebar"] ~ div[style*="cursor"],
.stSidebarResizeHandle {
    display: none !important;
    pointer-events: none !important;
    width: 0 !important;
    position: absolute !important;
    z-index: -1 !important;
}
/* ensure sidebar content is always on top and clickable */
[data-testid="stSidebarContent"],
[data-testid="stSidebarContent"] * {
    pointer-events: auto !important;
    position: relative !important;
    z-index: 999 !important;
}
[data-testid="stSidebar"] {
    resize: none !important;
    pointer-events: auto !important;
    z-index: 100 !important;
}

/* ── Sidebar always visible ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"][aria-expanded="false"],
[data-testid="stSidebar"][aria-expanded="true"] {
    background: #080d14 !important;
    border-right: 1px solid #0ff4 !important;
    min-width: 290px !important;
    width: 290px !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    left: 0 !important;
    position: relative !important;
}
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    width: 100% !important;
}
[data-testid="stSidebarContent"] {
    display: block !important;
    visibility: visible !important;
    padding: 20px 16px !important;
    opacity: 1 !important;
}
/* hide the collapse/expand arrow button entirely */
[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
section[data-testid="stSidebar"] > div:first-child > div > button {
    display: none !important;
    visibility: hidden !important;
}
[data-testid="stSidebar"] * {
    color: #b0d4ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00ffe7 !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #b0d4ff !important;
    font-size: 14px !important;
}

/* ── Hide sidebar collapse button ── */
button[kind="header"] { display: none !important; }

/* ── Main headings ── */
h1 {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 2.8rem !important;
    color: #00ffe7 !important;
    letter-spacing: 8px !important;
    text-transform: uppercase !important;
    text-shadow: 0 0 30px #00ffe740, 0 0 60px #00ffe720 !important;
    margin-bottom: 0 !important;
    font-weight: 700 !important;
}
h2 {
    font-family: 'Exo 2', sans-serif !important;
    color: #7df9ff !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}
h3 {
    font-family: 'Exo 2', sans-serif !important;
    color: #7df9ff !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
}

/* ── Subtitle ── */
.nexus-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 16px;
    color: #00ffe7a0;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: -6px;
    margin-bottom: 20px;
    font-weight: 700;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #0ff3 !important;
    margin: 14px 0 !important;
}

/* ── User chat bubble ── */
.user-bubble {
    background: linear-gradient(135deg, #0d1f35 0%, #102240 100%);
    border: 1px solid #1e4a7a;
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px;
    margin: 10px 0 10px 80px;
    color: #c8e6ff;
    font-size: 15px;
    line-height: 1.7;
    font-family: 'Exo 2', sans-serif;
}
.user-bubble .label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #4a9eff;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
    font-weight: 600;
}

/* ── NEXUS chat bubble ── */
.nexus-bubble {
    background: linear-gradient(135deg, #001a14 0%, #002820 100%);
    border: 1px solid #00ffe730;
    border-left: 3px solid #00ffe7;
    border-radius: 16px 16px 16px 4px;
    padding: 16px 20px;
    margin: 10px 80px 10px 0;
    color: #d4fff9;
    font-size: 15px;
    line-height: 1.8;
    font-family: 'Exo 2', sans-serif;
    box-shadow: 0 0 20px #00ffe710;
}
.nexus-bubble .label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #00ffe7;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 600;
}
.nexus-bubble.warn {
    border-left: 3px solid #ff6b35;
    background: linear-gradient(135deg, #1a0a00 0%, #250f00 100%);
    border-color: #ff6b3530;
    color: #ffd4b8;
}
.nexus-bubble.error {
    border-left: 3px solid #ff3333;
    background: linear-gradient(135deg, #1a0000 0%, #220000 100%);
    border-color: #ff333330;
    color: #ffb0b0;
}

/* ── Agent tags ── */
.agent-tag {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 3px 9px;
    border-radius: 3px;
    margin: 2px 2px;
    text-transform: uppercase;
    font-weight: 700;
}
.tag-researcher { background: #001433; color: #4ab4ff; border: 1px solid #4ab4ff50; }
.tag-analyst    { background: #0a1a00; color: #88ff44; border: 1px solid #88ff4450; }
.tag-coder      { background: #1a0033; color: #cc88ff; border: 1px solid #cc88ff50; }
.tag-critic     { background: #1a0a00; color: #ff8844; border: 1px solid #ff884450; }
.tag-optimizer  { background: #001a1a; color: #00ffcc; border: 1px solid #00ffcc50; }
.tag-validator  { background: #001a00; color: #44ff88; border: 1px solid #44ff8850; }
.tag-reporter   { background: #1a1a00; color: #ffee44; border: 1px solid #ffee4450; }
.tag-default    { background: #111; color: #aaa; border: 1px solid #333; }

/* ── Meta bar ── */
.meta-bar {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid #0ff2;
    font-size: 12px;
    color: #4a7a9a;
    font-family: 'Share Tech Mono', monospace;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.verdict-approved    { color: #44ff88; font-weight: bold; font-size: 12px; }
.verdict-conditional { color: #ffcc00; font-weight: bold; font-size: 12px; }
.verdict-rejected    { color: #ff4444; font-weight: bold; font-size: 12px; }

/* ── Live progress box ── */
.progress-wrap {
    background: #040810;
    border: 1px solid #0ff3;
    border-left: 3px solid #00ffe7;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
    font-family: 'Share Tech Mono', monospace;
}
.progress-title {
    font-size: 12px;
    color: #00ffe7;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 12px;
    font-weight: 700;
}
.agent-step {
    font-size: 13px;
    color: #7ab8cc;
    padding: 6px 0;
    border-bottom: 1px solid #0ff1;
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
.agent-step:last-child { border-bottom: none; }
.step-icon  { color: #00ffe7; min-width: 20px; font-size: 15px; }
.step-agent { color: #ffffff; font-weight: bold; min-width: 110px; font-size: 13px; }
.step-done  { color: #44ff88; min-width: 20px; font-size: 13px; }
.step-out   { color: #5a8a9a; font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 460px; }

/* ── Chat input ── */
[data-testid="stBottom"] {
    background: #060a0f !important;
    padding: 12px 0 !important;
}
[data-testid="stBottom"] > div {
    background: #060a0f !important;
}
[data-testid="stChatInput"] {
    background: #060a0f !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] > div {
    background: #0d1825 !important;
    border: 1px solid #00ffe750 !important;
    border-radius: 10px !important;
    box-shadow: 0 0 10px #00ffe710 !important;
}
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div {
    background: #0d1825 !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputContainer"] textarea {
    background: #0d1825 !important;
    color: #e2f0ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 15px !important;
    caret-color: #00ffe7 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #3a6a8a !important;
}
/* send button */
[data-testid="stChatInput"] button {
    background: #00ffe720 !important;
    border: 1px solid #00ffe750 !important;
    border-radius: 6px !important;
    color: #00ffe7 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #00ffe740 !important;
    color: #00ffe7 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    padding: 7px 14px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00ffe715 !important;
    border-color: #00ffe7 !important;
    box-shadow: 0 0 12px #00ffe720 !important;
}
.stButton > button p {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #00ffe7 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #080d14 !important;
    border: 1px dashed #1e4a7a !important;
    border-radius: 8px !important;
    padding: 6px !important;
}
[data-testid="stFileUploader"] * {
    color: #7ab0d4 !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 13px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #080d14 !important;
    border: 1px solid #0ff3 !important;
    border-radius: 6px !important;
    padding: 8px !important;
}
[data-testid="stMetricLabel"] {
    color: #4a8aaa !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #00ffe7 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {
    color: #7ab0d4 !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #080d14 !important;
    border: 1px solid #1e4a7a !important;
    color: #b0d4ff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 13px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #060a0f; }
::-webkit-scrollbar-thumb { background: #1e4a7a; border-radius: 2px; }

/* ── File ready badge ── */
.file-ready {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #88ff44;
    padding: 4px 0;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── JS: remove resize handle so sidebar is fully clickable ───────────────────
st.markdown("""
<script>
(function() {
    function removeResizeHandle() {
        // Remove the resize handle element
        var handles = document.querySelectorAll('[data-testid="stSidebarResizeHandle"]');
        handles.forEach(function(el) {
            el.style.display = 'none';
            el.style.pointerEvents = 'none';
            el.style.width = '0';
        });
        // Also target by class
        var handles2 = document.querySelectorAll('.stSidebarResizeHandle');
        handles2.forEach(function(el) {
            el.style.display = 'none';
            el.style.pointerEvents = 'none';
        });
    }
    // Run on load and observe for dynamic changes
    removeResizeHandle();
    var observer = new MutationObserver(removeResizeHandle);
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)


AGENT_ICONS = {
    "Planner":    "📋",
    "Researcher": "🔎",
    "Analyst":    "📊",
    "Coder":      "💻",
    "Critic":     "🔍",
    "Optimizer":  "⚡",
    "Validator":  "✅",
    "Reporter":   "📝",
}

TAG_CLASS = {
    "Researcher": "tag-researcher",
    "Analyst":    "tag-analyst",
    "Coder":      "tag-coder",
    "Critic":     "tag-critic",
    "Optimizer":  "tag-optimizer",
    "Validator":  "tag-validator",
    "Reporter":   "tag-reporter",
}

QUICK_TASKS = [
    ("🏥 Healthcare AI",  "Plan a startup in AI for healthcare"),
    ("⚙ Backend Arch",   "Generate backend architecture for scalable app"),
    ("📊 Sales CSV",      "Analyze sales.csv and create business strategy"),
    ("🔗 RAG Pipeline",   "Design a RAG pipeline for 50k documents"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def agent_tag(name: str) -> str:
    cls  = TAG_CLASS.get(name, "tag-default")
    icon = AGENT_ICONS.get(name, "·")
    return f'<span class="agent-tag {cls}">{icon} {name}</span>'


def verdict_html(text: str) -> str:
    t = text.upper()
    if "APPROVED"    in t: return '<span class="verdict-approved">⬡ APPROVED</span>'
    if "CONDITIONAL" in t: return '<span class="verdict-conditional">◈ CONDITIONAL</span>'
    if "REJECTED"    in t: return '<span class="verdict-rejected">✖ REJECTED</span>'
    return f'<span style="color:#aaa">{text}</span>'


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to BASE_DIR so agents can access it by filename."""
    dest = BASE_DIR / uploaded_file.name
    dest.write_bytes(uploaded_file.getvalue())
    return str(dest)


def read_output_files() -> dict:
    """Read all files from OUTPUT_DIR."""
    files = {}
    out_path = Path(OUTPUT_DIR)
    if out_path.exists():
        for f in sorted(out_path.iterdir()):
            if f.is_file():
                try:
                    files[f.name] = f.read_text(encoding="utf-8")
                except Exception:
                    files[f.name] = "[binary or unreadable file]"
    return files


def escape_html(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


# ── Session state ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "run_count"     not in st.session_state: st.session_state.run_count     = 0
if "last_agents"   not in st.session_state: st.session_state.last_agents   = []
if "last_trace"    not in st.session_state: st.session_state.last_trace    = []
if "quick_trigger" not in st.session_state: st.session_state.quick_trigger = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⬡ NEXUS AI")
    st.markdown(
        '<p style="color:#00ffe780;font-size:13px;margin-top:-8px;'
        'font-family:\'Share Tech Mono\',monospace;letter-spacing:2px;">'
        'AUTONOMOUS MULTI-AGENT</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    # Session stats
    st.markdown("### ⚙ SESSION")
    c1, c2 = st.columns(2)
    c1.metric("Runs",   st.session_state.run_count)
    c2.metric("Agents", len(st.session_state.last_agents))

    st.divider()

    # File upload
    st.markdown("### 📁 FILE UPLOAD")
    st.markdown(
        '<p style="color:#7ab0d4;font-size:12px;margin-top:-8px;">'
        'Upload CSV, PDF, TXT, JSON, PY for agents to use</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Drop file here",
        type=["csv", "pdf", "txt", "json", "md", "py"],
        label_visibility="collapsed",
        help="File saved to project root — reference by filename in your query",
    )
    if uploaded_file:
        st.markdown(
            f'<div class="file-ready">⬡ {uploaded_file.name} &nbsp;ready</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Output files viewer
    st.markdown("### OUTPUT FILES")
    output_files = read_output_files()
    if output_files:
        selected_file = st.selectbox(
            "Select file",
            list(output_files.keys()),
            label_visibility="collapsed",
        )
        if selected_file:
            content = output_files[selected_file]
            if selected_file.endswith(".py"):
                st.code(content, language="python")
            elif selected_file.endswith(".md"):
                st.markdown(content)
            elif selected_file.endswith(".json"):
                st.code(content, language="json")
            else:
                st.text(content[:3000])
    else:
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace;font-size:12px;'
            'color:#1a4a6a;font-weight:600;padding:4px 0;">NO OUTPUT FILES YET</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Last run trace
    if st.session_state.last_trace:
        st.markdown("### 🔍 LAST TRACE")
        for step in st.session_state.last_trace:
            agent = step.get("agent", "?")
            out   = str(step.get("output", ""))[:100]
            icon  = AGENT_ICONS.get(agent, "·")
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;padding:5px 0;'
                f'border-bottom:1px solid #0ff2;">'
                f'<span style="color:#00ffe7;font-family:sans-serif;">{icon}</span> '
                f'<b style="color:#ffffff;font-size:13px;">{agent}</b><br>'
                f'<span style="color:#2a6a8a;font-size:11px;">{out}…</span></div>',
                unsafe_allow_html=True,
            )
        st.divider()

    # Action buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages   = []
            st.session_state.last_trace = []
            st.rerun()
    with col_b:
        if st.button("🗑 Clear Output", use_container_width=True):
            out_path = Path(OUTPUT_DIR)
            if out_path.exists():
                shutil.rmtree(out_path)
                out_path.mkdir(exist_ok=True)
            st.rerun()

    st.divider()
    st.markdown(
        '<div style="font-family:\'Share Tech Mono\',monospace;font-size:11px;'
        'color:#1a4a6a;letter-spacing:2px;font-weight:600;">NEXUS AI // WEEK 9</div>',
        unsafe_allow_html=True,
    )


# ── Main header ───────────────────────────────────────────────────────────────
st.markdown("# ⬡ NEXUS AI")
st.markdown(
    '<div class="nexus-subtitle">'
    'autonomous multi-agent system // plan · research · code · analyze · validate'
    '</div>',
    unsafe_allow_html=True,
)

# Quick task buttons
st.markdown(
    '<p style="color:#4a8aaa;font-family:\'Share Tech Mono\',monospace;'
    'font-size:12px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">'
    'Quick Tasks:</p>',
    unsafe_allow_html=True,
)
qcols = st.columns(4)
for i, (col, (label, prompt)) in enumerate(zip(qcols, QUICK_TASKS)):
    with col:
        if st.button(label, key=f"quick_{i}"):
            st.session_state.quick_trigger = prompt
            st.rerun()

st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">'
            f'<div class="label">// you</div>'
            f'{msg["content"]}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        agents_used = msg.get("agents_used", [])
        verdict     = msg.get("verdict", "")
        duration    = msg.get("duration", "?")
        is_error    = msg.get("is_error", False)
        warn        = "REJECTED" in verdict.upper()
        bubble_cls  = "nexus-bubble error" if is_error else ("nexus-bubble warn" if warn else "nexus-bubble")

        tags  = "".join(agent_tag(a) for a in agents_used)
        vhtml = verdict_html(verdict) if verdict else ""
        meta  = (
            f'<div class="meta-bar">'
            f'{tags}'
            f'{"&nbsp;|&nbsp;" + vhtml if vhtml else ""}'
            f'&nbsp;|&nbsp;⏱ {duration}s'
            f'</div>'
        )
        st.markdown(
            f'<div class="{bubble_cls}">'
            f'<div class="label">// nexus ai</div>'
            f'{escape_html(msg["content"])}'
            f'{meta}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Enter task — e.g. 'Analyze sales.csv and create business strategy'")

# pick up quick trigger from session state
if st.session_state.quick_trigger:
    user_input = st.session_state.quick_trigger
    st.session_state.quick_trigger = None  # clear after use

if user_input:

    # Save uploaded file so agents can access it by filename
    file_path = None
    if uploaded_file:
        file_path = save_uploaded_file(uploaded_file)

    # Store and render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(
        f'<div class="user-bubble">'
        f'<div class="label">// you</div>'
        f'{user_input}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Live progress ─────────────────────────────────────────────────────────
    status_box = st.status("▶ Pipeline starting...", expanded=True)
    agent_steps: list = []

    def render_progress(running_agent: str = ""):
        if running_agent:
            status_box.update(label=f"▶ Running {running_agent}...", state="running")
        for step in agent_steps[-1:]:  # only write new step
            a    = step["agent"]
            out  = step["output"][:80]
            icon = AGENT_ICONS.get(a, "·")
            done = step.get("done", False)
            tick = "✔" if done else "▶"
            color = "#44ff88" if done else "#00ffe7"
            status_box.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:13px;'
                f'padding:4px 0;border-bottom:1px solid #0ff1;display:flex;gap:10px;">'
                f'<span style="color:{color};min-width:16px;">{tick}</span>'
                f'<span style="color:#fff;font-weight:bold;min-width:100px;">{icon} {a}</span>'
                f'<span style="color:#5a8a9a;font-size:12px;">{out}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Execute pipeline ──────────────────────────────────────────────────────
    t0         = time.time()
    error_msg  = None
    results    = {}
    plan_steps = 0
    verdict    = ""

    try:
        from agents.planner      import planner, ExecutionPlan
        from agents.orchestrator import run_autonomous_loop, memory_manager
        from autogen_agentchat.messages import TextMessage
        import json as _json
        import re  as _re

        # Append filename to query if file was uploaded
        query = user_input
        if file_path:
            fname = Path(file_path).name
            if fname not in query:
                query = f"{query} (file: {fname})"

        # Retrieve memory context
        memory_context = memory_manager.retrieve_context(query)
        enhanced_query = (
            f"USER REQUEST:\n{query}\n\n"
            f"MEMORY CONTEXT:\n{memory_context[:800]}"
        )

        # Plan step
        agent_steps.append({"agent": "Planner", "output": "Generating execution plan...", "done": False})
        render_progress("Planner")

        plan_result = run_async(
            planner.run(task=TextMessage(content=enhanced_query, source="user"))
        )
        raw = plan_result.messages[-1].content

        try:
            plan_data = _json.loads(raw)
        except _json.JSONDecodeError:
            match     = _re.search(r"\{.*\}", raw, _re.DOTALL)
            plan_data = _json.loads(match.group()) if match else {"steps": []}

        execution_plan = ExecutionPlan(**plan_data)
        plan_steps     = len(execution_plan.steps)

        agent_steps[-1]["output"] = (
            f"{plan_steps} steps: "
            f"{', '.join(s.agent for s in execution_plan.steps)}"
        )
        agent_steps[-1]["done"] = True
        render_progress()

        create_log_entry(
            str(LOG_FILE_PATH), "planner", "plan_generated", {"steps": plan_data}
        )

        # Patch orchestrator for live progress updates
        try:
            import agents.orchestrator as _orch
            _original_fn = _orch.run_agent_with_retry

            async def _patched(agent_name, instruction, global_context, user_query):
                agent_steps.append({
                    "agent":  agent_name,
                    "output": instruction[:70] + "...",
                    "done":   False,
                })
                render_progress(agent_name)
                result = await _original_fn(agent_name, instruction, global_context, user_query)
                out = result.get("output", result.get("error", ""))
                agent_steps[-1]["output"] = str(out)[:80]
                agent_steps[-1]["done"]   = True
                render_progress()
                return result

            _orch.run_agent_with_retry = _patched
            results = run_async(run_autonomous_loop(execution_plan, query))
            _orch.run_agent_with_retry = _original_fn

        except AttributeError:
            results = run_async(run_autonomous_loop(execution_plan, query))

        # Extract verdict
        if "Validator" in results:
            v_out = str(results["Validator"])
            if   "APPROVED"    in v_out.upper(): verdict = "APPROVED"
            elif "REJECTED"    in v_out.upper(): verdict = "REJECTED"
            else:                                verdict = "CONDITIONAL"

    except Exception as e:
        error_msg = str(e)
        agent_steps.append({"agent": "System", "output": f"ERROR: {error_msg[:80]}", "done": True})
        render_progress()

    duration = round(time.time() - t0, 1)
    if error_msg:
        status_box.update(label=f"✖ Pipeline failed after {duration}s", state="error")
    else:
        status_box.update(label=f"✔ Pipeline complete — {duration}s", state="complete")

    # ── Build response text ───────────────────────────────────────────────────
    is_error    = False
    agents_used = [
        s["agent"] for s in agent_steps
        if s["agent"] not in ("Planner", "System")
    ]
    agents_used = list(dict.fromkeys(agents_used))

    if error_msg and not results:
        response_text = f"Pipeline error:\n{error_msg}"
        is_error      = True
        agents_used   = []

    elif "system_error" in results:
        response_text = f"System error:\n{results['system_error']}"
        is_error      = True

    elif "Reporter" in results:
        response_text = str(results["Reporter"])

    else:
        lines = [f"Pipeline complete — {plan_steps} agents ran in {duration}s\n"]
        for agent, out in results.items():
            if out and str(out).strip():
                lines.append(f"{agent}:\n{str(out)[:400]}\n")
        response_text = "\n".join(lines)

    # Note any saved output files
    out_path = Path(OUTPUT_DIR)
    md_files = list(out_path.glob("*.md")) if out_path.exists() else []
    if md_files:
        names = ", ".join(f.name for f in md_files)
        response_text += f"\n\n📄 Files saved to Output/: {names}"

    # ── Store and render ──────────────────────────────────────────────────────
    st.session_state.messages.append({
        "role":        "assistant",
        "content":     response_text,
        "agents_used": agents_used,
        "verdict":     verdict,
        "duration":    duration,
        "is_error":    is_error,
    })
    st.session_state.run_count  += 1
    st.session_state.last_agents = agents_used
    st.session_state.last_trace  = [
        {"agent": a, "output": str(results.get(a, ""))[:300]}
        for a in agents_used
    ]

    create_log_entry(str(LOG_FILE_PATH), "system", "ui_run_complete", {
        "query": user_input, "agents": agents_used, "duration": duration,
    })

    st.rerun()