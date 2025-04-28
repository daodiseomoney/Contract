"""
Main entry point for the BIM AI Management Dashboard application
"""

import os
import logging
import sys
from flask import Flask, render_template, url_for, request, jsonify, abort, session
from dotenv import load_dotenv

from src.controllers.bim_controller import bim_bp
from src.controllers.ifc_controller import ifc_bp
from src.controllers.account_controller import account_bp
from src.controllers.transaction_controller import transaction_bp
from src.controllers.upload_controller import upload_bp
from src.controllers.contract_controller import contract_bp
from src.controllers.blockchain_controller import blockchain_bp
from src.security_utils import validate_environment, generate_csrf_token, apply_security_headers

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Validate environment variables before startup
try:
    validate_environment()
except Exception as e:
    logger.critical(f"FATAL: Environment validation failed: {str(e)}")
    sys.exit(1)

# Create Flask app
app = Flask(
    __name__,
    static_folder="src/external_interfaces/ui/static",
    template_folder="src/external_interfaces/ui/templates",
)

# Set secret key from environment (no default fallback in production)
app.secret_key = os.environ.get("SESSION_SECRET")

# Set session cookie security options
app.config['SESSION_COOKIE_SECURE'] = not app.debug  # Secure cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JS access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protect against CSRF

# Register blueprints
app.register_blueprint(bim_bp)
app.register_blueprint(ifc_bp)
app.register_blueprint(account_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(contract_bp)
app.register_blueprint(blockchain_bp)

# Add CSRF protection
@app.before_request
def csrf_protect():
    """Generate CSRF token for the session"""
    if request.method != 'GET':
        token = session.get('csrf_token')
        header_token = request.headers.get('X-CSRF-Token')
        
        if not token or token != header_token:
            logger.warning(f"CSRF validation failed from IP: {request.remote_addr}")
            if not app.debug:  # Only apply in production for now
                abort(403)  # Forbidden

# Generate CSRF token for all templates
@app.context_processor
def inject_csrf_token():
    """Inject CSRF token into all templates"""
    return {'csrf_token': generate_csrf_token()}

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    return apply_security_headers(response)


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
