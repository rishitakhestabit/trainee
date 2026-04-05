import streamlit as st
import requests

API_URL_CHAT = "http://localhost:8000/chat"
API_URL_GENERATE = "http://localhost:8000/generate"
MAX_HISTORY = 3

st.set_page_config(page_title="HR LLM", layout="wide")
st.markdown(
    "<h1 style='text-align:center;'>"
    "<span style='color:#7C3AED;'>HR LLM Chatbot</span> "
    "</h1>",
    unsafe_allow_html=True
)
st.sidebar.header("Settings")

mode = st.sidebar.radio("Mode", ["Chat", "Single Prompt"])

temp = st.sidebar.slider("Temperature", 0.1, 1.5, 0.7)
top_p = st.sidebar.slider("Top-P", 0.1, 1.0, 0.9)
top_k = st.sidebar.slider("Top-K", 10, 100, 40)


if mode == "Chat":
    st.subheader("Chat Mode")
    system_prompt = st.sidebar.text_area(
        "System Prompt",
    """You are a knowledgeable AI assistant.
    Rules:
    - Answer the question directly and completely.
    - Do NOT ask follow-up questions or request clarifications.
    - Do NOT simulate a conversation or generate fake dialogues.
    - Do NOT include 'User:' or 'Assistant:' in your response.
    - Give a full, complete answer in one response."""
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        st.chat_message(m["role"]).markdown(m["content"])

    user_input = st.chat_input("Ask something...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]
        st.chat_message("user").markdown(user_input)

        payload = {
            "system": system_prompt,
            "messages": st.session_state.messages,
            "temperature": temp,
            "top_p": top_p,
            "top_k": top_k,
            "stream": True
        }

        response = requests.post(API_URL_CHAT, json=payload, stream=True)

        assistant_text = ""
        with st.chat_message("assistant"):
            box = st.empty()
            for chunk in response.iter_content(chunk_size=1):
                if chunk:
                    assistant_text += chunk.decode("utf-8")
                    box.markdown(assistant_text)

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_text}
        )

else:
    st.subheader("Single Question Mode")

    prompt = st.text_area("Enter your prompt:")

    if st.button("Generate"):
        payload = {
            "prompt": prompt,
            "temperature": temp,
            "top_p": top_p,
            "top_k": top_k,
            "stream": True
        }

        response = requests.post(API_URL_GENERATE, json=payload, stream=True)

        output_text = ""
        box = st.empty()

        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                output_text += chunk.decode("utf-8")
                box.markdown(output_text)