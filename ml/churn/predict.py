import pandas as pd
import joblib

from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "churn_model.pkl"
)


# --------------------------------------------------
# Load production model package
# --------------------------------------------------
model_package = joblib.load(MODEL_FILE)

model = model_package["model"]
CHURN_THRESHOLD = model_package["threshold"]
FEATURES = model_package["features"]


# --------------------------------------------------
# Prediction function
# --------------------------------------------------
def predict_churn(
    recency,
    frequency,
    monetary,
    total_quantity,
    avg_order_value
):
    """
    Predict churn probability and risk level.
    """

    customer_data = pd.DataFrame([{
        "Recency": recency,
        "Frequency": frequency,
        "Monetary": monetary,
        "TotalQuantity": total_quantity,
        "AvgOrderValue": avg_order_value
    }])

    # Ensure correct feature order
    customer_data = customer_data[FEATURES]

    # Churn probability
    churn_probability = model.predict_proba(
        customer_data
    )[0][1]

    # Apply production threshold
    churn_prediction = int(
        churn_probability >= CHURN_THRESHOLD
    )

    # Risk level
    if churn_probability >= 0.70:
        risk_level = "High"
    elif churn_probability >= CHURN_THRESHOLD:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "churn_probability": round(
            float(churn_probability), 4
        ),
        "churn_prediction": churn_prediction,
        "risk_level": risk_level
    }


# --------------------------------------------------
# Test prediction
# --------------------------------------------------
if __name__ == "__main__":

    result = predict_churn(
        recency=200,
        frequency=2,
        monetary=500,
        total_quantity=100,
        avg_order_value=250
    )

    print("Churn Prediction:")
    print(result)