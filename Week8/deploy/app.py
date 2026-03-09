import uuid, logging
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from deploy.config import DEFAULT_TEMP, DEFAULT_TOP_P, DEFAULT_TOP_K
from deploy.model_loader import load_model

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Local LLM API")

llm = load_model()
print("model loaded")

class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = DEFAULT_TEMP
    top_p: float = DEFAULT_TOP_P
    top_k: int = DEFAULT_TOP_K
    max_tokens: int = 256
    stream: bool = True

class ChatRequest(BaseModel):
    system: str
    messages: list
    temperature: float = DEFAULT_TEMP
    top_p: float = DEFAULT_TOP_P
    top_k: int = DEFAULT_TOP_K
    max_tokens: int = 256
    stream: bool = True

def build_chat_prompt(system, messages):
    prompt = f"<|system|>\n{system}\n"
    prompt+="Previous Conversation: \n"
    for m in messages:
        prompt += f"<|{m['role']}|>\n{m['content']}\n"
    prompt += "<|assistant|>\n"
    return prompt


def stream_tokens(prompt, params):
    for chunk in llm(prompt, stream=True, **params):
        token = chunk["choices"][0]["text"]
        yield token


@app.post("/generate")
def generate(req: GenerateRequest):
    request_id = str(uuid.uuid4())
    logging.info(f"[{request_id}] Generate")

    params = dict(
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
    )

    return StreamingResponse(
        stream_tokens(req.prompt, params),
        media_type="text/plain"
    )

@app.post("/chat")
def chat(req: ChatRequest):
    request_id = str(uuid.uuid4())
    logging.info(f"[{request_id}] Chat")

    prompt = build_chat_prompt(req.system, req.messages)

    params = dict(
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
    )

    return StreamingResponse(
        stream_tokens(prompt, params),
        media_type="text/plain"
    )