# src/features/build_features.py

import pandas as pd
import numpy as np

DATA_PATH = "src/data/processed/final.csv"
TARGET_COL = "churn"


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[^\w]+", "_", regex=True)
          .str.strip("_")
    )
    return df


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = clean_column_names(df)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Day-2 Feature Engineering ONLY (row-wise).
    No splitting, no scaling, no encoding fitted here.
    """
    df = df.copy()

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found. Found columns: {df.columns.tolist()}")

    # Map churn to 0/1 if it's Yes/No
    df[TARGET_COL] = df[TARGET_COL].astype(str).str.strip()
    if set(df[TARGET_COL].unique()) <= {"Yes", "No"}:
        df[TARGET_COL] = df[TARGET_COL].map({"Yes": 1, "No": 0})

    if df[TARGET_COL].isna().any():
        raise ValueError("Target mapping failed. Ensure churn values are Yes/No OR already numeric 0/1.")

    # totalcharges numeric safe
    if "totalcharges" in df.columns:
        df["totalcharges"] = pd.to_numeric(df["totalcharges"], errors="coerce").fillna(0)

    # 1) tenure_years + tenure_bucket
    if "tenure" in df.columns:
        df["tenure_years"] = df["tenure"] / 12
        df["tenure_bucket"] = pd.cut(
            df["tenure"],
            bins=[-1, 12, 24, 48, 72, 10_000],
            labels=["0_1y", "1_2y", "2_4y", "4_6y", "6y_plus"]
        )

    # 2) avg_monthly_charge
    if all(col in df.columns for col in ["totalcharges", "tenure"]):
        df["avg_monthly_charge"] = df["totalcharges"] / (df["tenure"] + 1)

    # 3) long-term contract
    if "contract" in df.columns:
        df["is_long_term_contract"] = df["contract"].isin(["One year", "Two year"]).astype(int)

    # 4) autopay
    if "paymentmethod" in df.columns:
        df["is_autopay"] = df["paymentmethod"].str.contains("automatic", case=False, na=False).astype(int)

    # 5) has internet
    if "internetservice" in df.columns:
        df["has_internet"] = (df["internetservice"].str.lower() != "no").astype(int)

    # 6) counts
    security_cols = ["onlinesecurity", "onlinebackup", "deviceprotection", "techsupport"]
    sec_exist = [c for c in security_cols if c in df.columns]
    if sec_exist:
        df["security_services_count"] = df[sec_exist].apply(lambda x: (x == "Yes").sum(), axis=1)

    ent_cols = ["streamingtv", "streamingmovies"]
    ent_exist = [c for c in ent_cols if c in df.columns]
    if ent_exist:
        df["entertainment_services_count"] = df[ent_exist].apply(lambda x: (x == "Yes").sum(), axis=1)

    service_cols = [
        "phoneservice", "multiplelines", "onlinesecurity", "onlinebackup",
        "deviceprotection", "techsupport", "streamingtv", "streamingmovies"
    ]
    svc_exist = [c for c in service_cols if c in df.columns]
    if svc_exist:
        df["total_services"] = df[svc_exist].apply(lambda x: (x == "Yes").sum(), axis=1)

    # 7) ratio
    if all(col in df.columns for col in ["totalcharges", "monthlycharges"]):
        df["total_to_monthly_ratio"] = df["totalcharges"] / (df["monthlycharges"] + 1e-6)

    return df
