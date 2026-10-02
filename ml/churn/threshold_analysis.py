import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_predict
)

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = BASE_DIR / "data" / "processed" / "churn_data.csv"
MODEL_FILE = BASE_DIR / "models" / "churn_random_forest_tuned.pkl"


# --------------------------------------------------
# Load data
# --------------------------------------------------
df = pd.read_csv(DATA_FILE)

FEATURES = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AvgOrderValue"
]

X = df[FEATURES]
y = df["Churn"]


# --------------------------------------------------
# Same train-test split
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# Tuned Random Forest configuration
# --------------------------------------------------
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=6,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# --------------------------------------------------
# Cross-validation probabilities
# --------------------------------------------------
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_probabilities = cross_val_predict(
    model,
    X_train,
    y_train,
    cv=cv,
    method="predict_proba",
    n_jobs=-1
)[:, 1]


# --------------------------------------------------
# Threshold analysis
# --------------------------------------------------
thresholds = np.arange(0.30, 0.71, 0.05)

results = []

for threshold in thresholds:

    predictions = (
        cv_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_train,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_train,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_train,
        predictions,
        zero_division=0
    )

    results.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    })


results_df = pd.DataFrame(results)

print("========== CROSS-VALIDATED THRESHOLD ANALYSIS ==========")
print(
    results_df.to_string(
        index=False,
        formatters={
            "Threshold": "{:.2f}".format,
            "Precision": "{:.4f}".format,
            "Recall": "{:.4f}".format,
            "F1": "{:.4f}".format
        }
    )
)


# --------------------------------------------------
# Best threshold by F1
# --------------------------------------------------
best_row = results_df.loc[
    results_df["F1"].idxmax()
]

best_threshold = best_row["Threshold"]

print("\nBest threshold based on F1:")
print(f"Threshold: {best_threshold:.2f}")
print(f"Precision: {best_row['Precision']:.4f}")
print(f"Recall:    {best_row['Recall']:.4f}")
print(f"F1:        {best_row['F1']:.4f}")


# --------------------------------------------------
# Final test evaluation
# --------------------------------------------------
print("\n========== FINAL TEST EVALUATION ==========")

model.fit(X_train, y_train)

test_probabilities = model.predict_proba(X_test)[:, 1]

test_predictions = (
    test_probabilities >= best_threshold
).astype(int)

test_precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_auc = roc_auc_score(
    y_test,
    test_probabilities
)

print(f"Chosen threshold: {best_threshold:.2f}")
print(f"Precision: {test_precision:.4f}")
print(f"Recall:    {test_recall:.4f}")
print(f"F1:        {test_f1:.4f}")
print(f"ROC-AUC:   {test_auc:.4f}")