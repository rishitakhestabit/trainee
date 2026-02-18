import pandas as pd

from src.features.feature_engineering import clean_column_names

DATA_PATH = "src/data/processed/final.csv"
TARGET_COL = "churn"


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = clean_column_names(df)
    return df


def prepare_target(df: pd.DataFrame, target_col: str = TARGET_COL) -> pd.Series:
    """
    Converts churn to 0/1 safely.
    Keeps target logic separate from feature engineering.
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Found columns: {df.columns.tolist()}")

    y = df[target_col].astype(str).str.strip()

    # Map Yes/No to 1/0 if present
    if set(y.unique()) <= {"Yes", "No"}:
        y = y.map({"Yes": 1, "No": 0})

    # If already numeric-like, try converting
    y = pd.to_numeric(y, errors="coerce")

    if y.isna().any():
        raise ValueError("Target mapping failed. Ensure churn values are Yes/No OR already numeric 0/1.")

    return y.astype(int)
