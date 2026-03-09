
# FINAL-REPORT.md
# Week 8 — Day 5
## Capstone: Local LLM API Deployment

This capstone demonstrates deploying a fine-tuned and quantized TinyLlama model as a local LLM API with an interactive UI.

The system exposes endpoints for text generation and chat, supports streaming responses, and includes a Streamlit interface.

---

# Objective

Deploy the quantized TinyLlama model as a local microservice that can:

- Generate responses from prompts
- Handle chat conversations
- Stream tokens in real time
- Be accessed through API and UI

---

# Model Used

Base Model: TinyLlama-1.1B-Chat

Pipeline used:

TinyLlama Base Model  
LoRA Fine-Tuning  
Merge Adapter  
Quantization (GGUF q8_0)  
Local Deployment

The model runs using llama.cpp for efficient CPU inference.

---

# API Endpoints

The model is deployed using FastAPI.

### POST /generate

Used for single prompt generation.

Example request:

{
  "prompt": "Explain employee engagement.",
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 200
}

---

### POST /chat

Used for conversational interaction with chat history.

Example request:

{
  "system": "You are an HR assistant.",
  "messages": [
    {
      "role": "user",
      "content": "What is employee onboarding?"
    }
  ]
}

---

# Running the Application

## 1. Start the FastAPI Server

Run the API server:

```bash
uvicorn deploy.app:app --host 0.0.0.0 --port 8000 --reload
```

API documentation will be available at:

http://localhost:8000/docs

---

## 2. Run the Streamlit Interface

```bash
streamlit run deploy/streamlit.py
```

Open:

http://localhost:8501

---

## 3. Test API with CURL

Example:

```bash
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{
"system":"You are an HR assistant",
"messages":[{"role":"user","content":"What is performance appraisal?"}],
"temperature":0.7,
"top_p":0.9,
"top_k":40,
"max_tokens":200
}'
```

---

# System Workflow

User Interface (Streamlit)  
FastAPI Server  
llama.cpp Inference Engine  
Quantized TinyLlama Model

---

# Screenshots

## Swagger API Test

![Swagger Test](ss/day5ss/post-chat-waggerui.png)

---

## Streamlit Interface

![Streamlit UI](ss/day5ss/streamlitop.png)

---

## CURL API Test

![Curl Test](ss/day5ss/usingcurl.png)

---

# Result

The deployed system successfully provides:

- Local LLM inference
- REST API endpoints
- Chat interface
- Streaming responses
- Adjustable generation parameters

The architecture can be extended for RAG systems, AI assistants, or agent workflows.
