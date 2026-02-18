import json
import numpy as np
from scipy import sparse

from src.features.feature_selector import logistic_feature_importance, plot_feature_importance

X_TRAIN_PATH = "src/data/processed/X_train.npz"
Y_TRAIN_PATH = "src/data/processed/y_train.npy"
FEATURE_LIST_PATH = "src/features/feature_list.json"
PLOT_PATH = "src/features/feature_importance.png"


def main():
    print("\n[INFO] Running feature importance (Day-2 artifacts)")

    X_train = sparse.load_npz(X_TRAIN_PATH)
    y_train = np.load(Y_TRAIN_PATH)

    with open(FEATURE_LIST_PATH, "r") as f:
        feature_names = json.load(f)

    top20, _ = logistic_feature_importance(X_train, y_train, feature_names, top_k=20)

    print("\nTop 20 Important Features:")
    print(top20.to_string(index=False))

    plot_feature_importance(top20, save_path=PLOT_PATH)
    print(f"\nSaved plot: {PLOT_PATH}\n")


if __name__ == "__main__":
    main()
