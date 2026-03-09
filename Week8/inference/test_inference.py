
import time
import torch
import pandas as pd
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer, util


# =========================
# MODEL PATHS
# =========================

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
FT_MODEL = "/content/drive/MyDrive/merged_model"
GGUF_MODEL = "/content/drive/MyDrive/model-q8_0.gguf"

RESULTS_PATH = "./benchmarks/results.csv"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# =========================
# TEST PROMPTS
# =========================

PROMPTS = [
    "What are the best practices for employee onboarding?",
    "How should performance reviews be conducted?",
    "What are strategies to improve employee engagement?"
]

GROUND_TRUTH = [
    "Effective employee onboarding includes clear communication of expectations, structured training, mentorship, and regular feedback to integrate employees successfully.",
    "Performance reviews should combine feedback, goal evaluation, constructive discussion, and development planning.",
    "Employee engagement can be improved through recognition, growth opportunities, open communication, and work-life balance."
]


# =========================
# EMBEDDING MODEL
# =========================

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")


# =========================
# VRAM CHECK
# =========================

def get_vram():
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated() / 1024**2
    return 0


# =========================
# ACCURACY FUNCTION
# =========================

def accuracy(preds, refs):

    p_emb = embedder.encode(preds, convert_to_tensor=True)
    r_emb = embedder.encode(refs, convert_to_tensor=True)

    sims = util.cos_sim(p_emb, r_emb)

    return sims.diag().mean().item()


# =========================
# HF MODEL BENCHMARK
# =========================

def benchmark_hf(model_path, label):

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")

    outputs = []

    start = time.time()

    for prompt in PROMPTS:

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        out = model.generate(**inputs, max_new_tokens=128)

        text = tokenizer.decode(out[0], skip_special_tokens=True)

        outputs.append(text)

    end = time.time()

    tokens = sum(len(tokenizer.encode(o)) for o in outputs)

    tps = tokens / (end - start)

    acc = accuracy(outputs, GROUND_TRUTH)

    return {
        "Model": label,
        "Tokens/sec": round(tps,2),
        "Latency(s)": round(end-start,2),
        "VRAM(MB)": round(get_vram(),2),
        "Accuracy": round(acc,3)
    }


# =========================
# GGUF BENCHMARK
# =========================

def benchmark_gguf(label):

    llm = Llama(
        model_path=GGUF_MODEL,
        n_ctx=2048,
        n_threads=8,
        verbose=False
    )

    outputs = []

    start = time.time()

    for prompt in PROMPTS:

        out = llm(prompt, max_tokens=128)

        outputs.append(out["choices"][0]["text"])

    end = time.time()

    tokens = sum(len(o.split()) for o in outputs)

    tps = tokens / (end - start)

    acc = accuracy(outputs, GROUND_TRUTH)

    return {
        "Model": label,
        "Tokens/sec": round(tps,2),
        "Latency(s)": round(end-start,2),
        "VRAM(MB)": round(get_vram(),2),
        "Accuracy": round(acc,3)
    }


# =========================
# STREAMING OUTPUT DEMO
# =========================

def streaming_demo():

    print("\nStreaming Output Demo\n")

    llm = Llama(model_path=GGUF_MODEL, n_ctx=2048)

    prompt = "Explain the role of HR in improving employee engagement."

    for chunk in llm(prompt, max_tokens=120, stream=True):

        print(chunk["choices"][0]["text"], end="", flush=True)

    print("\n")


# =========================
# BATCH INFERENCE DEMO
# =========================

def batch_inference(model_path):

    print("\nBatch Inference Demo\n")

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")

    prompts = [
        "What is employee onboarding?",
        "Why are performance reviews important?",
        "How can HR improve employee engagement?"
    ]

    inputs = tokenizer(prompts, return_tensors="pt", padding=True).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=120)

    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    for i, out in enumerate(decoded):

        print(f"\nPrompt {i+1}:\n{out}")


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    os.makedirs("benchmarks", exist_ok=True)

    results = []

    for i in range(3):

        results.append(benchmark_gguf("GGUF Q8 llama.cpp"))

        results.append(benchmark_hf(BASE_MODEL, "Base Model"))

        results.append(benchmark_hf(FT_MODEL, "Fine-tuned"))

    df = pd.DataFrame(results)

    df.to_csv(RESULTS_PATH, index=False)

    print("\nBenchmark Results\n")

    print(df)


    # Run streaming demo
    streaming_demo()


    # Run batch inference
    batch_inference(FT_MODEL)
