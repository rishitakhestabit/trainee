# src/training/tuning.py

import json
import os
import joblib
from datetime import datetime

import numpy as np
import pandas as pd

from sklearn.model_selection import GridSearchCV, train_test_split, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from src.features.build_features import load_data, engineer_features, encode_features
from src.features.custom_transformers import MedianChargeFeatures


TARGET_COL = "churn"
RANDOM_STATE = 42

RESULTS_PATH = "src/tuning/results.json"
BEST_MODEL_PATH = "src/models/best_model_tuned.pkl"


def build_xy():
    df = load_data()
    df = engineer_features(df)
    df = encode_features(df)

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]
    return X, y


def main():
    os.makedirs("src/tuning", exist_ok=True)
    os.makedirs("src/models", exist_ok=True)

    X, y = build_xy()

    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    pipeline = Pipeline([
        ("median_feats", MedianChargeFeatures()),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            solver="lbfgs",
            random_state=RANDOM_STATE
        ))
    ])

    param_grid = {
        "model__C": [0.01, 0.1, 1.0, 10.0],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    grid = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_

    joblib.dump(best_model, BEST_MODEL_PATH)

    results = {
        "best_params": grid.best_params_,
        "best_cv_roc_auc": grid.best_score_,
        "generated_at": datetime.now().isoformat()
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("Best Params:", grid.best_params_)
    print("Best CV ROC-AUC:", grid.best_score_)
    print("Saved tuned model to:", BEST_MODEL_PATH)


if __name__ == "__main__":
    main()
