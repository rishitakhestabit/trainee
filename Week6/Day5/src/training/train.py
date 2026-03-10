import pandas as pd
import numpy as np
import json
import joblib
import matplotlib.pyplot as plt
from pathlib import Path

from ..utils.logger import setup_logger
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

logger = setup_logger()

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data/processed"
MODEL_DIR = BASE / "models"
EVAL_DIR = BASE / "evaluation"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

logger.info("Day 3: classification training started")

# Load data
X_train = pd.read_csv(DATA_DIR / "X_train.csv")
y_train = pd.read_csv(DATA_DIR / "y_train.csv").values.ravel()
X_test  = pd.read_csv(DATA_DIR / "X_test.csv")
y_test  = pd.read_csv(DATA_DIR / "y_test.csv").values.ravel()

# CONVERT REGRESSION TO BINARY CLASSIFICATION
price_threshold = np.median(y_train)  # Median house price as threshold
y_train_class = (y_train > price_threshold).astype(int)  # 0=Affordable, 1=Expensive
y_test_class = (y_test > price_threshold).astype(int)

logger.info(f"X_train={X_train.shape}, y_train_class={y_train_class.shape}")
logger.info(f"Price threshold: ${price_threshold:,.0f}")
logger.info(f"Class distribution: {np.bincount(y_train_class)} (0=Affordable, 1=Expensive)")

models = {
    "LogisticRegression": LogisticRegression(max_iter=200, random_state=2025),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=2025),
    "XGBoost": XGBClassifier(n_estimators=100, random_state=2025),
    "NeuralNetwork": MLPClassifier(hidden_layer_sizes=(32,), max_iter=200, random_state=2025),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2025)
results = {}

for name, model in models.items():
    logger.info(f"Training {name}...")
    
    metrics = {
        "accuracy": [], "precision": [],
        "recall": [], "f1": [], "roc_auc": []
    }

    for train_idx, val_idx in cv.split(X_train, y_train_class):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train_class[train_idx], y_train_class[val_idx]

        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        y_prob = model.predict_proba(X_val)[:, 1]

        metrics["accuracy"].append(accuracy_score(y_val, y_pred))
        metrics["precision"].append(precision_score(y_val, y_pred))
        metrics["recall"].append(recall_score(y_val, y_pred))
        metrics["f1"].append(f1_score(y_val, y_pred))
        metrics["roc_auc"].append(roc_auc_score(y_val, y_prob))

    results[name] = {k: float(np.mean(v)) for k, v in metrics.items()}

    logger.info(f"{name} CV ROC-AUC={results[name]['roc_auc']:.3f}")

best_name = max(results, key=lambda x: results[x]["roc_auc"])
best_model = models[best_name]
logger.info(f"Best model: {best_name}")

# Train final model on full training data
best_model.fit(X_train, y_train_class)
joblib.dump(best_model, MODEL_DIR / "best_model.pkl")

# Test predictions
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]  # Probability of class 1 (Expensive)

test_metrics = {
    "accuracy": float(accuracy_score(y_test_class, y_pred)),
    "precision": float(precision_score(y_test_class, y_pred)),
    "recall": float(recall_score(y_test_class, y_pred)),
    "f1": float(f1_score(y_test_class, y_pred)),
    "roc_auc": float(roc_auc_score(y_test_class, y_prob)),
}

# Confusion matrix plot
cm = confusion_matrix(y_test_class, y_pred)
plt.imshow(cm, cmap="viridis")
plt.title("Confusion Matrix\n(0=Affordable, 1=Expensive)")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.xticks([0, 1], ["Affordable", "Expensive"])
plt.yticks([0, 1], ["Affordable", "Expensive"])
plt.tight_layout()
plt.savefig(EVAL_DIR / "confusion_matrix.png")
plt.close()

results["best_model"] = best_name
results["best_model_test_metrics"] = test_metrics
with open(EVAL_DIR / "metrics.json", "w") as f:
    json.dump(results, f, indent=4)

logger.info(
    f"Done. Best={best_name}, Test ROC-AUC={test_metrics['roc_auc']:.3f}"
)
print(f"Best: {best_name}, Test ROC-AUC: {test_metrics['roc_auc']:.3f}")
