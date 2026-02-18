import os
import json
from pathlib import Path

import pandas as pd


# -----------------------------
# Config
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

LOG_PATH = os.getenv("PREDICTION_LOG_PATH", str(BASE_DIR / "prediction_logs.csv"))
OUT_DIR = Path(os.getenv("MONITORING_OUT_DIR", str(BASE_DIR / "src/monitoring")))
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_REPORT = Path(os.getenv("ACCURACY_REPORT_PATH", str(OUT_DIR / "accuracy_report.json")))

ROLLING_WINDOW = int(os.getenv("ACCURACY_ROLLING_WINDOW", "50"))


def main():
    if not os.path.exists(LOG_PATH):
        raise FileNotFoundError(f"prediction_logs.csv not found at: {LOG_PATH}")

    df = pd.read_csv(LOG_PATH)

    required = {"timestamp", "prediction", "true_label", "is_correct"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing columns in prediction_logs.csv: {missing}. "
            f"Update api.py logging to include true_label/is_correct."
        )

    # labeled rows only
    labeled = df[df["true_label"].astype(str).str.strip() != ""].copy()

    report = {
        "log_path": LOG_PATH,
        "total_predictions": int(len(df)),
        "labeled_samples": int(len(labeled)),
        "rolling_window": ROLLING_WINDOW,
        "overall_accuracy": None,
        "rolling_accuracy": None,
        "daily_accuracy": [],
        "note": None,
    }

    if len(labeled) == 0:
        report["note"] = (
            "No ground truth labels yet. Use POST /feedback to attach true labels, "
            "then re-run this script."
        )
        with open(OUT_REPORT, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[OK] Saved: {OUT_REPORT}")
        print("[INFO]", report["note"])
        return

    labeled["is_correct"] = labeled["is_correct"].astype(int)
    report["overall_accuracy"] = float(labeled["is_correct"].mean())

    # Rolling accuracy (last N labeled predictions)
    tail = labeled.tail(ROLLING_WINDOW)
    report["rolling_accuracy"] = float(tail["is_correct"].mean())

    # Daily accuracy trend (optional)
    labeled["timestamp"] = pd.to_datetime(labeled["timestamp"], errors="coerce")
    labeled = labeled.dropna(subset=["timestamp"])
    if len(labeled) > 0:
        labeled["date"] = labeled["timestamp"].dt.date.astype(str)
        daily = labeled.groupby("date")["is_correct"].mean().reset_index()
        report["daily_accuracy"] = daily.to_dict(orient="records")

    with open(OUT_REPORT, "w") as f:
        json.dump(report, f, indent=2)

    print(f"[OK] Saved: {OUT_REPORT}")
    print(
        "[SUMMARY] labeled:", report["labeled_samples"],
        "| overall_acc:", report["overall_accuracy"],
        "| rolling_acc:", report["rolling_accuracy"]
    )


if __name__ == "__main__":
    main()
