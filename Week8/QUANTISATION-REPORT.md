# QUANTISATION-REPORT.md

## Week 8 --- Day 3

**LLM Quantisation and Optimised Inference**



# Model Used

Base Model: **TinyLlama-1.1B-Chat-v1.0**\
Fine‑tuning Method: **LoRA (HR Instruction Dataset)**

Frameworks and libraries used:

-   transformers
-   bitsandbytes
-   PEFT
-   llama.cpp
-   llama-cpp-python

The LoRA adapter trained on the **HR dataset** was merged with the base
model before performing quantisation.



# 1. Objective

The objective of this experiment was to reduce the **memory footprint
and inference cost** of the fine‑tuned LLM while maintaining acceptable
output quality.

Quantisation converts model weights from high precision formats (such as
FP16) to lower precision formats such as **INT8 and INT4**.

This enables:

-   Lower memory usage
-   Faster inference
-   Ability to run models on **CPU or low‑VRAM GPUs**
-   Easier deployment on edge systems


# 2. Quantisation Techniques Implemented

## FP16 (Baseline)

-   Original merged TinyLlama model
-   Full precision weights
-   Highest memory usage
-   Best output fidelity


## INT8 Quantisation

-   Implemented using **BitsAndBytes**
-   8‑bit weight representation
-   Approximately **50% memory reduction**
-   Minimal loss in output quality



## INT4 Quantisation

-   Implemented using **4‑bit NF4 quantisation**
-   Much smaller model size
-   Allows inference on very limited hardware


## GGUF Format (llama.cpp)

The merged model was also converted into **GGUF format** using
**llama.cpp**.

GGUF is designed for:

-   Efficient **CPU inference**
-   Reduced memory footprint
-   Compatibility with **llama.cpp runtime**

Two GGUF variants were generated:

-   **q8_0**
-   **q4_0**


# 3. Quantisation Pipeline

HR Instruction Dataset\
\
LoRA Fine‑Tuning\
\
Adapter Weights\
\
Merge LoRA with Base Model\
\
Quantisation

-   INT8 (BitsAndBytes)\
-   INT4 (NF4 quantisation)\
-   GGUF conversion using llama.cpp\
-   GGUF q8_0 quantisation\
-   GGUF q4_0 quantisation



# 4. Model Size Comparison

  Format      Size (MB)
  ----------- -------------
  FP16        **2099 MB**
  INT8        **1115 MB**
  INT4        **712 MB**
  GGUF q8_0   **1100 MB**
  GGUF q4_0   **608 MB**

The results show that quantisation significantly reduces model size
compared to the FP16 baseline.

![Day-3 Comparison](ss/day3ss/comp.png)



# 5. Inference Speed Benchmark

  Format      Size (MB)   Inference Speed           Quality
  ----------- ----------- ------------------------- -----------------------
  FP16        2099        Moderate                  Highest
  INT8        1115        Faster                    Very close to FP16
  INT4        712         Faster                    Slight precision loss
  GGUF q8_0   1100        Fast CPU inference        Good
  GGUF q4_0   608         Very fast CPU inference   Slight quality drop

INT4 and GGUF models significantly improve inference efficiency while
reducing memory usage.



# 6. Quality Evaluation

HR prompts were used to evaluate the quantised models.

Example prompt:

> What are the best practices for employee onboarding in an
> organization?

Example reasoning prompt:

> Explain how HR strategies can improve employee engagement and
> retention.

![Day-3 Output](ss/day3ss/output.png)


