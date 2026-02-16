# src/training/train.py

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold, train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, ConfusionMatrixDisplay
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

# Day-2 pipeline reuse (feature engineering + encoding)
from src.features.build_features import load_data, engineer_features, encode_features

# Leakage-safe transformer (train-only median features) if you already created it.
# If you don't want this, you can remove this step from pipelines.
from src.features.custom_transformers import MedianChargeFeatures


# -----------------------------
# Config
# -----------------------------
TARGET_COL = "churn"
N_SPLITS = 5
RANDOM_STATE = 42

BEST_MODEL_PATH = "src/models/best_model.pkl"
METRICS_PATH = "src/evaluation/metrics.json"
CONF_MAT_PATH = "src/evaluation/confusion_matrix.png"
COMPARISON_CSV_PATH = "src/evaluation/model_comparison.csv"


# -----------------------------
# Data build (reuses Day 2)
# -----------------------------
def build_xy():
    """
    WHAT: Build final dataset (X, y) using Day-2 feature engineering & encoding.
    WHY: Avoid duplicating feature logic in training script.
    HOW: load_data -> engineer_features -> encode_features -> split X/y.
    """
    df = load_data()
    df = engineer_features(df)
    df = encode_features(df)

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target '{TARGET_COL}' not found after encoding.")

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]
    return X, y


# -----------------------------
# Models (4)
# -----------------------------
def get_models():
    """
    Day-3 models:
    1) Logistic Regression
    2) Random Forest
    3) HistGradientBoosting (sklearn boosting)
    4) Neural Network (MLP)

    Notes:
    - Scaling is used for LR + MLP.
    - Trees/boosting do not require scaling.
    - class_weight helps imbalanced churn.
    """
    models = {}

    # 1) Logistic Regression (simple + strong on tabular churn)
    models["LogisticRegression"] = Pipeline([
        ("median_feats", MedianChargeFeatures()),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=3000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=RANDOM_STATE
        ))
    ])

    # 2) Random Forest (non-linear)
    models["RandomForest"] = Pipeline([
        ("median_feats", MedianChargeFeatures()),
        ("model", RandomForestClassifier(
            n_estimators=700,                 # more trees -> stabler performance (not tuning)
            max_depth=None,                  # let it learn; min_samples_* controls overfit
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample"
        ))
    ])

    # 3) HistGradientBoosting (boosting-like model in sklearn)
    models["HistGradientBoosting"] = Pipeline([
        ("median_feats", MedianChargeFeatures()),
        ("model", HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_depth=6,
            max_iter=400,
            random_state=RANDOM_STATE
        ))
    ])

    # 4) MLP Neural Net (needs scaling)
    models["NeuralNetwork_MLP"] = Pipeline([
        ("median_feats", MedianChargeFeatures()),
        ("scaler", StandardScaler()),
        ("model", MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            alpha=1e-4,              # default-ish; keeps training stable
            max_iter=600,
            early_stopping=True,
            random_state=RANDOM_STATE
        ))
    ])

    return models


# -----------------------------
# Scoring
# -----------------------------
SCORING = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
    "roc_auc": "roc_auc",
}


def evaluate_models_cv(X, y, models):
    """
    WHAT: Evaluate all models with 5-fold CV.
    WHY: Fair comparison + stable metrics.
    HOW: StratifiedKFold + cross_validate with multiple metrics.
    """
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    results = {}
    for name, model in models.items():
        print(f"\n[CV] Training: {name}")

        scores = cross_validate(
            model,
            X, y,
            cv=cv,
            scoring=SCORING,
            n_jobs=-1,
            return_train_score=False
        )

        results[name] = {
            metric: {
                "mean": float(np.mean(scores[f"test_{metric}"])),
                "std": float(np.std(scores[f"test_{metric}"]))
            }
            for metric in SCORING.keys()
        }

    return results


def pick_best_model(metrics_dict, primary="roc_auc"):
    """
    WHAT: Choose the best model using CV mean of primary metric.
    WHY: For churn, ROC-AUC is threshold-independent and robust for imbalance.
    HOW: argmax over models.
    """
    best_name = None
    best_score = -1.0
    for name, m in metrics_dict.items():
        score = m[primary]["mean"]
        if score > best_score:
            best_score = score
            best_name = name
    return best_name, best_score


