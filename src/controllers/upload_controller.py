import os
import logging
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
from src.external_interfaces.config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
upload_bp = Blueprint("upload", __name__, url_prefix="/api")

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload requests"""
    if "file" not in request.files:
        logger.debug("No file part in the request")
        return (
            jsonify({"success": False, "message": "No file part in the request"}),
            400,
        )

    file = request.files["file"]

    # If user does not select file, browser submits empty file without filename
    if file.filename == "":
        logger.debug("No selected file")
        return jsonify({"success": False, "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        logger.debug(f"File uploaded successfully: {filename}")
        return jsonify(
            {
                "success": True,
                "message": "File uploaded successfully",
                "filename": filename,
                "path": file_path,
            }
        )

    logger.debug("File type not allowed")
    return jsonify({"success": False, "message": "File type not allowed"}), 400
