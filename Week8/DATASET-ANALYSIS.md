
# Instruction Tuning Dataset – HR Domain

![Day-1](ss/day1ss/result.png)

![Token Length Distribution](analysis/token_length_distribution.png)

## Dataset Overview
- **Domain:** Human Resources (HR)
- **Dataset Type:** Instruction‑tuning dataset for LLM fine‑tuning
- **Format:** JSONL (Instruction → Input → Output)
- **Raw Dataset File:** `data/raw.jsonl`

### Dataset Size
- **Total samples:** 568
- **Train split:** 90%
- **Validation split:** 10%

Final dataset files:

```
data/
 ├── raw.jsonl
 ├── train.jsonl
 └── val.jsonl
```

---

# Instruction Dataset Structure

Each training sample follows the standard **instruction tuning format**:

```json
{
  "instruction": "...",
  "input": "...",
  "output": "..."
}
```

---

# Dataset Domain

The dataset focuses on the **Human Resources (HR)** domain and contains questions and explanations related to:

- Employee onboarding
- Workplace policies
- Compensation and benefits
- Performance management
- HR analytics
- Recruitment and talent acquisition
- Workplace diversity and inclusion
- Employee engagement
- Labor law concepts
- Organizational development

The goal is to train the model to produce **clear HR explanations and policy descriptions**.

---

# Data Cleaning Pipeline

Dataset preprocessing is implemented in:

```
utils/data_cleaner.py
```

The script performs several cleaning operations.

### Cleaning Steps

**1. Invalid JSON Removal**
- Skips malformed JSON lines
- Removes empty rows

**2. Field Validation**
Ensures each record contains:

- `instruction`
- `output`

Invalid records are removed.

**3. Text Normalization**
- Trims whitespace
- Standardizes formatting

These steps ensure the dataset is **consistent and training‑ready**.

---

# Token Length Analysis

Token length analysis was performed using the tokenizer:

```
TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

For each sample:

```
instruction + input + output
```

was tokenized and analyzed.

---

# Token Length Filtering

Filtering thresholds used:

- **Minimum tokens:** 10  
- **Maximum tokens:** 512

This ensures samples are:

- Not too short
- Not excessively long

This improves **training stability and GPU efficiency**.

---

# Token Length Distribution

The distribution of token lengths was visualized using a histogram.

Saved at:

```
analysis/token_length_distribution.png
```

The histogram confirms:

- Most samples fall within a compact token range
- There are no extreme outliers
- The dataset is balanced for fine‑tuning

---

# Train / Validation Split

The dataset was split using:

```
sklearn.model_selection.train_test_split
```

Split configuration:

| Split | Percentage |
|------|------------|
| Train | 90% |
| Validation | 10% |

This allows the model to:

- Train on the majority of the dataset
- Evaluate performance on unseen validation data

---

