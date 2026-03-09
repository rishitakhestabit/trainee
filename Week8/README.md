
# README.md

# HR LLM — TinyLlama Fine-Tuning and Deployment

This project demonstrates the complete workflow of building and deploying a domain-specific Large Language Model using TinyLlama.

The model was trained on a Human Resources (HR) instruction dataset and optimized for efficient inference and deployment.

The project covers:

Day 1 — Dataset preparation and analysis  
Day 2 — Parameter-efficient fine-tuning using QLoRA  
Day 3 — Model quantization and optimization  
Day 4 — Inference benchmarking and evaluation  
Day 5 — Local LLM API deployment with FastAPI and Streamlit

---

# Project Structure

```
week8/
│
├── adapters/
│
├── analysis/
│   └── token_length_distribution.png
│
├── benchmarks/
│   └── results.csv
│
├── data/
│   ├── raw.jsonl
│   ├── train.jsonl
│   └── val.jsonl
│
├── deploy/
│   ├── app.py
│   ├── config.py
│   ├── model_loader.py
│   └── streamlit.py
│
├── inference/
│   ├── inference.ipynb
│   └── test_inference.py
│
├── notebooks/
│   ├── lora_train.ipynb
│   └── quantized.ipynb
│
├── quantized/
│
├── utils/
│   ├── data_cleaner.py
│   └── generate_data.py
│
├── DATASET-ANALYSIS.md
├── TRAINING-REPORT.md
├── QUANTISATION-REPORT.md
├── BENCHMARK-REPORT.md
├── FINAL-REPORT.md
└── README.md
```

---

# Day 1 — Dataset Preparation

An instruction-tuning dataset was prepared for the HR domain.

Topics included:

- employee onboarding
- performance management
- compensation and benefits
- HR analytics
- employee engagement
- recruitment and talent acquisition

Dataset format:

```
{
  "instruction": "...",
  "input": "...",
  "output": "..."
}
```

Dataset files:

```
data/raw.jsonl
data/train.jsonl
data/val.jsonl
```

Cleaning script:

```
utils/data_cleaner.py
```

Run data cleaning:

```bash
python utils/data_cleaner.py
```

Token distribution analysis:

```
analysis/token_length_distribution.png
```

---

# Day 2 — QLoRA Fine-Tuning

The base model used:

```
TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

Fine-tuning used **QLoRA** to reduce GPU memory usage.

Training configuration:

- LoRA rank = 16
- learning rate = 2e-4
- batch size = 4
- epochs = 3
- optimizer = paged_adamw_8bit

Training notebook:

```
notebooks/lora_train.ipynb
```

Run training:

```bash
jupyter notebook notebooks/lora_train.ipynb
```

Trained adapter weights are saved in:

```
adapters/
```

---

# Day 3 — Model Quantization

The merged model was quantized to reduce memory usage and enable CPU inference.

Quantization methods used:

FP16 (baseline)  
INT8 quantization using BitsAndBytes  
INT4 NF4 quantization  
GGUF conversion using llama.cpp

Generated formats:

```
INT8 model
INT4 model
GGUF q8_0
GGUF q4_0
```

Quantization notebook:

```
notebooks/quantized.ipynb
```

Run quantization:

```bash
jupyter notebook notebooks/quantized.ipynb
```

Model size comparison:

| Format | Size |
|------|------|
| FP16 | ~2099 MB |
| INT8 | ~1115 MB |
| INT4 | ~712 MB |
| GGUF q8_0 | ~1100 MB |
| GGUF q4_0 | ~608 MB |

---

# Day 4 — Inference Optimization and Benchmarking

Inference performance was evaluated for:

- Base model
- Fine-tuned model
- Quantized GGUF model

Metrics measured:

- Tokens per second
- Latency
- VRAM usage
- Semantic accuracy

Benchmark script:

```
inference/test_inference.py
```

Run benchmarking:

```bash
python inference/test_inference.py
```

Results saved in:

```
benchmarks/results.csv
```

---

# Day 5 — Local LLM API Deployment

The quantized model was deployed as a local API using **FastAPI**.

Deployment files:

```
deploy/app.py
deploy/config.py
deploy/model_loader.py
deploy/streamlit.py
```

API endpoints:

POST `/generate`  
Generate text from a prompt.

POST `/chat`  
Chat interface using system and user messages.

---

# Running the API Server

Start FastAPI:

```bash
uvicorn deploy.app:app --host 0.0.0.0 --port 8000 --reload
```

Open API documentation:

```
http://localhost:8000/docs
```

---

# Running the Streamlit Interface

```bash
streamlit run deploy/streamlit.py
```

Open:

```
http://localhost:8501
```

---

# Testing API using CURL

Example:

```bash
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{
"system": "You are an HR assistant",
"messages": [{"role": "user", "content": "What is employee onboarding?"}],
"temperature": 0.7,
"top_p": 0.9,
"top_k": 40
}'
```

---

# Results

The project successfully demonstrates:

- Instruction dataset creation
- Parameter-efficient fine-tuning
- Model quantization
- Inference benchmarking
- Local API deployment

The deployed system can be extended for:

- Retrieval Augmented Generation (RAG)
- AI assistants
- enterprise HR chatbots
