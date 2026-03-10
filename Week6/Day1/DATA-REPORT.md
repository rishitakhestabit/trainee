# DATA REPORT — Day 1

## Files

- Raw data: `src/data/raw/dataset.csv`
- Cleaned data: `src/data/processed/final.csv`
- Pipeline: `src/pipelines/data_pipeline.py`
- EDA notebook: `src/notebooks/EDA.ipynb`

---

## Pipeline Summary

- Load raw CSV from `src/data/raw/dataset.csv`.
- Remove duplicate rows.
- Handle missing values:
  - Numeric: fill with median.
  - Categorical: fill with mode.
- Remove outliers in numeric columns using IQR:
  - Keep only rows within `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]` for each numeric column.
- Save cleaned data to `src/data/processed/final.csv`.

---

## EDA Summary

Performed in `src/notebooks/EDA.ipynb` on `final.csv`:

- Printed dataset shape, column names, dtypes.
- Listed numeric and categorical features.
- Plotted:
  - Correlation heatmap for numeric features.
  - Histograms for numeric features.
  - Bar plots for main categorical feature(s).
- Checked missing values (heatmap and `.isnull().sum()`).

---

## Key Points

- Cleaned dataset has no missing values.
- Duplicates and outliers have been removed.
- Basic relationships between features are visualized

---

## Architecture

![alt text](<screenshots/projectstruc24.png>)

---