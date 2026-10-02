import pandas as pd
import joblib
from pathlib import Path


# ML project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Load trained model and scaler
kmeans = joblib.load(BASE_DIR / "models" / "segmentation_kmeans.pkl")
scaler = joblib.load(BASE_DIR / "models" / "segmentation_scaler.pkl")

def predict_segment(recency, frequency, monetary):
    """
    Predict the customer segment using RFM values.
    """

    data = pd.DataFrame(
        [[recency, frequency, monetary]],
        columns=["Recency", "Frequency", "Monetary"]
    )

    scaled_data = scaler.transform(data)

    cluster = kmeans.predict(scaled_data)[0]

    segment_names = {
        0: "Active / Regular",
        1: "Inactive / At Risk",
        2: "VIP / High Value"
    }

    return {
        "cluster": int(cluster),
        "segment": segment_names[cluster]
    }


if __name__ == "__main__":
    result = predict_segment(
        recency=20,
        frequency=10,
        monetary=3000
    )

    print(result)