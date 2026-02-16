# src/evaluation/shap_analysis.py

import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import confusion_matrix

from src.features.build_features import load_data, engineer_features, encode_features


MODEL_PATH = "src/models/best_model_tuned.pkl"


def error_analysis(model, X, y):
    """
    WHAT: Visualize model errors (FP / FN)
    WHY: Understand where the model is making mistakes
    HOW: Confusion matrix heatmap
    """
    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)

    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Reds")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Error Analysis Heatmap")
    plt.tight_layout()
    plt.savefig("src/evaluation/error_analysis.png")
    plt.close()


def main():
    # Load tuned model
    model = joblib.load(MODEL_PATH)

    # Rebuild dataset exactly like training
    df = load_data()
    df = engineer_features(df)
    df = encode_features(df)

    X = df.drop(columns=["churn"])
    y = df["churn"]

    # -----------------------------
    # SHAP EXPLAINABILITY
    # -----------------------------

    # Transform features using pipeline steps (excluding final model)
    X_transformed = model[:-1].transform(X)

    explainer = shap.LinearExplainer(
        model.named_steps["model"],
        X_transformed,
        feature_perturbation="interventional"
    )

    shap_values = explainer.shap_values(X_transformed)

    plt.figure()
    shap.summary_plot(
        shap_values,
        X_transformed,
        feature_names=X.columns,
        show=False
    )
    plt.savefig("src/evaluation/shap_summary.png", bbox_inches="tight")
    plt.close()

    print("Saved SHAP summary plot")

    # -----------------------------
    # ERROR ANALYSIS
    # -----------------------------
    error_analysis(model, X, y)
    print("Saved error analysis heatmap")


if __name__ == "__main__":
    main()
