from flask import Flask, jsonify
from flask_cors import CORS

from routes import health_bp
from routes.ml import ml_bp
from routes.dataset import dataset_bp
from routes.customers import customer_bp
from database.init_db import initialize_database

app = Flask(__name__)
CORS(app)

app.register_blueprint(dataset_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(ml_bp)

initialize_database()

# Register Blueprints
app.register_blueprint(health_bp)


@app.route("/")
def home():
    return "RetailMind backend is running"


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "API endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500


if __name__ == "__main__":
    app.run(debug=True)
