import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from scipy import sparse

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, ConfusionMatrixDisplay
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline

from xgboost import XGBClassifier


# -----------------------------
# Paths (Day-2 artifacts)
# -----------------------------
X_TRAIN_PATH = "src/data/processed/X_train.npz"
X_TEST_PATH  = "src/data/processed/X_test.npz"
Y_TRAIN_PATH = "src/data/processed/y_train.npy"
Y_TEST_PATH  = "src/data/processed/y_test.npy"

BEST_MODEL_PATH = "src/models/best_model.pkl"
METRICS_PATH = "src/evaluation/metrics.json"
CONF_MAT_PATH = "src/evaluation/confusion_matrix.png"
COMPARISON_CSV_PATH = "src/evaluation/model_comparison.csv"

N_SPLITS = 5
RANDOM_STATE = 42


# -----------------------------
# Load prepared data
# -----------------------------
def load_day2_artifacts():
    X_train = sparse.load_npz(X_TRAIN_PATH)
    X_test = sparse.load_npz(X_TEST_PATH)
    y_train = np.load(Y_TRAIN_PATH)
    y_test = np.load(Y_TEST_PATH)
    return X_train, X_test, y_train, y_test


# -----------------------------
# Compute class imbalance weight
# -----------------------------
def compute_class_weight(y):
    pos = np.sum(y == 1)
    neg = np.sum(y == 0)
    return neg / pos


# -----------------------------
# Models (Sparse Compatible)
# -----------------------------
def get_models(y_train):

    scale_weight = compute_class_weight(y_train)

    # convert sparse → dense (only for MLP)
    to_dense = FunctionTransformer(lambda x: x.toarray(), accept_sparse=True)

    return {

        # Logistic Regression (baseline)
        "LogisticRegression": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            solver="saga",
            random_state=RANDOM_STATE
        ),

        # Random Forest
        "RandomForest": RandomForestClassifier(
            n_estimators=500,
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample"
        ),

        # XGBoost 
        "XGBoost": XGBClassifier(
            n_estimators=600,
            learning_rate=0.03,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            tree_method="hist",
            scale_pos_weight=scale_weight,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),

        # Neural Network
        "NeuralNetwork_MLP": Pipeline([
            ("to_dense", to_dense),
            ("mlp", MLPClassifier(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                alpha=1e-4,
                max_iter=600,
                early_stopping=True,
                random_state=RANDOM_STATE
            ))
        ])
    }


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
    best_name, best_score = None, -1.0
    for name, m in metrics_dict.items():
        score = m[primary]["mean"]
        if score > best_score:
            best_score = score
            best_name = name
    return best_name, best_score


def build_model_comparison_table(metrics_dict):
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
    return pd.DataFrame(rows).sort_values("roc_auc_mean", ascending=False)


def plot_and_save_confusion_matrix(model, X_test, y_test, save_path):
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

    # 1) Load prepared data
    X_train, X_test, y_train, y_test = load_day2_artifacts()

    # 2) Models
    models = get_models(y_train)

    # 3) Cross-validation comparison
    cv_metrics = evaluate_models_cv(X_train, y_train, models)

    comparison_df = build_model_comparison_table(cv_metrics)
    comparison_df.to_csv(COMPARISON_CSV_PATH, index=False)

    print("\n[MODEL COMPARISON — CV MEAN SCORES]")
    print(comparison_df.to_string(index=False))

    # 4) Select best model
    best_name, best_score = pick_best_model(cv_metrics, primary="roc_auc")
    best_model = models[best_name]

    print(f"\nBest model: {best_name} | CV ROC-AUC: {best_score:.4f}\n")

    # 5) Train final model
    best_model.fit(X_train, y_train)

    # 6) Evaluate on holdout test
    y_pred = best_model.predict(X_test)

    if hasattr(best_model, "predict_proba"):
        y_proba = best_model.predict_proba(X_test)[:, 1]
    else:
        y_proba = None

    holdout_test_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if y_proba is not None else None
    }

    plot_and_save_confusion_matrix(best_model, X_test, y_test, CONF_MAT_PATH)
    joblib.dump(best_model, BEST_MODEL_PATH)

    with open(METRICS_PATH, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "best_model": best_name,
            "cv_metrics": cv_metrics,
            "holdout_test_metrics": holdout_test_metrics
        }, f, indent=2)

    print("\nHoldout test metrics:")
    for k, v in holdout_test_metrics.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
