# BENCHMARK REPORT

![Day-4](ss/day4ss/res.png)

## Project

LLM Fine-Tuning and Inference Optimization using TinyLlama

---

# Objective

The objective of this experiment was to benchmark different versions of the TinyLlama language model and analyze trade-offs between inference speed, latency, memory consumption, and output quality.

Three configurations were evaluated:

1. Base Model — TinyLlama-1.1B-Chat  
2. Fine-Tuned Model — LoRA merged HR model  
3. Quantized Model — GGUF Q8 (llama.cpp)

---

# Experimental Setup

## Base Model
Loaded directly from HuggingFace without modification.

## Fine-Tuned Model
Fine-tuned using LoRA on HR dataset and merged into base model.

## Quantized Model
Converted to GGUF format and quantized (Q8_0) using llama.cpp for CPU inference.

---

# Inference Optimization Techniques

## Streaming Output
Token-level streaming for real-time response display.

## Batch Inference
Multiple prompts processed together to improve throughput.

## Multi-Prompt Testing
HR-specific prompts used to simulate real-world usage.

---

# Evaluation Metrics

| Metric | Description |
|-------|------------|
| Tokens/sec | Tokens generated per second |
| Latency | Total response generation time |
| VRAM | GPU memory usage |
| Accuracy | Semantic similarity with ground truth |

Accuracy computed using:
BAAI/bge-base-en-v1.5 embeddings

---

# Benchmark Results (Averaged)

| Model | Tokens/sec | Latency (s) | VRAM (MB) | Accuracy |
|------|-----------|------------|----------|---------|
| Base Model | ~68 | ~0.53 | ~2526 | 0.769 |
| Fine-tuned Model | ~35 | ~8.05 | ~2526 | 0.742 |
| GGUF Q8 (CPU) | ~3.65 | ~25.82 | ~428 | 0.59 |

---

# Observations

## Base Model
- Highest speed and lowest latency
- Best overall accuracy
- Requires high VRAM (~2.5 GB)

## Fine-Tuned Model
- Slight drop in accuracy but improved domain relevance
- Higher latency due to merged weights
- Same VRAM usage as base model

## Quantized Model (GGUF)
- Extremely low memory usage (~428 MB)
- Suitable for CPU inference
- Significantly slower performance
- Slight drop in output quality

---

# Trade-off Analysis

| Model | Strength | Weakness |
|------|---------|----------|
| Base | Speed, accuracy | High memory usage |
| Fine-tuned | Domain relevance | Higher latency |
| GGUF | Low memory, CPU support | Slow speed, lower accuracy |

---

# Key Insights

- Fine-tuning improves domain-specific responses without major accuracy loss
- Quantization enables deployment on low-resource systems
- There is a clear trade-off between speed, memory, and quality
- Model choice depends on deployment requirements (GPU vs CPU)

---

# Conclusion

The benchmarking results highlight that:

- The base model is best for high-performance GPU environments
- The fine-tuned model is optimal for domain-specific applications
- The GGUF quantized model is ideal for low-resource or CPU-based deployment

This demonstrates the importance of selecting the right model configuration based on real-world constraints such as hardware, latency requirements, and use case.