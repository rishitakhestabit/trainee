# Model Comparison & Selection

## Project: California Housing Dataset
**Day 3 — Classification Pipeline (Affordable/Expensive)**


---

## Model Configurations

- **LogisticRegression**: `max_iter=200, random_state=2025`
- **RandomForest**: `n_estimators=100, random_state=2025`
- **XGBoost**: `n_estimators=100, random_state=2025`
- **NeuralNetwork**: `hidden_layer_sizes=(32,), max_iter=200, random_state=2025`

---

| Model            | CV ROC-AUC | Test ROC-AUC |
|------------------|------------|--------------|
| LogisticRegression | 0.921    | 0.964      |
| RandomForest     | 0.952     | 0.964      |
| **XGBoost**      | **0.964** | **0.964**  |
| NeuralNetwork    | 0.945     | 0.964      |

---

## Confusion Matrix
![Confusion Matrix](src/evaluation/confusion_matrix.png)


---

## Evaluation Method
- **5-fold StratifiedKFold** (`random_state=2025`)
- **Test set evaluation** on 20% holdout
- **Primary metric**: ROC-AUC (model selection + reporting)
- **Other metrics**: Accuracy, Precision, Recall, F1

**Target conversion**: Price > median($169,200) = 1(Expensive), else 0(Affordable)
**Class balance**: 6764 Affordable, 6752 Expensive

---

## Conclusion

**Best Model: XGBoost**
- **CV ROC-AUC**: 0.964 (highest)
- **Test ROC-AUC**: 0.964 (tied highest)
- **Saved as**: `src/models/best_model.pkl`

**Reason**: XGBoost leads CV ROC-AUC and matches best test performance. Excellent price classification.

**Metrics saved**: `src/evaluation/metrics.json`
