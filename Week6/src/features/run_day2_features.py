# src/features/run_day2_features.py

import json
import os
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from scipy.sparse import save_npz, issparse, csr_matrix

from src.features.build_features import load_data, engineer_features, TARGET_COL


# ----------------------------
# Paths (Day-2 outputs)
# ----------------------------
OUT_DIR = "src/data/processed"
X_TRAIN_PATH = os.path.join(OUT_DIR, "X_train.npz")
X_TEST_PATH  = os.path.join(OUT_DIR, "X_test.npz")
Y_TRAIN_PATH = os.path.join(OUT_DIR, "y_train.npy")
Y_TEST_PATH  = os.path.join(OUT_DIR, "y_test.npy")

FEATURE_LIST_PATH = "src/features/feature_list.json"
PREPROCESSOR_PATH = "src/features/preprocessor.joblib"

RANDOM_STATE = 40


# ----------------------------
# Preprocessor
# ----------------------------
def build_preprocessor(X_train):
    cat_cols = X_train.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    num_cols = X_train.select_dtypes(include=["number", "bool"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", StandardScaler(with_mean=False), num_cols),
        ],
        remainder="drop",
        sparse_threshold=0.3
    )
    return preprocessor


def get_feature_names(preprocessor, X_train):
    cat_cols = X_train.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    num_cols = X_train.select_dtypes(include=["number", "bool"]).columns.tolist()

    ohe = preprocessor.named_transformers_["cat"]
    cat_names = ohe.get_feature_names_out(cat_cols).tolist()

    # numeric feature names are unchanged
    return cat_names + num_cols


# ----------------------------
# Main
# ----------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs("src/features", exist_ok=True)

    # 1) Load processed data + feature engineering (row-wise safe)
    df = load_data()
    df = engineer_features(df)

    # 2) Split FIRST (leakage-safe)
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # 3) Fit preprocess on TRAIN only
    preprocessor = build_preprocessor(X_train)
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    # 4) Save arrays (sparse safe)
    X_train_out = X_train_t.tocsr() if issparse(X_train_t) else csr_matrix(X_train_t)
    X_test_out  = X_test_t.tocsr()  if issparse(X_test_t)  else csr_matrix(X_test_t)

    save_npz(X_TRAIN_PATH, X_train_out)
    save_npz(X_TEST_PATH, X_test_out)
    np.save(Y_TRAIN_PATH, y_train.to_numpy())
    np.save(Y_TEST_PATH, y_test.to_numpy())

    # 5) Save feature names
    feature_names = get_feature_names(preprocessor, X_train)
    with open(FEATURE_LIST_PATH, "w") as f:
        json.dump(feature_names, f, indent=2)

    # 6) Save preprocessor (needed later for inference)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)

    print("\n [DAY 2] Features built and saved")
    print("Saved:", X_TRAIN_PATH)
    print("Saved:", X_TEST_PATH)
    print("Saved:", Y_TRAIN_PATH)
    print("Saved:", Y_TEST_PATH)
    print("Saved:", FEATURE_LIST_PATH)
    print("Saved:", PREPROCESSOR_PATH)
    print(f"Total features: {len(feature_names)}\n")


if __name__ == "__main__":
    main()
