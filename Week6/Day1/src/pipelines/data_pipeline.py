import sys
sys.path.append('src')

from utils.logger import setup_logger
logger = setup_logger()
import pandas as pd
import numpy as np
from pathlib import Path

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = BASE_DIR / "src/data/raw/dataset.csv"
PROCESSED_DATA_PATH = BASE_DIR / "src/data/processed/final.csv"

def load_data():
    print("Loading data...")
    try:
        return pd.read_csv(RAW_DATA_PATH)
    except UnicodeDecodeError:
        return pd.read_csv(RAW_DATA_PATH, encoding='latin1')
    logger.info(f"Data loaded with shape {df.shape}")

def clean_data(df):
    print("Cleaning data...")
    
    # Drop duplicates
    df = df.drop_duplicates()
    
    # Fill numeric columns with median
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())
    
    # Fill categorical columns with mode
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna(df[col].mode()[0])
    logger.info("Finished data cleaning")
    return df

def remove_outliers(df):
    print("Removing outliers...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]
    logger.info("Removed outliers using IQR method")
    return df

def save_data(df):
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print("Saved to ",{PROCESSED_DATA_PATH})
    logger.info("Processed data saved")

def main():
    df = load_data()
    df = clean_data(df)
    df = remove_outliers(df)
    save_data(df)
    print("Pipeline complete! Final shape: ", {df.shape})
    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()
