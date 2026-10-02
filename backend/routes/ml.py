from flask import Blueprint, request, jsonify
import sys
from pathlib import Path
import pandas as pd

# Path to RetailMind ML project
ML_PROJECT = Path(__file__).resolve().parents[2]

if str(ML_PROJECT) not in sys.path:
    sys.path.insert(0, str(ML_PROJECT))

from ml.nba.predict import get_customer_recommendation


ml_bp = Blueprint("ml", __name__)


# =========================================================
# 1. Direct ML Recommendation API
# =========================================================

@ml_bp.route("/api/ml/recommendation", methods=["POST"])
def customer_recommendation():

    try:
        data = request.get_json()

        required_fields = [
            "recency",
            "frequency",
            "monetary",
            "total_quantity",
            "avg_order_value"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing_fields:
            return jsonify({
                "success": False,
                "message": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        result = get_customer_recommendation(
            recency=float(data["recency"]),
            frequency=float(data["frequency"]),
            monetary=float(data["monetary"]),
            total_quantity=float(data["total_quantity"]),
            avg_order_value=float(data["avg_order_value"])
        )

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# 2. Test ML Recommendation from test_ml_data.csv
# =========================================================

@ml_bp.route("/api/ml/customer/<customer_id>", methods=["GET"])
def customer_ml_prediction(customer_id):

    try:

        # Test CSV file
        csv_file = (
            Path(__file__).resolve().parents[1]
            / "test_ml_data.csv"
        )

        # Read CSV
        df = pd.read_csv(csv_file)

        # Find customer
        customer_data = df[
            df["customer_id"].astype(str) == str(customer_id)
        ].copy()

        if customer_data.empty:
            return jsonify({
                "success": False,
                "message": "Customer not found"
            }), 404

        # Convert data types
        customer_data["purchase_date"] = pd.to_datetime(
            customer_data["purchase_date"],
            errors="coerce"
        )

        customer_data["quantity"] = pd.to_numeric(
            customer_data["quantity"],
            errors="coerce"
        )

        customer_data["amount"] = pd.to_numeric(
            customer_data["amount"],
            errors="coerce"
        )

        # Remove invalid rows
        customer_data = customer_data.dropna(
            subset=[
                "purchase_date",
                "quantity",
                "amount"
            ]
        )

        if customer_data.empty:
            return jsonify({
                "success": False,
                "message": "Customer has no valid transaction data"
            }), 400

        # Reference date
        reference_date = customer_data["purchase_date"].max()

        # Customer's latest purchase
        last_purchase = customer_data["purchase_date"].max()

        # Calculate features
        recency = (
            reference_date - last_purchase
        ).days

        frequency = customer_data["invoice"].nunique()

        monetary = customer_data["amount"].sum()

        total_quantity = customer_data["quantity"].sum()

        avg_order_value = (
            monetary / frequency
            if frequency > 0
            else 0
        )

        # Existing ML pipeline
        result = get_customer_recommendation(
            recency=float(recency),
            frequency=float(frequency),
            monetary=float(monetary),
            total_quantity=float(total_quantity),
            avg_order_value=float(avg_order_value)
        )

        return jsonify({
            "success": True,
            "customer_id": customer_id,

            "features": {
                "recency": int(recency),
                "frequency": int(frequency),
                "monetary": float(monetary),
                "total_quantity": int(total_quantity),
                "avg_order_value": float(
                    round(avg_order_value, 2)
                )
            },

            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# 3. ML Recommendation from Uploaded Dataset
# =========================================================

@ml_bp.route(
    "/api/ml/dataset/<int:dataset_id>/customer/<customer_id>",
    methods=["GET"]
)
def customer_ml_from_dataset(dataset_id, customer_id):

    try:

        # Import database connection
        from database.db import get_db_connection

        # Get dataset information
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT stored_filename FROM datasets WHERE id = ?",
            (dataset_id,)
        )

        dataset = cursor.fetchone()

        connection.close()

        # Dataset not found
        if dataset is None:
            return jsonify({
                "success": False,
                "message": "Dataset not found"
            }), 404

        # Uploaded files folder
        upload_folder = (
            Path(__file__).resolve().parents[1]
            / "uploads"
        )

        csv_file = upload_folder / dataset["stored_filename"]

        # File not found
        if not csv_file.exists():
            return jsonify({
                "success": False,
                "message": "Uploaded CSV file not found"
            }), 404

        # Read uploaded CSV
        df = pd.read_csv(csv_file)

        # Required ML columns
        required_columns = [
            "customer_id",
            "invoice",
            "purchase_date",
            "quantity",
            "amount"
        ]

        # Check missing columns
        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            return jsonify({
                "success": False,
                "message": "CSV does not contain required ML columns",
                "missing_columns": missing_columns
            }), 400

        # Find customer
        customer_data = df[
            df["customer_id"].astype(str) == str(customer_id)
        ].copy()

        if customer_data.empty:
            return jsonify({
                "success": False,
                "message": "Customer not found in dataset"
            }), 404

        # Convert customer data types
        customer_data["purchase_date"] = pd.to_datetime(
            customer_data["purchase_date"],
            errors="coerce"
        )

        customer_data["quantity"] = pd.to_numeric(
            customer_data["quantity"],
            errors="coerce"
        )

        customer_data["amount"] = pd.to_numeric(
            customer_data["amount"],
            errors="coerce"
        )

        # Remove invalid rows
        customer_data = customer_data.dropna(
            subset=[
                "purchase_date",
                "quantity",
                "amount"
            ]
        )

        if customer_data.empty:
            return jsonify({
                "success": False,
                "message": "Customer has no valid transaction data"
            }), 400

        # Convert complete dataset purchase dates
        df["purchase_date"] = pd.to_datetime(
            df["purchase_date"],
            errors="coerce"
        )

        # Latest transaction date in entire dataset
        reference_date = df["purchase_date"].max()

        # Customer's latest purchase
        last_purchase = customer_data["purchase_date"].max()

        # Calculate ML features
        recency = (
            reference_date - last_purchase
        ).days

        frequency = customer_data["invoice"].nunique()

        monetary = customer_data["amount"].sum()

        total_quantity = customer_data["quantity"].sum()

        avg_order_value = (
            monetary / frequency
            if frequency > 0
            else 0
        )

        # Send features to existing ML pipeline
        result = get_customer_recommendation(
            recency=float(recency),
            frequency=float(frequency),
            monetary=float(monetary),
            total_quantity=float(total_quantity),
            avg_order_value=float(avg_order_value)
        )

        # Return complete result
        return jsonify({
            "success": True,
            "dataset_id": int(dataset_id),
            "customer_id": customer_id,

            "features": {
                "recency": int(recency),
                "frequency": int(frequency),
                "monetary": float(monetary),
                "total_quantity": int(total_quantity),
                "avg_order_value": float(
                    round(avg_order_value, 2)
                )
            },

            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500