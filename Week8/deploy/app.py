import uuid
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from deploy.config import DEFAULT_TEMP, DEFAULT_TOP_P, DEFAULT_TOP_K
from deploy.model_loader import load_model

# -------------------- LOGGING SETUP --------------------
logging.basicConfig(
    filename="logs/app.log",   # make sure logs/ folder exists
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -------------------- APP INIT --------------------
app = FastAPI(title="Local LLM API")

hr_llm = load_model("hr")
base_llm = load_model("base")
logging.info("Models loaded successfully")

# -------------------- REQUEST MODELS --------------------
class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = DEFAULT_TEMP
    top_p: float = DEFAULT_TOP_P
    top_k: int = DEFAULT_TOP_K
    max_tokens: int = 256
    stream: bool = True


class ChatRequest(BaseModel):
    system: str = ""
    messages: list = []
    temperature: float = DEFAULT_TEMP
    top_p: float = DEFAULT_TOP_P
    top_k: int = DEFAULT_TOP_K
    max_tokens: int = 256
    stream: bool = True


# -------------------- QUERY ROUTER --------------------
def is_hr_query(query: str):
    hr_keywords = [
        "leave", "salary", "policy", "employee",
        "benefits", "attendance", "recruitment",
        "hr", "performance", "onboarding", "appraisal",
        "termination", "resignation", "payroll", "grievance",
        "training", "promotion", "workplace", "conduct"
    ]
    return any(word in query.lower() for word in hr_keywords)


# -------------------- SYSTEM PROMPTS --------------------
HR_SYSTEM_PROMPT = """You are a strict HR assistant. You ONLY answer HR-related questions.
When answering, you MUST follow this exact format:

Step 1: [First action]
Step 2: [Second action]
Step 3: [Third action]
...continue steps as needed...

Rules:
- Always use numbered steps. Never use paragraphs.
- Be specific and practical (cite real HR practices)
- Maximum 6 steps
- Do NOT generate extra Q&A after your answer
- Do NOT repeat the question
- End your answer after the last step

Answer:"""

GENERAL_SYSTEM_PROMPT = """You are a task-completion AI assistant. Directly complete the user's request.

STRICT RULES:
- DO NOT ask questions
- DO NOT ask for preferences  
- DO NOT request clarification
- DO NOT simulate conversation

- se Day 1, Day 2... format only when the user asks for a plan, schedule, roadmap, or stepwise workflow.
- Include subjects/topics per day
- Keep it practical and realistic
- Do NOT ask questions

Always give a COMPLETE, DETAILED answer. Never give a one-paragraph vague response.

Answer:"""


# -------------------- PROMPT BUILDER --------------------
def build_chat_prompt(system, messages):
    prompt = f"{system.strip()}\n\n"
    for m in messages:
        role = m["role"].capitalize()
        prompt += f"{role}: {m['content'].strip()}\n"
    prompt += "\nComplete the full answer. Do not stop early.\nAssistant:"
    return prompt


# -------------------- STREAM FUNCTION --------------------
def stream_tokens(model, prompt, params, request_id):
    stop_words = ["\nUser:", "\nAssistant:"]
    buffer = ""

    logging.info(f"[{request_id}] Streaming started")

    for chunk in model(prompt, stream=True, stop=stop_words, **params):
        token = chunk["choices"][0]["text"]
        buffer += token

        if buffer.strip().endswith(tuple(stop_words)):
            break

        yield token

    logging.info(f"[{request_id}] Streaming completed")


# -------------------- GENERATE --------------------
@app.post("/generate")
def generate(req: GenerateRequest):
    request_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    logging.info(f"[{request_id}] /generate called")
    logging.info(f"[{request_id}] Prompt: {req.prompt}")

    model = hr_llm if is_hr_query(req.prompt) else base_llm

    params = dict(
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
    )

    response = StreamingResponse(
        stream_tokens(model, req.prompt, params, request_id),
        media_type="text/plain"
    )

    logging.info(f"[{request_id}] Response started")

    return response


# -------------------- CHAT --------------------
@app.post("/chat")
def chat(req: ChatRequest):
    request_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    logging.info(f"[{request_id}] /chat called")
    logging.info(f"[{request_id}] Messages: {req.messages}")

    user_query = req.messages[-1]["content"]

    # Modify non-HR queries
    if not is_hr_query(user_query):
        user_query = "Answer directly. Do not ask questions. " + user_query
        req.messages[-1]["content"] = user_query

    # Routing
    if is_hr_query(user_query):
        system_prompt = HR_SYSTEM_PROMPT
        model = hr_llm
        logging.info(f"[{request_id}] Using HR model")
    else:
        system_prompt = GENERAL_SYSTEM_PROMPT
        model = base_llm
        logging.info(f"[{request_id}] Using BASE model")

    prompt = build_chat_prompt(system_prompt, req.messages)

    params = dict(
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
    )

    response = StreamingResponse(
        stream_tokens(model, prompt, params, request_id),
        media_type="text/plain"
    )

    logging.info(f"[{request_id}] Response started")

    return response