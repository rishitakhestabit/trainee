# import streamlit as st
# import requests
# import os

# API = "http://127.0.0.1:8000"

# st.set_page_config(page_title="RAG System", layout="wide")
# st.title("Week 7 Production RAG System")

# # ================= TABS =================
# tab1, tab2, tab3 = st.tabs(["Text RAG", "Image RAG", "SQL RAG"])


# # =========================================================
# # TEXT RAG
# # =========================================================
# with tab1:
#     st.subheader("Upload PDF")

#     uploaded_file = st.file_uploader("Upload document", type=["pdf"])

#     # ✅ FIX: Re-ingestion bug
#     # Streamlit reruns the ENTIRE script on every single interaction —
#     # clicking "Ask", typing in a text box, anything.
#     # Without session_state, the upload block fires the API every rerun.
#     # Fix: track ingested filename in session_state. Only call /ingest
#     # when a genuinely new file is uploaded (name changed or first time).
#     if uploaded_file is not None:
#         already_ingested = (
#             st.session_state.get("ingested_file") == uploaded_file.name
#         )

#         if not already_ingested:
#             try:
#                 save_dir = "src/data/raw"
#                 os.makedirs(save_dir, exist_ok=True)
#                 file_path = os.path.join(save_dir, uploaded_file.name)

#                 with open(file_path, "wb") as f:
#                     f.write(uploaded_file.getvalue())

#                 with st.spinner("Ingesting document..."):
#                     response = requests.post(
#                         f"{API}/ingest",
#                         json={"file_path": file_path}
#                     )

#                 if response.status_code != 200:
#                     st.error("Ingestion API error")
#                 else:
#                     res = response.json()
#                     if "error" in res:
#                         st.error(res["error"])
#                     else:
#                         # Mark as ingested — won't trigger again on next rerun
#                         st.session_state["ingested_file"] = uploaded_file.name
#                         st.session_state["ingested_chunks"] = res.get("chunks", 0)
#                         st.success(
#                             f" Ingested **{uploaded_file.name}** — "
#                             f"{res.get('chunks', 0)} chunks created"
#                         )

#             except Exception as e:
#                 st.error(f"Upload failed: {str(e)}")
#         else:
#             # Same file still shown — just display status, no API call
#             st.success(
#                 f" Already ingested: **{uploaded_file.name}** — "
#                 f"{st.session_state.get('ingested_chunks', 0)} chunks"
#             )

#     st.divider()

#     st.subheader("Ask Question")
#     st.caption(
#         "💡 Tip: Just ask your question to use the **latest uploaded PDF**. "
#         "To target a specific PDF, include part of its name — e.g. 'what is RAG in week-7'"
#     )

#     query = st.text_input("Enter your question")

#     if st.button("Ask"):
#         if not query.strip():
#             st.warning("Please enter a question")
#         else:
#             try:
#                 with st.spinner("Generating answer..."):
#                     response = requests.post(
#                         f"{API}/ask",
#                         json={"query": query}
#                     )

#                 if response.status_code != 200:
#                     st.error("API error")
#                 else:
#                     res = response.json()

#                     if "error" in res:
#                         st.error(res["error"])
#                     else:
#                         st.write("### Answer")
#                         st.write(res.get("answer"))

#                         # Metrics
#                         if "eval" in res:
#                             eval_data = res["eval"]
#                             col1, col2, col3 = st.columns(3)
#                             col1.metric(
#                                 "Confidence",
#                                 round(eval_data.get("confidence", 0), 3)
#                             )
#                             col2.metric(
#                                 "Faithfulness",
#                                 round(eval_data.get("faithfulness", 0), 3)
#                             )
#                             col3.metric(
#                                 "Latency (sec)",
#                                 eval_data.get("latency", 0)
#                             )
#                             st.write(f"Quality: {eval_data.get('quality')}")
#                             st.progress(
#                                 float(eval_data.get("confidence", 0))
#                             )

