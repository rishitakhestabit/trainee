# pipelines/data_pipeline.py

import os
from pathlib import Path
import pandas as pd
import numpy as np


# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_PATH = PROJECT_ROOT / "src/data/raw/CustomerChurn.csv"
PROCESSED_PATH = PROJECT_ROOT / "src/data/processed/final.csv"



# -----------------------------
# Utils
# -----------------------------
def log(msg: str):
    print(f"[DATA_PIPELINE] {msg}")


# -----------------------------
# Step 1: Load
# -----------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {path}")

    df = pd.read_csv(path)
    log(f" Data loaded | shape={df.shape}")
    return df


# -----------------------------
# Step 2: Cleaning
# -----------------------------
def fix_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    """
    TotalCharges is often stored as string because it contains blank values " ".
    Convert to numeric safely. blanks -> NaN.
    """
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = df["TotalCharges"].astype(str).str.strip()
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    For Telco churn:
    - TotalCharges missing happens when tenure = 0 (no charges yet) => fill with 0.
    """
    before = df.isna().sum().sum()

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = df["TotalCharges"].fillna(0)

    # If any other missing values exist, fill with mode (categorical) / median (numeric)
    # (Usually there aren't in this dataset, but this makes pipeline robust.)
    for col in df.columns:
        if df[col].isna().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

    after = df.isna().sum().sum()
    log(f"Missing values handled | before={before}, after={after}")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    log(f"Duplicates removed | before={before}, after={after}, removed={before-after}")
    return df


def clip_outliers_iqr(df: pd.DataFrame, numeric_cols=None) -> pd.DataFrame:
    """
    Outlier handling using IQR clipping (not removal).
    Safer for churn dataset.
    """
    if numeric_cols is None:
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    for col in numeric_cols:
        # skip binary 0/1 columns (like SeniorCitizen)
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) <= 2:
            continue

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        if IQR == 0:
            continue

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        df[col] = df[col].clip(lower=lower, upper=upper)

    log(f" Outliers clipped using IQR (numeric cols checked={len(numeric_cols)})")
    return df


def drop_useless_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    customerID is an identifier (not predictive). Keep it only if you want tracking.
    For ML training, usually remove it.
    """
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])
        log("Dropped column: customerID (identifier)")
    return df


# -----------------------------
# Step 3: Save
# -----------------------------
def save_data(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    log(f"Cleaned dataset saved to: {path} | shape={df.shape}")


# -----------------------------
# Full pipeline runner
# -----------------------------
def run_pipeline():
    log(" Starting Day-1 Data Pipeline...")

    df = load_data(RAW_PATH)

    # Cleaning steps
    df = fix_total_charges(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = clip_outliers_iqr(df, numeric_cols=["tenure", "MonthlyCharges", "TotalCharges"])
    df = drop_useless_columns(df)

    # Final checks
    if df.isna().sum().sum() != 0:
        log(" Warning: Still missing values exist after cleaning.")
    else:
        log(" Final missing values check passed (no NaNs).")

    save_data(df, PROCESSED_PATH)

    log(" Day-1 pipeline completed successfully!")


if __name__ == "__main__":
    run_pipeline()
