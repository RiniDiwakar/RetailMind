from flask import Blueprint, jsonify
from database.db import get_db_connection

customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/api/customers", methods=["GET"])
def get_customers():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()

    connection.close()

    return jsonify({
        "success": True,
        "customers": [dict(customer) for customer in customers]
    })