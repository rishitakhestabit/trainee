import os
import json
import optuna
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from ..utils.logger import setup_logger
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

logger = setup_logger()

RANDOM_STATE = 2025
N_SPLITS = 5
N_TRIALS = 50

DATA_DIR = "src/data/processed"
TUNING_DIR = "src/tuning"
MODEL_DIR = "src/models"

os.makedirs(TUNING_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Load data 
X_train = pd.read_csv(f"{DATA_DIR}/X_train.csv")
y_train_raw = pd.read_csv(f"{DATA_DIR}/y_train.csv").values.ravel()
y_train = (y_train_raw > np.median(y_train_raw)).astype(int)

print(f"Loaded data: X_train={X_train.shape}, classes={np.bincount(y_train)}")
logger.info(f"Loaded data: X_train={X_train.shape}, classes={np.bincount(y_train)}")

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 8),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'subsample': trial.suggest_float('subsample', 0.7, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.7, 1.0),
        'random_state': RANDOM_STATE,
        'eval_metric': 'logloss'
    }
    
    model = XGBClassifier(**params)
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    scores = []
    
    for train_idx, val_idx in skf.split(X_train, y_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_tr, y_val = y_train[train_idx], y_train[val_idx]
        
        model.fit(X_tr, y_tr)
        y_prob = model.predict_proba(X_val)[:, 1]
        scores.append(roc_auc_score(y_val, y_prob))
    
    return np.mean(scores)

if __name__ == "__main__":
    print(f"Starting Optuna optimization with {N_TRIALS} trials...")
    logger.info(f"Starting Optuna with {N_TRIALS} trials, {N_SPLITS}-fold CV")

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS)
    
    print(f"Optimization complete!")
    logger.info("Optuna optimization complete")
    
    # Train final tuned model
    best_params = study.best_params
    best_params.update({'random_state': RANDOM_STATE, 'eval_metric': 'logloss'})
    print("Training final model with best parameters...")
    logger.info("Training final tuned model")

    best_model = XGBClassifier(**best_params)
    best_model.fit(X_train, y_train)
    
    # Save
    joblib.dump(best_model, f"{MODEL_DIR}/tuned_xgboost.pkl")
    
    results = {
        "best_roc_auc": study.best_value,
        "best_params": best_params,
        "n_trials": len(study.trials)
    }
    
    with open(f"{TUNING_DIR}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Tuning complete. Best CV ROC-AUC: {study.best_value:.4f}")
    print(f"Best params: {best_params}")
    logger.info(f"Tuning complete. Best CV ROC-AUC: {study.best_value:.4f}")
    logger.info(f"Best params: {best_params}")
