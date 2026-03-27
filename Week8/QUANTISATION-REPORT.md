# QUANTISATION-REPORT.md

## Week 8 — Day 3

LLM Quantisation and Optimised Inference

---

# Model Used

Base Model: TinyLlama-1.1B-Chat-v1.0  
Fine-tuning Method: LoRA (HR Instruction Dataset)

Frameworks and libraries used:

- transformers  
- bitsandbytes  
- PEFT  
- llama.cpp  
- llama-cpp-python  

The LoRA adapter trained on the HR dataset was merged with the base model before quantisation.

---

# 1. Objective

The objective of this experiment was to reduce the memory footprint and inference cost of the fine-tuned LLM while maintaining acceptable output quality.

Quantisation converts model weights from high precision formats (such as FP16) to lower precision formats such as INT8 and INT4.

This enables:

- Lower memory usage  
- Faster inference  
- Ability to run models on CPU or low-VRAM GPUs  
- Easier deployment on edge systems  

---

# 2. Quantisation Techniques Implemented

## FP16 (Baseline)

- Original merged TinyLlama model  
- Full precision weights  
- Highest memory usage  
- Best output fidelity  

## INT8 Quantisation

- Implemented using BitsAndBytes  
- 8-bit weight representation  
- Approximately 50% memory reduction  
- Minimal loss in output quality  

## INT4 Quantisation

- Implemented using 4-bit NF4 quantisation  
- Much smaller model size  
- Suitable for low-resource environments  

## GGUF Format (llama.cpp)

The merged model was converted into GGUF format using llama.cpp.

GGUF is designed for:

- Efficient CPU inference  
- Reduced memory footprint  
- Compatibility with llama.cpp runtime  

Generated variants:

- q8_0  
- q4_0  

---

# 3. Quantisation Pipeline

HR Dataset  
→ LoRA Fine-Tuning  
→ Adapter Weights  
→ Merge with Base Model  
→ Quantisation (INT8, INT4)  
→ GGUF Conversion (q8_0, q4_0)  

---

# 4. Model Size Comparison

| Format | Size (MB) |
|--------|----------|
| FP16 | 2099 |
| INT8 | 1115 |
| INT4 | 712 |
| GGUF q8_0 | 1100 |
| GGUF q4_0 | 608 |

Quantisation significantly reduces model size compared to the FP16 baseline.

![Day-3 Comparison](ss/day3ss/comp.png)

---

# 5. Inference Performance Comparison

| Format | Speed | Memory | Quality |
|--------|------|--------|--------|
| FP16 | Moderate | High | Highest |
| INT8 | Faster | Medium | Very close to FP16 |
| INT4 | Faster | Low | Slight drop |
| GGUF q8_0 | Fast (CPU) | Low | Good |
| GGUF q4_0 | Very fast (CPU) | Very Low | Slight drop |

---

# 6. Quality Evaluation

Evaluation was performed using HR-related prompts.

Example prompt:

What are the best practices for employee onboarding in an organization?

Example reasoning prompt:

Explain how HR strategies can improve employee engagement and retention.

![Day-3 Output](ss/day3ss/output.png)

---

# 7. Key Insights

- Quantisation reduces model size by up to 70% compared to FP16  
- INT8 provides a strong balance between performance and quality  
- INT4 enables deployment on very low-resource systems  
- GGUF models are ideal for CPU-based inference environments  
- There is a trade-off between model size, speed, and output quality  

---

# 8. Conclusion

Quantisation is a critical step in making LLMs practical for real-world deployment.

While FP16 models provide the highest quality, INT8 and INT4 significantly reduce memory requirements with minimal quality loss.

GGUF quantisation enables efficient local deployment on CPU systems, making LLM applications accessible without requiring high-end hardware.

The choice of quantisation technique depends on the deployment constraints and performance requirements.