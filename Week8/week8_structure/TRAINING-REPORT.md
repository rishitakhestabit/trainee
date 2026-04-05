
# WEEK 8 — DAY 2 REPORT
## Parameter‑Efficient Fine‑Tuning (QLoRA)

---
![Train Loss](ss/day2ss/trainloss.png)

# 1. Objective

On Day 2, I fine‑tuned a **Large Language Model (LLM)** using **QLoRA (Quantized Low‑Rank Adaptation)** on the **Human Resources (HR) instruction dataset** prepared in Day 1.

The goal was to perform **memory‑efficient fine‑tuning** by training only a small number of parameters while keeping the base model frozen.

### Training requirements

- Use **QLoRA**
- Load model in **4‑bit precision**
- **LoRA rank (r) = 16**
- **Learning rate = 2e‑4**
- **Batch size = 4**
- **Epochs = 3**
- **Trainable parameters ≈ 1%**
- **Save adapter weights**

---

# 2. Files Created and Used

## 2.1 notebooks/lora_train.ipynb

This notebook implements the **QLoRA fine‑tuning pipeline**.

Inside the notebook the following steps were performed.

### 1. Installed required libraries

The following libraries were installed for training:

- torch
- transformers
- datasets
- peft
- accelerate
- bitsandbytes
- trl

These libraries support **LLM training, quantization, and parameter‑efficient fine‑tuning**.

---

### 2. Loaded the HR instruction dataset

The dataset prepared during **Day 1** was loaded.

Files used:

- `data/train.jsonl`
- `data/val.jsonl`

The dataset contains HR related instruction examples including:

- HR question answering
- HR reasoning tasks
- HR information extraction

---

### 3. Loaded the Base Model

The base model used:

```
TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

TinyLlama is a lightweight **1.1B parameter transformer model** suitable for efficient fine‑tuning.

---

### 4. Configured 4‑bit Quantization

The base model was loaded using **4‑bit quantization** through `BitsAndBytesConfig`.

Configuration used:

- `load_in_4bit = True`
- `bnb_4bit_quant_type = "nf4"`
- `bnb_4bit_use_double_quant = True`
- `bnb_4bit_compute_dtype = bfloat16`

This significantly reduces **GPU memory usage**.

---

### 5. Enabled Memory Optimization

To support efficient training the following optimizations were enabled:

- `prepare_model_for_kbit_training`
- **Gradient checkpointing**
- `paged_adamw_8bit` optimizer

These reduce memory consumption during training.

---

### 6. Configured LoRA

LoRA adapters were applied to the model with the following configuration:

- `r = 16`
- `lora_alpha = 32`
- `lora_dropout = 0.05`
- `target_modules = ["q_proj", "v_proj"]`

Only the LoRA layers were trained while the **original model weights remained frozen**.

---

### 7. Training Configuration

Training parameters:

- `per_device_train_batch_size = 4`
- `learning_rate = 2e-4`
- `num_train_epochs = 3`
- `lr_scheduler_type = cosine`
- `warmup_ratio = 0.05`
- mixed precision (`bf16`)

---

### 8. Trainer Used

Training was performed using:

```
SFTTrainer
```

from the **TRL library**, which is optimized for instruction fine‑tuning.

---

### 9. Trainable Parameter Verification

The following command was used:

```
model.print_trainable_parameters()
```

This confirmed that only **~0.7–1% of the total parameters were trainable**, as expected with LoRA.

---

### 10. Saved Adapter Weights

After training the LoRA adapter weights were saved using:

```
trainer.model.save_pretrained()
```

---

## 2.2 adapters/hr_adapter/

This directory stores the **trained LoRA adapter weights**.

Important files:

- `adapter_model.bin`
- `adapter_config.json`

These files contain **only the LoRA parameters**, not the full model.

The base TinyLlama model remains frozen.



