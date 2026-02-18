import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, ConfusionMatrixDisplay
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from xgboost import XGBClassifier

from src.features.build_features import load_data, prepare_target, TARGET_COL
from src.features.feature_engineering import add_engineered_features_df
from src.features.run_day2_features import build_preprocessor


# -----------------------------
# Outputs
# -----------------------------
OUT_MODELS_DIR = "src/models"
OUT_EVAL_DIR = "src/evaluation"

BEST_MODEL_PATH = os.path.join(OUT_MODELS_DIR, "best_model.pkl")

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")
INFERENCE_PIPELINE_PATH = os.path.join(OUT_MODELS_DIR, f"inference_pipeline_{MODEL_VERSION}.joblib")

METRICS_PATH = os.path.join(OUT_EVAL_DIR, "metrics.json")
CONF_MAT_PATH = os.path.join(OUT_EVAL_DIR, "confusion_matrix.png")
COMPARISON_CSV_PATH = os.path.join(OUT_EVAL_DIR, "model_comparison.csv")

RANDOM_STATE = 42
N_SPLITS = 5


# -----------------------------
# Helpers
# -----------------------------
def compute_scale_pos_weight(y: np.ndarray) -> float:
    pos = np.sum(y == 1)
    neg = np.sum(y == 0)
    return float(neg / max(pos, 1))


def make_base_pipeline(model):
    """
    Full pipeline:
    raw X -> feature engineering -> preprocessor (OHE+scaler) -> model
    """
    return Pipeline(
        steps=[
            ("feat_eng", FunctionTransformer(add_engineered_features_df, validate=False)),
            ("preprocess", build_preprocessor(pd.DataFrame())),  # placeholder; we will replace after split
            ("model", model),
        ]
    )


def build_models(y_train: np.ndarray):
    scale_pos_weight = compute_scale_pos_weight(y_train)

    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=4000,
            class_weight="balanced",
            solver="saga",
            random_state=RANDOM_STATE
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=500,
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=RANDOM_STATE,
            class_weight="balanced_subsample"
        ),
        "XGBoost": XGBClassifier(
            n_estimators=600,
            learning_rate=0.03,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            tree_method="hist",
            scale_pos_weight=scale_pos_weight,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        # NOTE: MLP needs dense input -> we will add densify step before model
        "NeuralNetwork_MLP": MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            alpha=1e-4,
            max_iter=600,
            early_stopping=True,
            random_state=RANDOM_STATE
        )
    }
    return models


def attach_preprocessor(pipeline: Pipeline, X_train_raw: pd.DataFrame) -> Pipeline:
    """
    build_preprocessor() needs actual columns and dtypes, so we build it after feature engineering is applied.
    We do:
      X_train_eng = add_engineered_features_df(X_train_raw)
      preprocessor = build_preprocessor(X_train_eng)
      then set pipeline step preprocess = preprocessor
    """
    X_train_eng = add_engineered_features_df(X_train_raw)
    preprocessor = build_preprocessor(X_train_eng)
    pipeline.set_params(preprocess=preprocessor)
    return pipeline


def add_dense_step_if_needed(name: str, pipeline: Pipeline) -> Pipeline:
    """
    MLP can't take sparse; densify after preprocess.
    """
    if name != "NeuralNetwork_MLP":
        return pipeline

    densify = FunctionTransformer(lambda x: x.toarray() if hasattr(x, "toarray") else x, accept_sparse=True)
    return Pipeline(
        steps=[
            ("feat_eng", pipeline.named_steps["feat_eng"]),
            ("preprocess", pipeline.named_steps["preprocess"]),
            ("to_dense", densify),
            ("model", pipeline.named_steps["model"]),
        ]
    )


SCORING = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
    "roc_auc": "roc_auc",
}