#                         # Sources
#                         if "sources" in res and res["sources"]:
#                             st.write("### Sources Used")
#                             for s in res["sources"]:
#                                 src = s.get("source", "unknown")
#                                 page = s.get("page", "?")
#                                 preview = s.get("preview", "")
#                                 with st.expander(f"📄 {src} — page {page}"):
#                                     st.write(preview)

#             except Exception as e:
#                 st.error(f"Request failed: {str(e)}")


# # =========================================================
# # IMAGE RAG
# # =========================================================
# with tab2:
#     st.subheader("Image Search")

#     mode = st.selectbox("Mode", ["text2img", "img2img"])
#     img_query = st.text_input("Enter text query", key="img_query")
#     uploaded_img = st.file_uploader("Upload image", type=["jpg", "png"])

#     img_path = None
#     if uploaded_img is not None:
#         try:
#             os.makedirs("src/data/raw", exist_ok=True)
#             img_path = f"src/data/raw/{uploaded_img.name}"
#             with open(img_path, "wb") as f:
#                 f.write(uploaded_img.getvalue())
#         except Exception as e:
#             st.error(f"Image upload failed: {str(e)}")

#     if st.button("Search Image"):
#         try:
#             if mode == "img2img" and not img_path:
#                 st.warning("Please upload an image for img2img mode")
#             else:
#                 payload = {
#                     "mode": mode,
#                     "query": img_query,
#                     "image_path": img_path,
#                     "top_k": 3,
#                 }
#                 with st.spinner("Searching images..."):
#                     response = requests.post(f"{API}/ask-image", json=payload)

#                 if response.status_code != 200:
#                     st.error("API error")
#                 else:
#                     res = response.json()
#                     if "error" in res:
#                         st.error(res["error"])
#                     else:
#                         if "eval" in res:
#                             st.write(
#                                 f"Latency: {res['eval'].get('latency', 0)} sec"
#                             )
#                         st.write("### Results")
#                         for r in res.get("results", []):
#                             st.image(
#                                 r["source"],
#                                 caption=f"Score: {round(r['score'], 3)}"
#                             )

#         except Exception as e:
#             st.error(f"Request failed: {str(e)}")


# # =========================================================
# # SQL RAG
# # =========================================================
# with tab3:
#     st.subheader("SQL Question Answering")

#     question = st.text_input("Enter SQL question")

#     if st.button("Run SQL"):
#         if not question.strip():
#             st.warning("Please enter a question")
#         else:
#             try:
#                 with st.spinner("Executing SQL..."):
#                     response = requests.post(
#                         f"{API}/ask-sql",
#                         json={"question": question}
#                     )

#                 if response.status_code != 200:
#                     st.error("API error")
#                 else:
#                     res = response.json()
#                     if "error" in res:
#                         st.error(res["error"])
#                     else:
#                         st.write("### Generated SQL")
#                         st.code(res.get("sql"))

#                         st.write("### Result Summary")
#                         st.write(res.get("summary"))

#                         if "eval" in res:
#                             eval_data = res["eval"]
#                             col1, col2, col3 = st.columns(3)
#                             col1.metric(
#                                 "Confidence",
#                                 round(eval_data.get("confidence", 0), 3)
#                             )
#                             col2.metric(
#                                 "Faithfulness",
#                                 round(eval_data.get("faithfulness", 0), 3)
#                             )
#                             col3.metric(
#                                 "Latency (sec)",
#                                 eval_data.get("latency", 0)
#                             )
#                             st.write(f"Quality: {eval_data.get('quality')}")

#             except Exception as e:
#                 st.error(f"Request failed: {str(e)}")

import streamlit as st
import requests
import os
import subprocess
import time
import sys

def _start_fastapi():
    # Check if already running
    try:
        r = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if r.status_code == 200:
            return  # already up, nothing to do
    except Exception:
        pass  # not running yet — start it

    # Launch uvicorn in the background
    subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "src.deployment.app:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for it to come up (max 10 seconds)
    for _ in range(20):
        try:
            r = requests.get("http://127.0.0.1:8000/docs", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.5)

