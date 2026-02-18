import os
import json
from datetime import datetime

import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from src.features.build_features import load_data, prepare_target, TARGET_COL
from src.features.feature_engineering import add_engineered_features_df
from src.features.run_day2_features import build_preprocessor


# Outputs
OUT_TUNING_DIR = "src/tuning"
OUT_MODELS_DIR = "src/models"

RESULTS_PATH = os.path.join(OUT_TUNING_DIR, "results.json")
BEST_MODEL_PATH = os.path.join(OUT_MODELS_DIR, "best_model_tuned.pkl")

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
INFERENCE_PIPELINE_PATH = os.path.join(OUT_MODELS_DIR, f"inference_pipeline_{MODEL_VERSION}.joblib")

RANDOM_STATE = 42
N_SPLITS = 5


def safe_predict_proba(model, X):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        s = model.decision_function(X)
        return 1 / (1 + np.exp(-s))
    return None


def main():
    os.makedirs(OUT_TUNING_DIR, exist_ok=True)
    os.makedirs(OUT_MODELS_DIR, exist_ok=True)

    # 1) Load raw data
    df = load_data()
    y = prepare_target(df, TARGET_COL).to_numpy()
    X_raw = df.drop(columns=[TARGET_COL])

    # 2) Split once to have holdout test for quick check
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # 3) Build preprocess based on engineered TRAIN columns
    X_train_eng = add_engineered_features_df(X_train_raw)
    preprocessor = build_preprocessor(X_train_eng)

    # 4) Base pipeline
    base_pipe = Pipeline(
        steps=[
            ("feat_eng", FunctionTransformer(add_engineered_features_df, validate=False)),
            ("preprocess", preprocessor),
            ("model", LogisticRegression(
                solver="saga",
                max_iter=8000,
                random_state=RANDOM_STATE
            )),
        ]
    )

    # 5) Grid params (note: model__ prefix)
    param_grid = {
        "model__C": [0.01, 0.1, 1.0, 5.0, 10.0],
        "model__penalty": ["l1", "l2"],
        "model__class_weight": [None, "balanced"],
    }

    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    grid = GridSearchCV(
        estimator=base_pipe,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        verbose=1,
        error_score="raise"
    )

    print("\n[TUNING] GridSearchCV starting...")
    grid.fit(X_train_raw, y_train)

    best_pipeline = grid.best_estimator_

    # Save tuned pipeline
    joblib.dump(best_pipeline, BEST_MODEL_PATH)
    joblib.dump(best_pipeline, INFERENCE_PIPELINE_PATH)

    # Evaluate tuned model quickly on holdout test
    tuned_proba = safe_predict_proba(best_pipeline, X_test_raw)
    tuned_test_roc_auc = float(roc_auc_score(y_test, tuned_proba)) if tuned_proba is not None else None

    results = {
        "generated_at": datetime.now().isoformat(),
        "model_version": MODEL_VERSION,
        "cv_folds": N_SPLITS,
        "best_params": grid.best_params_,
        "best_cv_roc_auc": float(grid.best_score_),
        "holdout_test_roc_auc_tuned": tuned_test_roc_auc,
        "saved_model_path": BEST_MODEL_PATH,
        "saved_inference_pipeline_path": INFERENCE_PIPELINE_PATH
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("\n==============================")
    print("Best Params:", grid.best_params_)
    print("Best CV ROC-AUC:", grid.best_score_)
    print("Holdout Test ROC-AUC (tuned):", tuned_test_roc_auc)
    print("==============================")
    print("Saved tuned model to:", BEST_MODEL_PATH)
    print("Saved inference pipeline:", INFERENCE_PIPELINE_PATH)
    print("Saved results to:", RESULTS_PATH)


if __name__ == "__main__":
    main()
