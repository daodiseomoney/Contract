"""
Main entry point for the BIM AI Management Dashboard application
"""
import os
import logging
from flask import Flask, render_template, redirect, url_for

# Import blueprints
from src.controllers.bim_agent_controller import bim_agent_bp

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
            template_folder='src/external_interfaces/ui/templates',
            static_folder='src/external_interfaces/ui/static')

# Set secret key from environment or use a default for development
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Register blueprints
app.register_blueprint(bim_agent_bp)

# Routes
@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/viewer')
def viewer():
    """Render the BIM viewer page"""
    return render_template('viewer.html')

@app.route('/upload')
def upload():
    """Render the upload page for BIM models"""
    return render_template('upload.html')

@app.route('/contracts')
def contracts():
    """Render the contracts page"""
    return render_template('contracts.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)