def evaluate_models_cv(X_train_raw: pd.DataFrame, y_train: np.ndarray, models_dict):
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

    results = {}
    for name, model in models_dict.items():
        print(f"\n[CV] Training: {name}")

        # Build a pipeline per model
        pipe = Pipeline(
            steps=[
                ("feat_eng", FunctionTransformer(add_engineered_features_df, validate=False)),
                ("preprocess", "passthrough"),  # set below
                ("model", model),
            ]
        )
        pipe = attach_preprocessor(pipe, X_train_raw)
        pipe = add_dense_step_if_needed(name, pipe)

        scores = cross_validate(
            pipe,
            X_train_raw, y_train,
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


def plot_and_save_confusion_matrix(model, X_test_raw, y_test, save_path):
    y_pred = model.predict(X_test_raw)
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    plt.figure(figsize=(6, 5))
    disp.plot(values_format="d")
    plt.title("Confusion Matrix (Best Pipeline on Test Set)")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(OUT_MODELS_DIR, exist_ok=True)
    os.makedirs(OUT_EVAL_DIR, exist_ok=True)

    # 1) Load raw data
    df = load_data()
    y = prepare_target(df, TARGET_COL).to_numpy()
    X_raw = df.drop(columns=[TARGET_COL])

    # 2) Train/test split on RAW (important)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # 3) Models (base estimators)
    models = build_models(y_train)

    # 4) CV comparison (pipelines)
    cv_metrics = evaluate_models_cv(X_train_raw, y_train, models)

    comparison_df = build_model_comparison_table(cv_metrics)
    comparison_df.to_csv(COMPARISON_CSV_PATH, index=False)

    print("\n[MODEL COMPARISON — CV MEAN SCORES]")
    print(comparison_df.to_string(index=False))

    # 5) Pick best model by ROC-AUC
    best_name, best_score = pick_best_model(cv_metrics, primary="roc_auc")
    print(f"\nBest model: {best_name} | CV ROC-AUC: {best_score:.4f}\n")

    # 6) Build final best pipeline
    best_estimator = models[best_name]
    best_pipeline = Pipeline(
        steps=[
            ("feat_eng", FunctionTransformer(add_engineered_features_df, validate=False)),
            ("preprocess", "passthrough"),
            ("model", best_estimator),
        ]
    )
    best_pipeline = attach_preprocessor(best_pipeline, X_train_raw)
    best_pipeline = add_dense_step_if_needed(best_name, best_pipeline)

    # 7) Fit on train
    best_pipeline.fit(X_train_raw, y_train)

    # 8) Evaluate on test
    y_pred = best_pipeline.predict(X_test_raw)

    y_proba = None
    if hasattr(best_pipeline, "predict_proba"):
        y_proba = best_pipeline.predict_proba(X_test_raw)[:, 1]

    holdout_test_metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if y_proba is not None else None
    }

    # 9) Save artifacts
    plot_and_save_confusion_matrix(best_pipeline, X_test_raw, y_test, CONF_MAT_PATH)

    # best pipeline for general usage
    joblib.dump(best_pipeline, BEST_MODEL_PATH)

    # versioned pipeline for Day-5 inference
    joblib.dump(best_pipeline, INFERENCE_PIPELINE_PATH)

    with open(METRICS_PATH, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "model_version": MODEL_VERSION,
            "best_model": best_name,
            "cv_metrics": cv_metrics,
            "holdout_test_metrics": holdout_test_metrics,
            "saved_best_model_path": BEST_MODEL_PATH,
            "saved_inference_pipeline_path": INFERENCE_PIPELINE_PATH
        }, f, indent=2)

    print("\nHoldout test metrics:")
    for k, v in holdout_test_metrics.items():
        print(f"  {k}: {v}")

    print("\nSaved:")
    print(" ", BEST_MODEL_PATH)
    print(" ", INFERENCE_PIPELINE_PATH)
    print(" ", METRICS_PATH)
    print(" ", CONF_MAT_PATH)
    print(" ", COMPARISON_CSV_PATH)


if __name__ == "__main__":
    main()
