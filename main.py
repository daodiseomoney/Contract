"""
Main entry point for the BIM AI Management Dashboard application
"""

import os
import logging
from flask import Flask, render_template, url_for, request, jsonify, abort
from dotenv import load_dotenv

from src.controllers.bim_controller import bim_bp
from src.controllers.ifc_controller import ifc_bp
from src.controllers.account_controller import account_bp
from src.controllers.transaction_controller import transaction_bp
from src.controllers.upload_controller import upload_bp
from src.controllers.contract_controller import contract_bp
from src.controllers.blockchain_controller import blockchain_bp

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(
    __name__,
    static_folder="src/external_interfaces/ui/static",
    template_folder="src/external_interfaces/ui/templates",
)

# Set secret key from environment or use a default for development
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Register blueprints
app.register_blueprint(bim_bp)
app.register_blueprint(ifc_bp)
app.register_blueprint(account_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(contract_bp)
app.register_blueprint(blockchain_bp)


# Routes
@app.route("/")
def index():
    """Render the main dashboard page"""
    return render_template("dashboard.html")


@app.route("/viewer")
def viewer():
    """Render the BIM viewer page"""
    return render_template("viewer.html")


@app.route("/upload")
def upload():
    """Render the upload page for BIM models"""
    return render_template("upload.html")


@app.route("/contracts")
def contracts():
    """Render the contracts page"""
    return render_template("contracts.html")


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return (
        render_template("error.html", error_code=404, error_message="Page not found"),
        404,
    )


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return (
        render_template("error.html", error_code=500, error_message="Server error"),
        500,
    )


# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
