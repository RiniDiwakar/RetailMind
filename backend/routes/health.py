from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "RetailMind backend is running"
    })