def build_model_comparison_table(metrics_dict):
    """
    WHAT: Make a clean comparison table (CV means).
    WHY: Helps you write MODEL-COMPARISON.md.
    HOW: Convert dict -> DataFrame and sort by ROC-AUC.
    """
    rows = []
    for model_name, m in metrics_dict.items():
        rows.append({
            "model": model_name,
            "roc_auc_mean": m["roc_auc"]["mean"],
            "f1_mean": m["f1"]["mean"],
            "recall_mean": m["recall"]["mean"],
            "precision_mean": m["precision"]["mean"],
            "accuracy_mean": m["accuracy"]["mean"],
        })

    df = pd.DataFrame(rows).sort_values("roc_auc_mean", ascending=False)
    return df


def plot_and_save_confusion_matrix(model, X_test, y_test, save_path):
    """
    WHAT: Plot confusion matrix for best model on holdout set.
    WHY: Day-3 required visualization.
    HOW: ConfusionMatrixDisplay + savefig.
    """
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    plt.figure(figsize=(6, 5))
    disp.plot(values_format="d")
    plt.title("Confusion Matrix (Best Model on Test Set)")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def main():
    os.makedirs("src/models", exist_ok=True)
    os.makedirs("src/evaluation", exist_ok=True)

    # Build dataset
    X, y = build_xy()
    models = get_models()

    # Holdout split (final reporting)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # 5-fold CV comparison on training portion only
    cv_metrics = evaluate_models_cv(X_train, y_train, models)

    # Comparison table (for MODEL-COMPARISON.md)
    comparison_df = build_model_comparison_table(cv_metrics)
    comparison_df.to_csv(COMPARISON_CSV_PATH, index=False)

    print("\n[MODEL COMPARISON — CV MEAN SCORES]")
    print(comparison_df.to_string(index=False))
    print(f"\nSaved comparison table: {COMPARISON_CSV_PATH}")

    # Pick best model
    best_name, best_score = pick_best_model(cv_metrics, primary="roc_auc")
    best_model = models[best_name]

    print("\n==============================")
    print(f"✅ Best model: {best_name} | CV ROC-AUC: {best_score:.4f}")
    print("==============================\n")

    # Fit best model on full training data
    best_model.fit(X_train, y_train)

    # Predict on test set
    y_pred = best_model.predict(X_test)

    # ROC-AUC should be computed using probabilities (or decision_function)
    if hasattr(best_model, "predict_proba"):
        y_proba = best_model.predict_proba(X_test)[:, 1]
    elif hasattr(best_model, "decision_function"):
        scores = best_model.decision_function(X_test)
        y_proba = 1 / (1 + np.exp(-scores))  # approximate sigmoid
    else:
        y_proba = None

    holdout_test_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if y_proba is not None else None,
    }

    # Save confusion matrix image
    plot_and_save_confusion_matrix(best_model, X_test, y_test, CONF_MAT_PATH)

    # Save best model
    joblib.dump(best_model, BEST_MODEL_PATH)

    # Save metrics.json
    payload = {
        "generated_at": datetime.now().isoformat(),
        "cv_folds": N_SPLITS,
        "primary_selection_metric": "roc_auc",
        "best_model": best_name,
        "cv_metrics": cv_metrics,
        "holdout_test_metrics": holdout_test_metrics,
        "artifacts": {
            "best_model_path": BEST_MODEL_PATH,
            "metrics_path": METRICS_PATH,
            "confusion_matrix_path": CONF_MAT_PATH,
            "model_comparison_csv": COMPARISON_CSV_PATH
        }
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print("Saved best model to        :", BEST_MODEL_PATH)
    print("Saved metrics to           :", METRICS_PATH)
    print("Saved confusion matrix to  :", CONF_MAT_PATH)
    print("\nHoldout test metrics:")
    for k, v in holdout_test_metrics.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
