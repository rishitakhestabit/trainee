# src/features/run_feature_importance.py

import json
import numpy as np
import pandas as pd

from src.features.build_features import (
    load_data,
    engineer_features,
    encode_features,
    split_and_scale
)

from src.features.feature_selector import (
    logistic_feature_importance,
    plot_feature_importance
)


def main():
    print("\n[INFO] Running feature importance")

    # 1. Rebuild features exactly as Day 2
    df = load_data()
    df = engineer_features(df)
    df = encode_features(df)

    X_train, X_test, y_train, y_test, feature_names = split_and_scale(df)

    # 2. Compute feature importance
    top_features, full_importance = logistic_feature_importance(
        X_train,
        y_train,
        feature_names,
        top_k=20
    )

    # 3. Show top features
    print("\nTop 20 Important Features:")
    print(top_features)

    # 4. Plot importance
    plot_feature_importance(top_features)

    print("\n[INFO] Feature importance completed\n")


if __name__ == "__main__":
    main()
