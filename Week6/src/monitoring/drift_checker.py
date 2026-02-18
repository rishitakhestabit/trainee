import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Config
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # Week6 root

REFERENCE_CSV = os.getenv(
    "REFERENCE_DATA_PATH",
    str(BASE_DIR / "src/data/processed/final.csv")
)
PRED_LOG_PATH = os.getenv(
    "PREDICTION_LOG_PATH",
    str(BASE_DIR / "prediction_logs.csv")
)

OUT_DIR = Path(os.getenv("MONITORING_OUT_DIR", str(BASE_DIR / "src/monitoring")))
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_REPORT = OUT_DIR / "drift_report.json"

TARGET_COL = "churn"

# PSI thresholds (common rule of thumb)
PSI_OK = 0.1
PSI_WARN = 0.2

# Minimum production samples before we trust drift metrics
MIN_CURRENT_SAMPLES = int(os.getenv("MIN_CURRENT_SAMPLES", "100"))


# -----------------------------
# Helpers
# -----------------------------
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def safe_json_loads(x):
    try:
        return json.loads(x)
    except Exception:
        return None


def load_reference_df(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Reference dataset not found: {path}")

    df = pd.read_csv(path)
    df = clean_column_names(df)

    if TARGET_COL in df.columns:
        df = df.drop(columns=[TARGET_COL])

    return df


def load_current_df_from_logs(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prediction logs not found: {path}")

    logs = pd.read_csv(path)

    if "input_json" not in logs.columns:
        raise ValueError("prediction_logs.csv must contain column: input_json")

    records = [safe_json_loads(x) for x in logs["input_json"].astype(str).tolist()]
    records = [r for r in records if isinstance(r, dict)]

    if len(records) == 0:
        raise ValueError("No valid JSON inputs found in prediction_logs.csv")

    df = pd.DataFrame(records)
    df = clean_column_names(df)
    return df


def get_feature_lists(ref: pd.DataFrame, cur: pd.DataFrame) -> Tuple[List[str], List[str]]:
    common = [c for c in ref.columns if c in cur.columns]

    # split by dtype using reference types (baseline)
    cat_cols = ref[common].select_dtypes(include=["object", "category", "string"]).columns.tolist()
    num_cols = ref[common].select_dtypes(include=["number", "bool", "int64", "float64"]).columns.tolist()

    return num_cols, cat_cols


def psi_numeric(ref: pd.Series, cur: pd.Series, bins: int = 10) -> float:
    ref = pd.to_numeric(ref, errors="coerce").dropna()
    cur = pd.to_numeric(cur, errors="coerce").dropna()

    if len(ref) == 0 or len(cur) == 0:
        return float("nan")

    # Use reference quantile bins (stable)
    quantiles = np.linspace(0, 1, bins + 1)
    cut_points = np.unique(ref.quantile(quantiles).values)

    # If not enough unique cut points, fallback to equal-width
    if len(cut_points) < 3:
        cut_points = np.linspace(ref.min(), ref.max(), bins + 1)

    ref_counts, _ = np.histogram(ref, bins=cut_points)
    cur_counts, _ = np.histogram(cur, bins=cut_points)

    ref_dist = ref_counts / max(ref_counts.sum(), 1)
    cur_dist = cur_counts / max(cur_counts.sum(), 1)

    # avoid zeros
    eps = 1e-6
    ref_dist = np.clip(ref_dist, eps, 1)
    cur_dist = np.clip(cur_dist, eps, 1)

    return float(np.sum((cur_dist - ref_dist) * np.log(cur_dist / ref_dist)))


def psi_categorical(ref: pd.Series, cur: pd.Series) -> float:
    ref = ref.astype(str).fillna("MISSING")
    cur = cur.astype(str).fillna("MISSING")

    ref_counts = ref.value_counts(normalize=True)
    cur_counts = cur.value_counts(normalize=True)

    all_cats = sorted(set(ref_counts.index).union(set(cur_counts.index)))

    eps = 1e-6
    psi = 0.0
    for cat in all_cats:
        r = float(ref_counts.get(cat, 0.0))
        c = float(cur_counts.get(cat, 0.0))
        r = max(r, eps)
        c = max(c, eps)
        psi += (c - r) * np.log(c / r)

    return float(psi)


def psi_status(value: float) -> str:
    if np.isnan(value):
        return "unknown"
    if value < PSI_OK:
        return "ok"
    if value < PSI_WARN:
        return "warning"
    return "alert"


def write_report(report: Dict):
    with open(OUT_REPORT, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[OK] Drift report saved: {OUT_REPORT}")


# -----------------------------
# Main
# -----------------------------
def main():
    ref = load_reference_df(REFERENCE_CSV)
    cur = load_current_df_from_logs(PRED_LOG_PATH)

    # ✅ Guardrail: too few production samples => drift metrics will be misleading
    if len(cur) < MIN_CURRENT_SAMPLES:
        report = {
            "status": "insufficient_data",
            "message": f"Need at least {MIN_CURRENT_SAMPLES} prediction samples to evaluate drift reliably.",
            "reference_data_path": REFERENCE_CSV,
            "prediction_log_path": PRED_LOG_PATH,
            "n_reference_rows": int(len(ref)),
            "n_current_rows": int(len(cur)),
            "min_current_samples": MIN_CURRENT_SAMPLES,
            "next_step": "Send more /predict requests (or run a small load test) then re-run drift_checker.",
        }
        write_report(report)
        print("[INFO] Not enough production data for drift detection.")
        return

    num_cols, cat_cols = get_feature_lists(ref, cur)

    report: Dict = {
        "status": "ok",
        "reference_data_path": REFERENCE_CSV,
        "prediction_log_path": PRED_LOG_PATH,
        "n_reference_rows": int(len(ref)),
        "n_current_rows": int(len(cur)),
        "numeric_features_checked": num_cols,
        "categorical_features_checked": cat_cols,
        "psi_thresholds": {"ok_lt": PSI_OK, "warning_lt": PSI_WARN},
        "feature_psi": {},
        "summary": {"ok": 0, "warning": 0, "alert": 0, "unknown": 0},
        "alerts": [],
    }

    # Numeric PSI
    for col in num_cols:
        val = psi_numeric(ref[col], cur[col])
        status = psi_status(val)
        report["feature_psi"][col] = {"psi": val, "type": "numeric", "status": status}
        report["summary"][status] += 1
        if status == "alert":
            report["alerts"].append(col)

    # Categorical PSI
    for col in cat_cols:
        val = psi_categorical(ref[col], cur[col])
        status = psi_status(val)
        report["feature_psi"][col] = {"psi": val, "type": "categorical", "status": status}
        report["summary"][status] += 1
        if status == "alert":
            report["alerts"].append(col)

    # overall status
    if report["summary"]["alert"] > 0:
        report["status"] = "alert"
    elif report["summary"]["warning"] > 0:
        report["status"] = "warning"
    else:
        report["status"] = "ok"

    write_report(report)
    print("[SUMMARY]", report["summary"])
    if report["status"] != "ok":
        print("[ALERT FEATURES]", report["alerts"][:20], "..." if len(report["alerts"]) > 20 else "")


if __name__ == "__main__":
    main()