# Only run once per Streamlit session
if "fastapi_started" not in st.session_state:
    _start_fastapi()
    st.session_state["fastapi_started"] = True

# =========================================================

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG System", layout="wide")

# ================= COLOURS ONLY =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}

h1 { color: #58a6ff !important; }
h2, h3 { color: #e6edf3 !important; }

[data-testid="stTabs"] [role="tablist"] {
    background: #161b22 !important;
    border-radius: 8px !important;
    padding: 4px !important;
    border: 1px solid #30363d !important;
}
[data-testid="stTabs"] [role="tab"] {
    color: #8b949e !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #58a6ff !important;
    color: #0d1117 !important;
}

[data-testid="stTextInput"] input {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
}
[data-testid="stTextInput"] label { color: #8b949e !important; }

[data-testid="stFileUploader"] {
    background: #161b22 !important;
    border: 2px dashed #30363d !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] { background: #161b22 !important; }

[data-testid="stButton"] button {
    background: #238636 !important;
    color: #ffffff !important;
    border: 1px solid #2ea043 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button:hover { background: #2ea043 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] label { color: #8b949e !important; }

[data-testid="stMetric"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetric"] label { color: #8b949e !important; }
[data-testid="stMetricValue"] { color: #58a6ff !important; }

[data-testid="stSuccess"] {
    background: rgba(35,134,54,0.15) !important;
    border: 1px solid #2ea043 !important;
    color: #3fb950 !important;
    border-radius: 8px !important;
}
[data-testid="stError"] {
    background: rgba(248,81,73,0.15) !important;
    border: 1px solid #f85149 !important;
    color: #f85149 !important;
    border-radius: 8px !important;
}
[data-testid="stWarning"] {
    background: rgba(210,153,34,0.15) !important;
    border: 1px solid #d29922 !important;
    color: #e3b341 !important;
    border-radius: 8px !important;
}

[data-testid="stExpander"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary { color: #58a6ff !important; }

[data-testid="stProgress"] > div {
    background: #21262d !important;
    border-radius: 999px !important;
}
[data-testid="stProgress"] > div > div {
    background: #58a6ff !important;
    border-radius: 999px !important;
}

[data-testid="stCode"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}

hr { border-color: #30363d !important; }
[data-testid="stCaptionContainer"] { color: #8b949e !important; }
[data-testid="stMarkdownContainer"] p { color: #e6edf3 !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.title("Week 7 Production RAG System")

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(["Text RAG", "Image RAG", "SQL RAG"])


# =========================================================
# TEXT RAG
# =========================================================
with tab1:
    st.subheader("Upload PDF")

    uploaded_file = st.file_uploader("Upload document", type=["pdf"])

    if uploaded_file is not None:
        already_ingested = (
            st.session_state.get("ingested_file") == uploaded_file.name
        )

        if not already_ingested:
            try:
                save_dir = "src/data/raw"
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, uploaded_file.name)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                with st.spinner("Ingesting document..."):
                    response = requests.post(
                        f"{API}/ingest",
                        json={"file_path": file_path}
                    )

                if response.status_code != 200:
                    st.error("Ingestion API error")
                else:
                    res = response.json()
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.session_state["ingested_file"] = uploaded_file.name
                        st.session_state["ingested_chunks"] = res.get("chunks", 0)
                        st.success(
                            f"✅ Ingested **{uploaded_file.name}** — "
                            f"{res.get('chunks', 0)} chunks created"
                        )

            except Exception as e:
                st.error(f"Upload failed: {str(e)}")
        else:
            st.success(
                f" Already ingested: **{uploaded_file.name}** — "
                f"{st.session_state.get('ingested_chunks', 0)} chunks"
            )

    st.divider()

    st.subheader("Ask Question")
    st.caption(
        "💡 Tip: Just ask your question to use the latest uploaded PDF. "
        "To target a specific PDF, include part of its name — e.g. 'what is RAG in week-7'"
    )

    query = st.text_input("Enter your question")

    if st.button("Ask"):
        if not query.strip():
            st.warning("Please enter a question")
        else:
            try:
                with st.spinner("Generating answer..."):
                    response = requests.post(f"{API}/ask", json={"query": query})

                if response.status_code != 200:
                    st.error("API error")
                else:
                    res = response.json()

                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.write("### Answer")
                        st.write(res.get("answer"))

                        if "eval" in res:
                            eval_data = res["eval"]
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Confidence", round(eval_data.get("confidence", 0), 3))
                            col2.metric("Faithfulness", round(eval_data.get("faithfulness", 0), 3))
                            col3.metric("Latency (sec)", eval_data.get("latency", 0))
                            st.write(f"Quality: {eval_data.get('quality')}")
                            st.progress(float(eval_data.get("confidence", 0)))

                        if "sources" in res and res["sources"]:
                            st.write("### Sources Used")
                            for s in res["sources"]:
                                src = s.get("source", "unknown")
                                page = s.get("page", "?")
                                preview = s.get("preview", "")
                                with st.expander(f"📄 {src} — page {page}"):
                                    st.write(preview)

            except Exception as e:
                st.error(f"Request failed: {str(e)}")


# =========================================================
# IMAGE RAG
# =========================================================
with tab2:
    st.subheader("Image Search")

    mode = st.selectbox("Mode", ["text2img", "img2img"])
    img_query = st.text_input("Enter text query", key="img_query")
    uploaded_img = st.file_uploader("Upload image", type=["jpg", "png"])

    img_path = None
    if uploaded_img is not None:
        try:
            os.makedirs("src/data/raw", exist_ok=True)
            img_path = f"src/data/raw/{uploaded_img.name}"
            with open(img_path, "wb") as f:
                f.write(uploaded_img.getvalue())
        except Exception as e:
            st.error(f"Image upload failed: {str(e)}")

    if st.button("Search Image"):
        try:
            if mode == "img2img" and not img_path:
                st.warning("Please upload an image for img2img mode")
            else:
                payload = {
                    "mode": mode,
                    "query": img_query,
                    "image_path": img_path,
                    "top_k": 3,
                }
                with st.spinner("Searching images..."):
                    response = requests.post(f"{API}/ask-image", json=payload)

                if response.status_code != 200:
                    st.error("API error")
                else:
                    res = response.json()
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        if "eval" in res:
                            st.write(f"Latency: {res['eval'].get('latency', 0)} sec")
                        st.write("### Results")
                        for r in res.get("results", []):
                            st.image(r["source"], caption=f"Score: {round(r['score'], 3)}")

        except Exception as e:
            st.error(f"Request failed: {str(e)}")


# =========================================================
# SQL RAG
# =========================================================
with tab3:
    st.subheader("SQL Question Answering")

    question = st.text_input("Enter SQL question")

    if st.button("Run SQL"):
        if not question.strip():
            st.warning("Please enter a question")
        else:
            try:
                with st.spinner("Executing SQL..."):
                    response = requests.post(f"{API}/ask-sql", json={"question": question})

                if response.status_code != 200:
                    st.error("API error")
                else:
                    res = response.json()
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.write("### Generated SQL")
                        st.code(res.get("sql"))

                        st.write("### Result Summary")
                        st.write(res.get("summary"))

                        if "eval" in res:
                            eval_data = res["eval"]
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Confidence", round(eval_data.get("confidence", 0), 3))
                            col2.metric("Faithfulness", round(eval_data.get("faithfulness", 0), 3))
                            col3.metric("Latency (sec)", eval_data.get("latency", 0))
                            st.write(f"Quality: {eval_data.get('quality')}")

            except Exception as e:
                st.error(f"Request failed: {str(e)}")