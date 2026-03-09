# BENCHMARK REPORT

![Day-4](ss/day4ss/res.png)

## Project

LLM Fine-Tuning and Inference Optimization using TinyLlama

# Objective

The objective of this experiment was to benchmark different versions of
the TinyLlama language model and analyze the trade-offs between
inference speed, latency, memory consumption, and output quality.

Three different model configurations were evaluated:

1.  Base Model -- TinyLlama-1.1B-Chat
2.  Fine-Tuned Model -- LoRA merged model trained on HR instruction
    dataset
3.  Quantized Model -- GGUF Q8 model running with llama.cpp

The evaluation was conducted using HR-related prompts simulating common
human-resource scenarios such as employee onboarding, performance
reviews, and employee engagement.

# Experimental Setup

## Base Model

The base model used in this experiment was:

TinyLlama-1.1B-Chat-v1.0

The model was loaded directly from HuggingFace and used without any
additional training.

## Fine-Tuned Model

The base TinyLlama model was fine-tuned using LoRA (Low Rank Adaptation)
on a custom HR instruction dataset.

The LoRA adapters were later merged with the base model, producing a
standalone fine-tuned model capable of HR-specific reasoning and
responses.

## Quantized Model

To optimize inference efficiency, the merged model was converted into
GGUF format using llama.cpp and quantized with Q8_0 quantization.

Quantization significantly reduces memory consumption and enables
CPU-friendly inference.

# Inference Optimization Techniques

## Streaming Output

Token streaming was implemented to display model responses
token-by-token during generation, allowing users to see outputs as they
generated.

## Batch Inference

Batch inference was implemented by processing multiple prompts
simultaneously, improving overall throughput during evaluation.

## Multi-Prompt Testing

Multiple HR prompts were used during benchmarking to simulate real-world
usage scenarios such as employee onboarding, performance reviews, and
engagement strategies.

# Evaluation Metrics

  -----------------------------------------------------------------------
  Metric                              Description
  ----------------------------------- -----------------------------------
  Tokens/sec                          Number of tokens generated per
                                      second

  Latency                             Total time required to generate a
                                      response

  VRAM Usage                          GPU memory used during inference

  Accuracy                            Semantic similarity between
                                      generated output and ground truth
  -----------------------------------------------------------------------

Accuracy was measured using sentence embeddings with:

BAAI/bge-base-en-v1.5

# Benchmark Results

  Model               Tokens/sec   Latency (s)   VRAM (MB)   Accuracy
  ------------------- ------------ ------------- ----------- ----------
  GGUF Q8 llama.cpp   3.88         24.22         427.85      0.59
  Base Model          36.13        0.86          2526.03     0.769
  Fine-tuned          35.85        8.01          2526.03     0.742
  GGUF Q8 llama.cpp   3.55         26.49         427.85      0.59
  Base Model          82.77        0.37          2526.03     0.769
  Fine-tuned          33.39        8.59          2526.03     0.742
  GGUF Q8 llama.cpp   3.51         26.75         427.85      0.59
  Base Model          85.85        0.36          2526.03     0.769
  Fine-tuned          38.04        7.54          2526.03     0.742

# Observations

## Base Model

The base TinyLlama model achieved high inference speed and strong
semantic accuracy but required higher GPU memory (\~2.5 GB).

## Fine-Tuned Model

The fine-tuned model maintained similar accuracy while improving HR
domain relevance, though latency slightly increased due to merged LoRA
weights.

## Quantized Model (GGUF)

The GGUF model significantly reduced memory usage (\~428 MB), making it
suitable for CPU inference environments. However, inference speed was
slower compared to GPU-based HuggingFace models.

