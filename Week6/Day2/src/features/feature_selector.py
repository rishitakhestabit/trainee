import sys
sys.path.append('src')

from utils import logger as log_module
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.feature_selection import mutual_info_regression

logger = log_module.setup_logger()

# Dynamic paths
BASE = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE / "data/processed"
LOGS_DIR = BASE / "logs"
LOGS_DIR.mkdir(exist_ok=True)

if __name__ == "__main__":
    # Load train data
    X_train = pd.read_csv(INPUT_DIR / 'X_train.csv')
    y_train = pd.read_csv(INPUT_DIR / 'y_train.csv').values.ravel()
    logger.info("Train data loaded: X%s, y%s", X_train.shape, y_train.shape)
    
    # Correlation filter
    corr = X_train.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > 0.9)]
    X_corr_filtered = X_train.drop(columns=to_drop)
    logger.info("Dropped %d correlated features: %s", len(to_drop), to_drop)
    
    # Mutual information
    mi_scores = mutual_info_regression(X_corr_filtered, y_train, random_state=2025)
    mi_series = pd.Series(mi_scores, index=X_corr_filtered.columns)
    mi_series = mi_series.sort_values(ascending=False)
    logger.info("Mutual information scores calculated")
    
    # Plot top 15
    plt.figure(figsize=(10, 6))
    mi_series.head(15).plot(kind="bar", color='steelblue')
    plt.title("Top 15 Feature Importance (Mutual Information)")
    plt.ylabel("MI Score")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(LOGS_DIR / 'feature_importance.png', dpi=150)
    plt.close()
    logger.info("Feature importance plot saved")
    
    # Log top features
    logger.info("Top 5 features: %s", list(mi_series.head(5).index))
    logger.info("Feature selection completed")
