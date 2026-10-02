import joblib

from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_MODEL = (
    BASE_DIR
    / "models"
    / "churn_random_forest_tuned.pkl"
)

FINAL_MODEL = (
    BASE_DIR
    / "models"
    / "churn_model.pkl"
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------
CHURN_THRESHOLD = 0.35

FEATURES = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AvgOrderValue"
]


# --------------------------------------------------
# Load trained model
# --------------------------------------------------
model = joblib.load(SOURCE_MODEL)


# --------------------------------------------------
# Package production model
# --------------------------------------------------
model_package = {
    "model": model,
    "threshold": CHURN_THRESHOLD,
    "features": FEATURES
}


# --------------------------------------------------
# Save
# --------------------------------------------------
joblib.dump(model_package, FINAL_MODEL)


# --------------------------------------------------
# Verification
# --------------------------------------------------
print("Final churn model packaged successfully.")
print(f"Model type: {type(model).__name__}")
print(f"Threshold: {CHURN_THRESHOLD}")
print(f"Features: {FEATURES}")
print(f"Saved to: {FINAL_MODEL}")