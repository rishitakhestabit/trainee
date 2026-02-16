# src/training/tuning.py

import json
import os
from datetime import datetime

import numpy as np
import joblib
from scipy import sparse

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import roc_auc_score


# -----------------------------
# Day-2 artifacts (same as Day-3)
# -----------------------------
X_TRAIN_PATH = "src/data/processed/X_train.npz"
Y_TRAIN_PATH = "src/data/processed/y_train.npy"
X_TEST_PATH = "src/data/processed/X_test.npz"
Y_TEST_PATH = "src/data/processed/y_test.npy"

# Optional: compare with baseline model if exists
BASELINE_MODEL_PATH = "src/models/best_model.pkl"

# Outputs
RESULTS_PATH = "src/tuning/results.json"
BEST_MODEL_PATH = "src/models/best_model_tuned.pkl"

RANDOM_STATE = 42
N_SPLITS = 5


def load_day2_train():
    X_train = sparse.load_npz(X_TRAIN_PATH)
    y_train = np.load(Y_TRAIN_PATH).astype(int)
    return X_train, y_train


def load_day2_test():
    X_test = sparse.load_npz(X_TEST_PATH)
    y_test = np.load(Y_TEST_PATH).astype(int)
    return X_test, y_test


def safe_predict_proba(model, X):
    """Return probability of positive class for ROC-AUC."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        s = model.decision_function(X)
        return 1 / (1 + np.exp(-s))
    return None


def main():
    os.makedirs("src/tuning", exist_ok=True)
    os.makedirs("src/models", exist_ok=True)

    X_train, y_train = load_day2_train()
    X_test, y_test = load_day2_test()

    # Base model for tuning (sparse-friendly)
    base = LogisticRegression(
        solver="saga",          
        max_iter=6000,
        random_state=RANDOM_STATE
    )

    # Grid (keep it simple but meaningful)
    param_grid = {
        "C": [0.01, 0.1, 1.0, 5.0, 10.0],
        "penalty": ["l1", "l2"],
        "class_weight": [None, "balanced"],
    }

    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    grid = GridSearchCV(
        estimator=base,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        verbose=1,
        error_score="raise"
    )

    print("\n[TUNING] GridSearchCV starting...")
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    joblib.dump(best_model, BEST_MODEL_PATH)

    # Evaluate tuned model on holdout test (quick check)
    tuned_proba = safe_predict_proba(best_model, X_test)
    tuned_test_roc_auc = float(roc_auc_score(y_test, tuned_proba)) if tuned_proba is not None else None

    # Optional: compare to baseline (Day-3 best_model.pkl) if it exists
    baseline_test_roc_auc = None
    if os.path.exists(BASELINE_MODEL_PATH):
        try:
            baseline = joblib.load(BASELINE_MODEL_PATH)
            base_proba = safe_predict_proba(baseline, X_test)
            baseline_test_roc_auc = float(roc_auc_score(y_test, base_proba)) if base_proba is not None else None
        except Exception:
            baseline_test_roc_auc = None

    results = {
        "generated_at": datetime.now().isoformat(),
        "cv_folds": N_SPLITS,
        "best_params": grid.best_params_,
        "best_cv_roc_auc": float(grid.best_score_),
        "holdout_test_roc_auc_tuned": tuned_test_roc_auc,
        "holdout_test_roc_auc_baseline": baseline_test_roc_auc,
        "saved_model_path": BEST_MODEL_PATH
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("\n==============================")
    print("Best Params:", grid.best_params_)
    print(" Best CV ROC-AUC:", grid.best_score_)
    print(" Holdout Test ROC-AUC (tuned):", tuned_test_roc_auc)
    if baseline_test_roc_auc is not None:
        print("ℹ Holdout Test ROC-AUC (baseline):", baseline_test_roc_auc)
    print("==============================")
    print("Saved tuned model to:", BEST_MODEL_PATH)
    print("Saved results to    :", RESULTS_PATH)


if __name__ == "__main__":
    main()
