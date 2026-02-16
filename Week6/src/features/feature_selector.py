# src/features/feature_selector.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from scipy import sparse


def logistic_feature_importance(X, y, feature_names, top_k=20):
    """
    Works with sparse matrices from OneHotEncoder.
    """
    if sparse.issparse(X):
        X_mat = X
    else:
        X_mat = np.asarray(X)

    model = LogisticRegression(
        max_iter=3000,
        solver="saga",
        n_jobs=-1
    )
    model.fit(X_mat, y)

    imp = np.abs(model.coef_[0])
    imp_df = pd.DataFrame({"feature": feature_names, "importance": imp})
    imp_df = imp_df.sort_values("importance", ascending=False)

    return imp_df.head(top_k), imp_df


def plot_feature_importance(top_df, save_path=None):
    plt.figure(figsize=(10, 6))
    plt.barh(top_df["feature"], top_df["importance"])
    plt.gca().invert_yaxis()
    plt.title("Top Feature Importance (Logistic Regression)")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()
