import sys
sys.path.append('src')

from utils import logger as log_module
import pandas as pd
import numpy as np
from pathlib import Path

logger = log_module.setup_logger()

BASE = Path(__file__).resolve().parent.parent

def generate_features(df):
    """Create 10 new features"""
    # Encode categorical
    df = pd.get_dummies(df, columns=['ocean_proximity'], drop_first=True)
    
    # 10 new features
    df['rooms_per_hh'] = df['total_rooms'] / df['households']
    df['bed_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['pop_per_hh'] = df['population'] / df['households']
    df['log_income'] = np.log1p(df['median_income'])
    df['log_rooms'] = np.log1p(df['total_rooms'])
    df['income_sq'] = df['median_income'] ** 2
    df['income_per_room'] = df['median_income'] / df['total_rooms']
    df['age_income'] = df['housing_median_age'] * df['median_income']
    df['dist_coast'] = np.abs(df['longitude'] + 120)
    df['is_north'] = (df['latitude'] > 37).astype(int)
    
    logger.info("Generated 10 new features")
    return df
