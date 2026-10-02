import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV
)

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = BASE_DIR / "data" / "processed" / "churn_data.csv"
MODEL_FILE = BASE_DIR / "models" / "churn_random_forest_tuned.pkl"


# --------------------------------------------------
# Load dataset
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
# Train-test split
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# Base Random Forest
# --------------------------------------------------
rf = RandomForestClassifier(
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# --------------------------------------------------
# Parameter grid
# --------------------------------------------------
param_grid = {
    "n_estimators": [200, 300],
    "max_depth": [6, 8, 10],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2]
}


# --------------------------------------------------
# Cross-validation
# --------------------------------------------------
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# --------------------------------------------------
# Grid Search
# --------------------------------------------------
grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    scoring="roc_auc",
    cv=cv,
    n_jobs=-1,
    verbose=1
)

print("Starting GridSearchCV...")

grid_search.fit(X_train, y_train)

print("\nGridSearchCV completed.")


# --------------------------------------------------
# Best parameters
# --------------------------------------------------
print("\nBest Parameters:")
print(grid_search.best_params_)

print("\nBest Cross-Validation ROC-AUC:")
print(f"{grid_search.best_score_:.4f}")


# --------------------------------------------------
# Best model
# --------------------------------------------------
best_model = grid_search.best_estimator_


# --------------------------------------------------
# Test set evaluation
# --------------------------------------------------
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]


accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)


print("\n========== TUNED RANDOM FOREST ==========")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")


print("\nClassification Report:")
print(classification_report(y_test, y_pred))


print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# --------------------------------------------------
# Feature importance
# --------------------------------------------------
importance = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": best_model.feature_importances_
}).sort_values(
    "Importance",
    ascending=False
)

print("\nFeature Importance:")
print(importance.to_string(index=False))


# --------------------------------------------------
# Save tuned model
# --------------------------------------------------
joblib.dump(best_model, MODEL_FILE)

print("\nTuned model saved to:")
print(MODEL_FILE)