import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = BASE_DIR / "data" / "processed" / "churn_data.csv"
MODEL_FILE = BASE_DIR / "models" / "churn_model.pkl"


# --------------------------------------------------
# Load data and model
# --------------------------------------------------
df = pd.read_csv(DATA_FILE)

package = joblib.load(MODEL_FILE)

model = package["model"]

FEATURES = package["features"]


# --------------------------------------------------
# Same train-test split used throughout the project
# --------------------------------------------------
X = df[FEATURES]
y = df["Churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# Train model
# --------------------------------------------------
model.fit(X_train, y_train)

probabilities = model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# Compare thresholds
# --------------------------------------------------
thresholds = [0.35, 0.40, 0.45, 0.50]

print("========== THRESHOLD COMPARISON ==========\n")

for threshold in thresholds:

    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions
    ).ravel()

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    print(f"Threshold: {threshold:.2f}")
    print(f"True Negatives : {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives : {tp}")
    print(f"Precision      : {precision:.4f}")
    print(f"Recall         : {recall:.4f}")
    print(f"F1 Score       : {f1:.4f}")
    print("-" * 40)