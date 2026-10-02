from flask import Blueprint, jsonify, request
import csv
import os
import uuid
from database.db import get_db_connection
dataset_bp = Blueprint("dataset", __name__)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "uploads"
)


@dataset_bp.route("/api/datasets", methods=["GET"])
def get_datasets():
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM datasets ORDER BY uploaded_at DESC")

    datasets = cursor.fetchall()

    connection.close()

    return jsonify({
        "success": True,
         "datasets": [dict(dataset) for dataset in datasets]
    })
@dataset_bp.route("/api/datasets/<int:dataset_id>", methods=["GET"])
def get_dataset(dataset_id):
    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (dataset_id,)
    )

    dataset = cursor.fetchone()

    connection.close()

    if dataset is None:
        return jsonify({
            "success": False,
            "message": "Dataset not found"
        }), 404

    return jsonify({
        "success": True,
        "dataset": dict(dataset)
    })

@dataset_bp.route("/api/datasets/upload", methods=["POST"])
def upload_dataset():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file provided"
        }), 400
    file = request.files["file"]
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > 10 * 1024 * 1024:
        return jsonify({
            "success": False,
            "message": "File size must be less than 10 MB"
        }), 400

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    if not file.filename.endswith(".csv"):
        return jsonify({
            "success": False,
            "message": "Only CSV files are allowed"
        }), 400

    if file.read(1) == b"":
        return jsonify({
            "success": False,
            "message": "Uploaded CSV file is empty"
        }), 400

    file.seek(0)

    stored_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, stored_filename)
    file.save(file_path)
    file.seek(0)

    try:
        csv_file = file.read().decode("utf-8")
        csv_reader = csv.reader(csv_file.splitlines())

        rows = list(csv_reader)

    except Exception:
        return jsonify({
            "success": False,
            "message": "Invalid CSV file"
        }), 400
    if not rows or not rows[0]:
        return jsonify({
            "success": False,
            "message": "CSV file must contain column headers"
        }), 400
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO datasets (filename, stored_filename) VALUES (?, ?)",
        (file.filename, stored_filename)
    )
    dataset_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message":"File received successfully",
        "dataset_id": dataset_id,
        "filename": file.filename
    })

