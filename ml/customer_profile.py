import sys
from pathlib import Path


# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# --------------------------------------------------
# Import existing prediction functions
# --------------------------------------------------
from ml.segmentation.predict import predict_segment
from ml.churn.predict import predict_churn


# --------------------------------------------------
# Customer Profile
# --------------------------------------------------
def create_customer_profile(
    recency,
    frequency,
    monetary,
    total_quantity,
    avg_order_value
):
    """
    Generate a combined customer profile using
    segmentation and churn prediction.
    """

    # Segmentation prediction
    segment_result = predict_segment(
        recency=recency,
        frequency=frequency,
        monetary=monetary
    )

    # Churn prediction
    churn_result = predict_churn(
        recency=recency,
        frequency=frequency,
        monetary=monetary,
        total_quantity=total_quantity,
        avg_order_value=avg_order_value
    )

    # Combined profile
    profile = {
        "segment": segment_result["segment"],
        "cluster": segment_result["cluster"],
        "churn_probability": churn_result["churn_probability"],
        "churn_prediction": churn_result["churn_prediction"],
        "risk_level": churn_result["risk_level"]
    }

    return profile


# --------------------------------------------------
# Test
# --------------------------------------------------
if __name__ == "__main__":

    result = create_customer_profile(
        recency=200,
        frequency=2,
        monetary=500,
        total_quantity=100,
        avg_order_value=250
    )

    print("========== CUSTOMER PROFILE ==========")
    print(result)