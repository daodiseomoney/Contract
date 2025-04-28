import os
import logging
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from src.external_interfaces.config import Config
from src.bim.bim_agent import BIMAgentManager

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
        
        # If it's an IFC file, try to load it with the BIM Agent
        if filename.lower().endswith('.ifc'):
            try:
                # Import here to avoid circular imports
                from src.controllers.bim_agent_controller import get_bim_agent_instance
                
                # Get the BIM agent instance
                bim_agent = get_bim_agent_instance()
                
                # Try to load the uploaded IFC file
                load_result = bim_agent.load_ifc_file(file_path)
                
                # Add IFC loading result to the response
                return jsonify(
                    {
                        "success": True,
                        "message": "File uploaded successfully",
                        "filename": filename,
                        "path": file_path,
                        "ifc_loaded": load_result.get("success", False),
                        "ifc_message": load_result.get("message", ""),
                    }
                )
            except Exception as e:
                logger.error(f"Error loading IFC file after upload: {str(e)}")
                # Continue with normal response if loading fails
        
        # Standard response for non-IFC files or if IFC loading failed
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


@upload_bp.route("/ifc/reload", methods=["POST"])
def reload_ifc_file():
    """Force reload of an IFC file"""
    try:
        # Get request data
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({"success": False, "message": "No file path provided"}), 400
        
        # Validate the file path
        if not os.path.exists(file_path):
            return jsonify({"success": False, "message": f"File not found: {file_path}"}), 404
        
        # Load the file with the BIM Agent
        from src.controllers.bim_agent_controller import get_bim_agent_instance
        bim_agent = get_bim_agent_instance()
        
        # Try to load the IFC file
        load_result = bim_agent.load_ifc_file(file_path)
        
        return jsonify(load_result)
    
    except Exception as e:
        logger.error(f"Error reloading IFC file: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
