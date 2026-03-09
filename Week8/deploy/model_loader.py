from llama_cpp import Llama
from deploy.config import MODEL_PATH, N_CTX, N_THREADS, N_GPU_LAYERS


llm = None

def load_model():
    global llm
    if llm is None:
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            n_gpu_layers=N_GPU_LAYERS,
            repetition_penalty = 1.3,
            verbose=False
        )
    return llm