from llama_cpp import Llama
from deploy.config import MODEL_PATH, N_CTX, N_THREADS, N_GPU_LAYERS

# HR model (your fine-tuned one)
HR_MODEL_PATH = MODEL_PATH

# Base model (general)
BASE_MODEL_PATH = "/home/rishitakumar/trainee/Week8/quantized/base-model.gguf"

hr_llm = None
base_llm = None


def load_model(model_type="hr"):
    global hr_llm, base_llm

    if model_type == "hr":
        if hr_llm is None:
            print("Loading HR model...")
            hr_llm = Llama(
                model_path=HR_MODEL_PATH,
                n_ctx=N_CTX,
                n_threads=N_THREADS,
                n_gpu_layers=N_GPU_LAYERS,
                repetition_penalty=1.3,
                verbose=False
            )
        return hr_llm

    elif model_type == "base":
        if base_llm is None:
            print("Loading BASE model...")
            base_llm = Llama(
                model_path=BASE_MODEL_PATH,
                n_ctx=N_CTX,
                n_threads=N_THREADS,
                n_gpu_layers=N_GPU_LAYERS,
                repetition_penalty=1.1,
                verbose=False
            )
        return base_llm