# Feature Engineering & Feature Selection

## Project: California Housing Dataset

**Day 2 — Feature Engineering Pipeline**

---

## Objective

Build a reusable feature engineering pipeline that:

- Encodes categorical variables  
- Transforms numerical features  
- Generates new meaningful features  
- Applies feature selection/analysis  
- Produces model-ready train/test datasets

---

## Folder Structure

- `src/pipelines/`
  - `feature_pipeline.py` (Full feature engineering pipeline)
- `src/features/`
  - `build_feature.py` (generate_features() helper)
  - `feature_selector.py` (feature importance + filtering)
  - `feature_list.json` (final feature names)
- `src/data/processed/`
  - `final.csv` (cleaned data from Day 1)
  - `X_train.csv`
  - `X_test.csv`
  - `y_train.csv`
  - `y_test.csv`
- `src/logs/`
  - `pipeline.log`
  - `feature_importance.png`

---

## Feature Engineering Steps

### 1. Input Data

- Source: `src/data/processed/final.csv`  
- Cleaned dataset from Day 1 pipeline (California housing data)

### 2. Encoding

- `ocean_proximity` → One‑hot encoded with `drop_first=True`  
  (e.g. `ocean_proximity_INLAND`, `..._NEAR OCEAN`, etc.)

### 3. Feature Generation

Generated 10 new features:

- `rooms_per_hh`  
- `bed_per_room`  
- `pop_per_hh`  
- `log_income`  
- `log_rooms`  
- `income_sq`  
- `income_per_room`  
- `age_income`  
- `dist_coast`  
- `is_north`

### 4. Feature Scaling

- Applied `StandardScaler` to all feature columns  
- `fit_transform` on training data, `transform` on test data

### 5. Train/Test Split

- 80% Train / 20% Test  
- `random_state = 2025`  
- Target: `median_house_value`

---

## Feature Selection / Analysis

### Correlation Filter

- Computed absolute correlation between features  
- Dropped features with correlation > 0.9 to reduce redundancy

### Mutual Information

- Used `mutual_info_regression` to score features against `median_house_value`  
- Sorted scores and plotted top 15 features  
- Plot saved as `src/logs/feature_importance.png`

---

## Outputs

- Model-ready datasets:  
  - `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`  
- Feature importance bar plot (mutual information)  
- Final feature list saved as JSON: `src/features/feature_list.json`  
- Detailed logs in `src/logs/pipeline.log`

---
