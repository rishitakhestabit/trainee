# src/features/feature_selector.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt


def correlation_filter(X, feature_names, threshold=0.90):
    """
    WHAT: Remove highly correlated features.
    WHY: Reduces redundancy and multicollinearity.
    HOW: correlation matrix + upper triangle filtering.
    """
    X_df = pd.DataFrame(X, columns=feature_names)
    corr = X_df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    drop_cols = [c for c in upper.columns if any(upper[c] > threshold)]
    return drop_cols


def logistic_feature_importance(X, y, feature_names, top_k=20):
    """
    WHAT: Rank features by logistic regression coefficients.
    WHY: Gives interpretable feature importance quickly.
    HOW: Fit logistic regression, take absolute coefficients.
    """
    model = LogisticRegression(max_iter=2000)
    model.fit(X, y)

    imp = np.abs(model.coef_[0])
    imp_df = pd.DataFrame({"feature": feature_names, "importance": imp})
    imp_df = imp_df.sort_values("importance", ascending=False)

    return imp_df.head(top_k), imp_df


def plot_feature_importance(imp_df):
    """
    WHAT: Plot top feature importances.
    WHY: Required output for Day 2.
    HOW: matplotlib horizontal bar chart.
    """
    plt.figure(figsize=(9, 6))
    plt.barh(imp_df["feature"], imp_df["importance"])
    plt.gca().invert_yaxis()
    plt.title("Top Feature Importance (Logistic Regression)")
    plt.tight_layout()
    plt.show()
