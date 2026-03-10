import pandas as pd
from scipy.stats import ks_2samp

from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

REFERENCE = BASE / "data/processed/X_train.csv"
LIVE = "prediction_logs.csv"

def check_drift():
    ref = pd.read_csv(REFERENCE)
    live = pd.read_csv(LIVE)

    common_cols = (
        set(ref.select_dtypes(include=["int64", "float64"]).columns)
        .intersection(
            set(live.select_dtypes(include=["int64", "float64"]).columns)
        )
    )

    report = {}

    for col in common_cols:
        stat, p = ks_2samp(
            ref[col].dropna(),
            live[col].dropna()
        )
        report[col] = "DRIFT" if p < 0.05 else "OK"

    return report

if __name__ == "__main__":
    print(check_drift())
