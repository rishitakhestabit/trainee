# src/features/custom_transformers.py

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class MedianChargeFeatures(BaseEstimator, TransformerMixin):
    """
    Learns median monthlycharges from TRAIN only, then creates:
    - high_monthly_charge
    - low_tenure_high_charge
    """

    def __init__(self, monthly_col="monthlycharges", tenure_col="tenure"):
        self.monthly_col = monthly_col
        self.tenure_col = tenure_col
        self.median_charge_ = None

    def fit(self, X, y=None):
        X = pd.DataFrame(X).copy()
        self.median_charge_ = float(pd.to_numeric(X[self.monthly_col], errors="coerce").median())
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()

        monthly = pd.to_numeric(X[self.monthly_col], errors="coerce").fillna(0)
        tenure = pd.to_numeric(X[self.tenure_col], errors="coerce").fillna(0)

        X["high_monthly_charge"] = (monthly > self.median_charge_).astype(int)
        X["low_tenure_high_charge"] = ((tenure < 12) & (monthly > self.median_charge_)).astype(int)

        return X
