import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "retail_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "churn_data.csv"


# --------------------------------------------------
# Configuration
# --------------------------------------------------
CUTOFF_DATE = pd.Timestamp("2011-08-31")
CHURN_WINDOW_DAYS = 90


# --------------------------------------------------
# Load data
# --------------------------------------------------
df = pd.read_csv(INPUT_FILE)

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])


# --------------------------------------------------
# Remove cancellations / invalid transactions
# --------------------------------------------------
df["Invoice"] = df["Invoice"].astype(str)

df = df[
    (~df["Invoice"].str.startswith("C"))
    & (df["Quantity"] > 0)
    & (df["TotalAmount"] > 0)
].copy()


# --------------------------------------------------
# Split past and future transactions
# --------------------------------------------------
past = df[df["InvoiceDate"] <= CUTOFF_DATE].copy()

future_end = CUTOFF_DATE + pd.Timedelta(days=CHURN_WINDOW_DAYS)

future = df[
    (df["InvoiceDate"] > CUTOFF_DATE)
    & (df["InvoiceDate"] <= future_end)
].copy()


# --------------------------------------------------
# Create customer features
# --------------------------------------------------
customer_features = past.groupby("Customer ID").agg(
    LastPurchase=("InvoiceDate", "max"),
    Frequency=("Invoice", "nunique"),
    Monetary=("TotalAmount", "sum"),
    TotalQuantity=("Quantity", "sum")
).reset_index()


# --------------------------------------------------
# Recency
# --------------------------------------------------
customer_features["Recency"] = (
    CUTOFF_DATE - customer_features["LastPurchase"]
).dt.days


# --------------------------------------------------
# Average Order Value
# --------------------------------------------------
customer_features["AvgOrderValue"] = (
    customer_features["Monetary"]
    / customer_features["Frequency"]
)


# --------------------------------------------------
# Create churn target
# --------------------------------------------------
future_customers = set(future["Customer ID"].unique())

customer_features["Churn"] = (
    ~customer_features["Customer ID"].isin(future_customers)
).astype(int)


# --------------------------------------------------
# Select final columns
# --------------------------------------------------
churn_data = customer_features[
    [
        "Customer ID",
        "Recency",
        "Frequency",
        "Monetary",
        "TotalQuantity",
        "AvgOrderValue",
        "Churn"
    ]
].copy()


# --------------------------------------------------
# Save
# --------------------------------------------------
churn_data.to_csv(OUTPUT_FILE, index=False)


# --------------------------------------------------
# Summary
# --------------------------------------------------
print("Churn dataset created successfully.")
print(f"Cutoff date: {CUTOFF_DATE.date()}")
print(f"Future window end: {future_end.date()}")
print(f"Customers: {len(churn_data)}")
print(f"Churned: {churn_data['Churn'].sum()}")
print(f"Not churned: {(churn_data['Churn'] == 0).sum()}")
print(f"Churn rate: {churn_data['Churn'].mean() * 100:.2f}%")
print(f"Saved to: {OUTPUT_FILE}")
print("\nColumns:")
print(churn_data.columns.tolist())
print("\nFirst 5 rows:")
print(churn_data.head())