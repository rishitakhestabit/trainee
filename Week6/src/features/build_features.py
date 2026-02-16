# src/features/build_features.py

import json
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


DATA_PATH = "src/data/processed/final.csv"
TARGET_COL = "churn"   # in your raw file it might be "Churn" -> we'll handle it


# ----------------------------
# STEP 0: Column cleaning
# ----------------------------
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHAT: Convert column names to lowercase + snake_case.
    WHY: Avoid case-sensitive bugs + make code consistent.
    HOW: pandas string ops.
    """
    df = df.copy()
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[^\w]+", "_", regex=True)  # spaces/special -> _
          .str.strip("_")
    )
    return df


# ----------------------------
# STEP 1: Load dataset
# ----------------------------
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = clean_column_names(df)
    return df


# ----------------------------
# STEP 2: Feature Engineering (10+ meaningful)
# ----------------------------
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHAT: Create new features from existing columns.
    WHY: Helps model learn hidden patterns (tenure behavior, spending behavior, service usage).
    HOW: Derived numeric features + flags + buckets.
    """
    df = df.copy()

    # If churn values are Yes/No, convert to 1/0 (binary target)
    # This works after lowercasing columns
    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found. Found columns: {df.columns.tolist()}")

    df[TARGET_COL] = df[TARGET_COL].astype(str).str.strip()
    df[TARGET_COL] = df[TARGET_COL].map({"Yes": 1, "No": 0})

    # Safety check
    if df[TARGET_COL].isna().any():
        raise ValueError("Target mapping failed. Ensure churn values are Yes/No.")

    # Convert totalcharges to numeric safely (Telco dataset often has spaces)
    if "totalcharges" in df.columns:
        df["totalcharges"] = pd.to_numeric(df["totalcharges"], errors="coerce")
        df["totalcharges"] = df["totalcharges"].fillna(0)

    # -------- 10+ new features --------

    # 1) tenure in years
    if "tenure" in df.columns:
        df["tenure_years"] = df["tenure"] / 12

        # 2) tenure bucket (categorical)
        df["tenure_bucket"] = pd.cut(
            df["tenure"],
            bins=[-1, 12, 24, 48, 72, 10_000],
            labels=["0_1y", "1_2y", "2_4y", "4_6y", "6y_plus"]
        )

    # 3) average monthly charge (avoid divide by 0)
    if all(col in df.columns for col in ["totalcharges", "tenure"]):
        df["avg_monthly_charge"] = df["totalcharges"] / (df["tenure"] + 1)

    # 4) long-term contract flag
    if "contract" in df.columns:
        df["is_long_term_contract"] = df["contract"].isin(["One year", "Two year"]).astype(int)

    # 5) autopay flag
    if "paymentmethod" in df.columns:
        df["is_autopay"] = df["paymentmethod"].str.contains("automatic", case=False, na=False).astype(int)

    # 6) has internet
    if "internetservice" in df.columns:
        df["has_internet"] = (df["internetservice"].str.lower() != "no").astype(int)

    # 7) security services count
    security_cols = ["onlinesecurity", "onlinebackup", "deviceprotection", "techsupport"]
    existing_security = [c for c in security_cols if c in df.columns]
    if existing_security:
        df["security_services_count"] = df[existing_security].apply(lambda x: (x == "Yes").sum(), axis=1)

    # 8) entertainment services count
    entertainment_cols = ["streamingtv", "streamingmovies"]
    existing_ent = [c for c in entertainment_cols if c in df.columns]
    if existing_ent:
        df["entertainment_services_count"] = df[existing_ent].apply(lambda x: (x == "Yes").sum(), axis=1)

    # 9) total add-on services count (Yes count across all service columns)
    service_cols = [
        "phoneservice", "multiplelines", "onlinesecurity", "onlinebackup",
        "deviceprotection", "techsupport", "streamingtv", "streamingmovies"
    ]
    existing_services = [c for c in service_cols if c in df.columns]
    if existing_services:
        df["total_services"] = df[existing_services].apply(lambda x: (x == "Yes").sum(), axis=1)

    # 10) ratio: totalcharges vs monthlycharges
    if all(col in df.columns for col in ["totalcharges", "monthlycharges"]):
        df["total_to_monthly_ratio"] = df["totalcharges"] / (df["monthlycharges"] + 1e-6)

    return df


# ----------------------------
# STEP 3: Encoding (OneHot)
# ----------------------------
def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    WHAT: Convert categorical columns to numeric.
    WHY: Models can't learn from strings directly.
    HOW: pd.get_dummies (OneHot) with drop_first to avoid dummy trap.
    """
    df = df.copy()

    # object/category columns except target
    cat_cols = df.select_dtypes(include=["object", "category","string"]).columns.tolist()
    if TARGET_COL in cat_cols:
        cat_cols.remove(TARGET_COL)

    df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    return df_encoded


# ----------------------------
# STEP 4: Train/Test + Scaling
# ----------------------------
def split_and_scale(df: pd.DataFrame):
    """
    WHAT: Split into train/test and scale numeric range.
    WHY: Prevent leakage + improve training stability.
    HOW: train_test_split + StandardScaler.
    """
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, X.columns.tolist()


# ----------------------------
# STEP 5: Save feature list
# ----------------------------
def save_feature_list(feature_names):
    with open("src/features/feature_list.json", "w") as f:
        json.dump(feature_names, f, indent=2)


# ----------------------------
# MAIN
# ----------------------------
def main():
    df = load_data()
    df = engineer_features(df)
    df = encode_features(df)

    X_train, X_test, y_train, y_test, feature_names = split_and_scale(df)

    save_feature_list(feature_names)

    print("\n [DAY 2] Feature engineering pipeline complete")
    print(f"Target: {TARGET_COL}")
    print(f"Total features after encoding: {len(feature_names)}")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape : {X_test.shape}")
    print("Saved: src/features/feature_list.json\n")


if __name__ == "__main__":
    main()