@dataset_bp.route("/api/datasets/<int:dataset_id>/info", methods=["GET"])
def get_dataset_info(dataset_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (dataset_id,)
    )

    dataset = cursor.fetchone()
    connection.close()

    if dataset is None:
        return jsonify({
            "success": False,
            "message": "Dataset not found"
        }), 404

    file_path = os.path.join(
        UPLOAD_FOLDER,
        dataset["stored_filename"]
    )

    if not os.path.exists(file_path):
        return jsonify({
            "success": False,
            "message": "Dataset file not found"
        }), 404

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)

        if not rows:
            return jsonify({
                "success": False,
                "message": "Dataset is empty"
            }), 400

        columns = rows[0]
        row_count = len(rows) - 1
        column_count = len(columns)
        file_size = os.path.getsize(file_path)

        return jsonify({
            "success": True,
            "dataset": {
                "id": dataset["id"],
                "filename": dataset["filename"],
                "file_size_bytes": file_size,
                "row_count": row_count,
                "column_count": column_count,
                "columns": columns
            }
        })

    except Exception as e:
        print("VALIDATION ERROR:", repr(e))
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
@dataset_bp.route("/api/datasets/<int:dataset_id>/validate", methods=["GET"])
def validate_dataset(dataset_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (dataset_id,)
    )

    dataset = cursor.fetchone()
    connection.close()

    if dataset is None:
        return jsonify({
            "success": False,
            "message": "Dataset not found"
        }), 404

    file_path = os.path.join(
        UPLOAD_FOLDER,
        dataset["stored_filename"]
    )

    if not os.path.exists(file_path):
        return jsonify({
            "success": False,
            "message": "Dataset file not found"
        }), 404

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)

        if not rows:
            return jsonify({
                "success": False,
                "message": "Dataset is empty"
            }), 400

        headers = rows[0]
        data_rows = rows[1:]

        # Required columns
        required_columns = [
            "customer_id",
            "purchase_date",
            "amount",
            "login_frequency"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in headers
        ]

        missing_values = 0
        duplicate_rows = 0
        invalid_date_rows = 0
        invalid_amount_rows = 0
        invalid_login_frequency_rows = 0


        seen_rows = set()

        # Find purchase_date column position
        purchase_date_index = None

        if "purchase_date" in headers:
            purchase_date_index = headers.index("purchase_date")

        for row in data_rows:

            # Missing values
            if any(value.strip() == "" for value in row):
                missing_values += 1

            # Duplicate rows
            row_tuple = tuple(row)

            if row_tuple in seen_rows:
                duplicate_rows += 1
            else:
                seen_rows.add(row_tuple)

            # Invalid purchase dates
            if purchase_date_index is not None:
                if purchase_date_index >= len(row):
                    invalid_date_rows += 1
                else:
                    date_value = row[purchase_date_index].strip()

                    try:
                        from datetime import datetime
                        datetime.strptime(date_value, "%Y-%m-%d")
                    except ValueError:
                        invalid_date_rows += 1
            # Invalid amount
            if "amount" in headers:
                amount_index = headers.index("amount")

                if amount_index >= len(row):
                    invalid_amount_rows += 1
                else:
                    amount_value = row[amount_index].strip()

                    try:
                        float(amount_value)
                    except ValueError:
                        invalid_amount_rows += 1


            # Invalid login frequency
            if "login_frequency" in headers:
                login_frequency_index = headers.index("login_frequency")

                if login_frequency_index >= len(row):
                    invalid_login_frequency_rows += 1
                else:
                    login_frequency_value = row[login_frequency_index].strip()

                    try:
                        int(login_frequency_value)
                    except ValueError:
                        invalid_login_frequency_rows += 1

        valid = (
            len(missing_columns) == 0
            and missing_values == 0
            and duplicate_rows == 0
            and invalid_date_rows == 0
            and invalid_amount_rows == 0
            and invalid_login_frequency_rows == 0
        )
        

        return jsonify({
            "success": True,
            "validation": {
                "total_rows": len(data_rows),
                "total_columns": len(headers),
                "missing_columns": missing_columns,
                "missing_value_rows": missing_values,
                "duplicate_rows": duplicate_rows,
                "invalid_date_rows": invalid_date_rows,
                "invalid_amount_rows": invalid_amount_rows,
                "invalid_login_frequency_rows": invalid_login_frequency_rows,
                "valid": valid
            }
        })

    except Exception as e:
        print("VALIDATION ERROR:", repr(e))
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
@dataset_bp.route("/api/datasets/<int:dataset_id>/rows", methods=["GET"])
def get_dataset_rows(dataset_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM datasets WHERE id = ?",
        (dataset_id,)
    )

    dataset = cursor.fetchone()
    connection.close()

    if dataset is None:
        return jsonify({
            "success": False,
            "message": "Dataset not found"
        }), 404

    file_path = os.path.join(
        UPLOAD_FOLDER,
        dataset["stored_filename"]
    )

    if not os.path.exists(file_path):
        return jsonify({
            "success": False,
            "message": "Dataset file not found"
        }), 404

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            page = request.args.get("page", 1, type=int)
            if page <= 0:
                return jsonify({
                    "success": False,
                    "message": "Page must be greater than 0"
                }), 400
            limit = request.args.get("limit", 10, type=int)
            if limit <= 0:
                return jsonify({
                    "success": False,
                    "message": "Limit must be greater than 0"
                }), 400
            if limit > 100:
                return jsonify({
                    "success": False,
                    "message": "Limit cannot be greater than 100"
            }), 400
            rows = list(csv_reader)
            start = (page - 1) * limit
            end = start + limit

            rows = rows[start:end]
        return jsonify({
            "success": True,
            "dataset_id": dataset_id,
            "page": page,
            "limit": limit,
            "rows": rows
        })

    except Exception as e:
        print("ROWS ERROR:", repr(e))
        return jsonify({
            "success": False,
            "message": str(e)
    }), 400

@dataset_bp.route("/api/datasets/<int:dataset_id>/customers/<customer_id>", methods=["GET"])
def get_customer(dataset_id, customer_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (dataset_id,)
        )

        dataset = cursor.fetchone()
        connection.close()

        if dataset is None:
            return jsonify({
                "success": False,
                "message": "Dataset not found"
            }), 404

        file_path = os.path.join(
            UPLOAD_FOLDER,
            dataset["stored_filename"]
        )

        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "message": "Dataset file not found"
            }), 404

        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                if row.get("customer_id") == customer_id:
                    return jsonify({
                        "success": True,
                        "dataset_id": dataset_id,
                        "customer": row
                    })

        return jsonify({
            "success": False,
            "message": "Customer not found"
        }), 404

    except Exception as e:
        print("CUSTOMER ERROR:", repr(e))
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
@dataset_bp.route("/api/datasets/<int:dataset_id>", methods=["DELETE"])
def delete_dataset(dataset_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (dataset_id,)
        )

        dataset = cursor.fetchone()

        if dataset is None:
            connection.close()
            return jsonify({
                "success": False,
                "message": "Dataset not found"
            }), 404

        # Delete uploaded CSV file
        file_path = os.path.join(
            UPLOAD_FOLDER,
            dataset["stored_filename"]
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete database record
        cursor.execute(
            "DELETE FROM datasets WHERE id = ?",
            (dataset_id,)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Dataset deleted successfully",
            "dataset_id": dataset_id
        })

    except Exception as e:
        print("DELETE DATASET ERROR:", repr(e))
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400