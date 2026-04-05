import os
import asyncio
import sqlite3
import pandas as pd
import streamlit as st
from orchestrator.orchestrator import Orchestrator
from tools.file_agent import FileAgent

st.set_page_config(
    page_title="AutoGen Multi-Agent System",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — no Google Fonts, full contrast, readable everywhere ─────────────────
st.markdown("""
<style>
html, body, .stApp {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Ubuntu',
                 'Helvetica Neue', Arial, sans-serif !important;
    color: #f1f5f9 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background-color: #161b2e !important;
    border-right: 1px solid #2e3650 !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h2 {
    color: #ffffff !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
}

.stApp { background-color: #0d1117 !important; }

h1 {
    color: #ffffff !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.01em !important;
    margin-bottom: 0 !important;
}
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
}

[data-testid="stChatMessage"] {
    background-color: #161b2e !important;
    border: 1px solid #2e3650 !important;
    border-radius: 10px !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] label {
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
}

[data-testid="stCode"] pre,
[data-testid="stCode"] code,
.stCode pre, .stCode code {
    background-color: #0a0e1a !important;
    color: #c9d1d9 !important;
    font-family: 'Cascadia Code', 'Fira Code', 'Courier New', monospace !important;
    font-size: 0.83rem !important;
    border: 1px solid #2e3650 !important;
    border-radius: 6px !important;
}

[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #2e3650 !important;
    border-radius: 8px !important;
    margin-top: 0.4rem !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #cbd5e1 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}
[data-testid="stMarkdownContainer"] strong { color: #ffffff !important; }

[data-testid="stChatInput"] textarea {
    background-color: #161b2e !important;
    border: 1px solid #2e3650 !important;
    color: #f1f5f9 !important;
    font-size: 0.95rem !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #64748b !important; }

.stButton button {
    background-color: #1e2a45 !important;
    color: #e2e8f0 !important;
    border: 1px solid #2e3650 !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
}
.stButton button:hover {
    background-color: #263354 !important;
    border-color: #4a5568 !important;
}

[data-testid="stAlert"] {
    border-radius: 6px !important;
    font-size: 0.85rem !important;
}
[data-testid="stAlert"] p { color: inherit !important; }

[data-testid="stFileUploader"] {
    background-color: #111827 !important;
    border: 1px dashed #2e3650 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] * { color: #cbd5e1 !important; }

hr { border-color: #2e3650 !important; margin: 0.8rem 0 !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #2e3650; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = Orchestrator()
    if "file_agent" not in st.session_state:
        # FileAgent auto-creates data/ and output/ folders on init
        base_dir = os.path.abspath(os.path.dirname(__file__))
        st.session_state.file_agent = FileAgent(base_dir=base_dir)
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None

init_state()

# Convenience reference
file_agent: FileAgent = st.session_state.file_agent


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Upload CSV")

    # ── Show sandbox folder info ───────────────────────────────────────────
    st.markdown(
        f"<small style='color:#64748b'>📁 Source files → <code>data/</code><br>"
        f"📁 Agent output → <code>output/</code></small>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    uploaded = st.file_uploader(
        label="CSV file",
        type=["csv"],
        label_visibility="collapsed",
    )

    if uploaded:
        if st.session_state.uploaded_file_name != uploaded.name:
            st.session_state.uploaded_file_name = uploaded.name

            # ── Save to data/ sandbox (read-only) ─────────────────────────
            msg = file_agent.save_uploaded_file(uploaded.name, uploaded.getbuffer())
            save_path = os.path.join(file_agent.read_sandbox, uploaded.name)

            if "already exists" in msg:
                st.info(f"ℹ {uploaded.name} already in data/ — not overwritten.")
            else:
                st.success(f"✓ Saved to data/{uploaded.name}")

            # ── Also import into SQLite for DB agent queries ───────────────
            db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "multiagent.db")
            table   = os.path.splitext(uploaded.name)[0]
            conn    = sqlite3.connect(db_path)
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,),
                )
                if cur.fetchone():
                    st.info(f"Table '{table}' already exists in DB — skipping import.")
                else:
                    df = pd.read_csv(save_path)
                    df.to_sql(table, conn, if_exists="replace", index=False)
                    st.success(f"✓ Imported {len(df)} rows → DB table '{table}'")
            except Exception as e:
                st.error(f"DB import failed: {e}")
            finally:
                conn.close()
        else:
            st.success(f"✓ {uploaded.name} already loaded.")

    st.markdown("---")
    st.markdown("**Session**")
    if st.button("🗑  Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Agent result renderer ─────────────────────────────────────────────────────

AGENT_LABELS = {
    "code":     "⚙  CODE AGENT RESULT",
    "file":     "📄  FILE AGENT RESULT",
    "database": "🗄  DATABASE AGENT RESULT",
}

def render_agent_result(agent_name: str, result):
    label = AGENT_LABELS.get(agent_name, f"• {agent_name.upper()} AGENT RESULT")
    with st.expander(label, expanded=True):
        if isinstance(result, dict) and "generated_code" in result:
            gen = result.get("generated_code", "").strip()
            out = result.get("execution_result", "").strip()
            if gen and not gen.startswith("built-in"):
                st.markdown("**Generated Code**")
                st.code(gen, language="python")
            if out:
                st.markdown("**Output**")
                st.code(out, language="text")
        else:
            st.code(str(result), language="text")


# ── Async runner ──────────────────────────────────────────────────────────────

async def run_request(user_input: str):
    status = st.empty()
    def update_status(msg: str):
        status.markdown(f"*◌ {msg}*")
    result = await st.session_state.orchestrator.process_request(
        user_input, status_callback=update_status,
    )
    status.empty()
    return result


# ── Main UI ───────────────────────────────────────────────────────────────────

st.title("AutoGen Multi-Agent System")
st.caption("Tool-calling agents for code execution · file operations · database queries")
st.markdown("---")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "details" in msg:
            for agent_name, agent_result in msg["details"]["agent_results"].items():
                render_agent_result(agent_name, agent_result)

if prompt := st.chat_input("Enter your request..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        result = asyncio.run(run_request(prompt))
        final  = result.get("final_answer", "").strip()
        st.markdown(final)
        for agent_name, agent_result in result.get("agent_results", {}).items():
            render_agent_result(agent_name, agent_result)

    st.session_state.messages.append({
        "role": "assistant", "content": final, "details": result,
    })