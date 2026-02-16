# src/evaluation/shap_analysis.py

import os
import joblib
import shap
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import sparse
from sklearn.metrics import confusion_matrix


MODEL_PATH = "src/models/best_model_tuned.pkl"

X_TEST_PATH = "src/data/processed/X_test.npz"
Y_TEST_PATH = "src/data/processed/y_test.npy"
FEATURE_LIST_PATH = "src/features/feature_list.json"

OUT_DIR = "src/evaluation"
SHAP_PLOT_PATH = os.path.join(OUT_DIR, "shap_summary.png")
FI_PLOT_PATH = os.path.join(OUT_DIR, "feature_importance.png")
ERROR_HEATMAP_PATH = os.path.join(OUT_DIR, "error_analysis_heatmap.png")
ERRORS_CSV_PATH = os.path.join(OUT_DIR, "errors.csv")

RANDOM_STATE = 42


def safe_predict_proba(model, X):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        s = model.decision_function(X)
        return 1 / (1 + np.exp(-s))
    return None


def save_confusion_heatmap(y_true, y_pred, save_path):
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(5, 4))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Error Analysis Heatmap (Confusion Matrix)")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    # annotate values
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")

    plt.xticks([0, 1], ["Non-Churn(0)", "Churn(1)"])
    plt.yticks([0, 1], ["Non-Churn(0)", "Churn(1)"])

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def save_feature_importance_logreg(model, feature_names, save_path, top_k=25):
    # LogisticRegression: coef_ shape = (1, n_features)
    coefs = np.abs(model.coef_[0])
    imp_df = pd.DataFrame({"feature": feature_names, "importance": coefs})
    imp_df = imp_df.sort_values("importance", ascending=False).head(top_k)

    plt.figure(figsize=(10, 6))
    plt.barh(imp_df["feature"][::-1], imp_df["importance"][::-1])
    plt.title(f"Top {top_k} Feature Importance (|coef|)")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    return imp_df


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Load tuned model
    model = joblib.load(MODEL_PATH)

    # 2) Load test artifacts
    X_test = sparse.load_npz(X_TEST_PATH)
    y_test = np.load(Y_TEST_PATH).astype(int)

    # 3) Load feature names
    with open(FEATURE_LIST_PATH, "r") as f:
        feature_names = json.load(f)

    # -----------------------------
    # A) Feature importance (fast)
    # -----------------------------
    fi_df = save_feature_importance_logreg(model, feature_names, FI_PLOT_PATH, top_k=25)
    print("Saved feature importance chart:", FI_PLOT_PATH)

    # -----------------------------
    # B) Error analysis heatmap + error table
    # -----------------------------
    y_pred = model.predict(X_test)
    save_confusion_heatmap(y_test, y_pred, ERROR_HEATMAP_PATH)
    print("Saved error analysis heatmap:", ERROR_HEATMAP_PATH)

    # Save error rows (index + type)
    y_proba = safe_predict_proba(model, X_test)
    errors = []
    for idx, (yt, yp) in enumerate(zip(y_test, y_pred)):
        if yt != yp:
            err_type = "FN" if (yt == 1 and yp == 0) else "FP"
            prob = float(y_proba[idx]) if y_proba is not None else None
            errors.append({"row_index": idx, "actual": int(yt), "pred": int(yp), "type": err_type, "p_churn": prob})

    pd.DataFrame(errors).to_csv(ERRORS_CSV_PATH, index=False)
    print("Saved error table:", ERRORS_CSV_PATH)

    # -----------------------------
    # C) SHAP summary (sampled, to avoid huge memory)
    # -----------------------------
    # SHAP for linear model: convert a subset to dense
    n = X_test.shape[0]
    sample_size = min(800, n)

    rng = np.random.default_rng(RANDOM_STATE)
    idxs = rng.choice(n, size=sample_size, replace=False)

    X_sample = X_test[idxs]
    X_sample_dense = X_sample.toarray() if sparse.issparse(X_sample) else np.asarray(X_sample)

    # Background (smaller)
    bg_size = min(200, sample_size)
    bg_idxs = idxs[:bg_size]
    X_bg = X_test[bg_idxs]
    X_bg_dense = X_bg.toarray() if sparse.issparse(X_bg) else np.asarray(X_bg)

    explainer = shap.LinearExplainer(model, X_bg_dense)
    shap_values = explainer.shap_values(X_sample_dense)

    # plot
    plt.figure()
    shap.summary_plot(
        shap_values,
        X_sample_dense,
        feature_names=feature_names,
        show=False
    )
    plt.tight_layout()
    plt.savefig(SHAP_PLOT_PATH, bbox_inches="tight")
    plt.close()

    print("Saved SHAP summary plot:", SHAP_PLOT_PATH)


if __name__ == "__main__":
    main()
