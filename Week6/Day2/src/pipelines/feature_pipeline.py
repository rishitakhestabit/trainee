import sys
sys.path.append('src')

from utils import logger as log_module
from features.build_feature import generate_features
import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = log_module.setup_logger()

BASE = Path(__file__).resolve().parent.parent
INPUT = BASE / "data/processed/final.csv"
OUTPUT_DIR = BASE / "data/processed"
FEAT_DIR = BASE / "features"
FEAT_DIR.mkdir(exist_ok=True)

def build_pipeline(data_path):
    # Load
    df = pd.read_csv(data_path)
    logger.info("Data loaded")
    
    # Generate features (imported from build_features.py)
    df = generate_features(df)
    
    # Split X and y
    y = df['median_house_value']
    X = df.drop(columns=['median_house_value'])
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2025)
    logger.info("Train/test split done")
    
    # Normalize
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=X.columns)
    logger.info("Features normalized")
    
    # Save
    X_train.to_csv(OUTPUT_DIR / 'X_train.csv', index=False)
    X_test.to_csv(OUTPUT_DIR / 'X_test.csv', index=False)
    y_train.to_csv(OUTPUT_DIR / 'y_train.csv', index=False, header=['median_house_value'])
    y_test.to_csv(OUTPUT_DIR / 'y_test.csv', index=False, header=['median_house_value'])
    
    with open(FEAT_DIR / 'feature_list.json', 'w') as f:
        json.dump(list(X.columns), f, indent=2)
    
    logger.info("Pipeline completed with %d features", len(X.columns))
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    build_pipeline(INPUT)
