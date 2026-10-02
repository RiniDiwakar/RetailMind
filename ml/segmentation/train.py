import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib


# Load RFM data
rfm = pd.read_csv("data/processed/rfm.csv")

# Features used for segmentation
features = ["Recency", "Frequency", "Monetary"]
X = rfm[features]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train K-Means
kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

rfm["Cluster"] = kmeans.fit_predict(X_scaled)

# Save trained model and scaler
joblib.dump(kmeans, "models/segmentation_kmeans.pkl")
joblib.dump(scaler, "models/segmentation_scaler.pkl")

# Display segment statistics
print("\nSegment Statistics:")
print(
    rfm.groupby("Cluster")[features]
    .mean()
    .round(2)
)

print("\nSegment Sizes:")
print(rfm["Cluster"].value_counts().sort_index())

print("\nSegmentation training completed.")