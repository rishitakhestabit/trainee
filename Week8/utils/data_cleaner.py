import json
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

RAW_PATH = "data/raw.jsonl"
TRAIN_PATH = "data/train.jsonl"
VAL_PATH = "data/val.jsonl"
ANALYSIS_DIR = "analysis"
TOKEN_PLOT_PATH = os.path.join(ANALYSIS_DIR, "token_length_distribution.png")

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
MAX_TOKENS = 1200

os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(TRAIN_PATH), exist_ok=True)


def load_and_clean(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line {i}: {e}")
                continue

            # Validate required fields
            if not item.get("instruction") or not item.get("output"):
                continue

            # Clean whitespace
            item["instruction"] = item["instruction"].strip()
            item["input"] = item.get("input", "").strip()
            item["output"] = item["output"].strip()

            data.append(item)
    return data


def save_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def analyze_token_lengths(file_path, tokenizer, plot_path):
    lengths = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            text = f"{obj['instruction']} {obj['input']} {obj['output']}"
            tokens = tokenizer(text, truncation=False)["input_ids"]
            lengths.append(len(tokens))

    # Plot distribution
    plt.figure(figsize=(10, 6))
    plt.hist(lengths, bins=50, color="skyblue", edgecolor="black")
    plt.xlabel("Token Length")
    plt.ylabel("Frequency")
    plt.title("Token Length Distribution")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()

    print(f"Saved plot to: {plot_path}")
    print(f"Total samples analyzed: {len(lengths)}")
    print(f"Average token length: {sum(lengths)/len(lengths):.2f}")
    print(f"Max token length: {max(lengths)}")
    print(f"Min token length: {min(lengths)}")


def main():
    print("Loading and cleaning dataset...")
    data = load_and_clean(RAW_PATH)
    print(f"Total clean samples: {len(data)}")

    train_data, val_data = train_test_split(data, test_size=0.1, random_state=42)
    save_jsonl(train_data, TRAIN_PATH)
    save_jsonl(val_data, VAL_PATH)
    print(f"Train samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")

    print(f"Loading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("Analyzing token lengths...")
    analyze_token_lengths(TRAIN_PATH, tokenizer, TOKEN_PLOT_PATH)
    print("Data cleaning and analysis complete!")


if __name__ == "__main__":
    main()
