"""
IFC Controller for handling IFC file operations and analysis.
"""

import logging
import os
from flask import Blueprint, jsonify, request, current_app

from src.services.ai.ai_agent_service import AIAgentService
from src.gateways.ifc.ifc_gateway import IFCGateway

# Configure logging
logger = logging.getLogger(__name__)

# Create a Flask Blueprint
ifc_bp = Blueprint("ifc", __name__, url_prefix="/api/ifc")

# Initialize services
ai_agent_service = AIAgentService()

@ifc_bp.route("/summary", methods=["GET"])
def get_ifc_summary():
    """Get a summary of an IFC file"""
    try:
        file_path = request.args.get("file")
        
        if not file_path:
            # Look for default file in uploads directory
            uploads_dir = os.path.join(os.getcwd(), "uploads")
            
            if not os.path.exists(uploads_dir):
                return jsonify({
                    "success": False,
                    "message": "Uploads directory not found"
                }), 404
            
            # Find first IFC file
            ifc_files = [
                os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir)
                if f.lower().endswith(".ifc")
            ]
            
            if not ifc_files:
                return jsonify({
                    "success": False,
                    "message": "No IFC files found in uploads directory"
                }), 404
            
            file_path = ifc_files[0]
        
        # Use gateway to get summary
        result = ai_agent_service.get_ifc_summary(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting IFC summary: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@ifc_bp.route("/analyze", methods=["POST"])
def analyze_ifc_file():
    """Analyze an IFC file with AI"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
        
        # Use AI agent service to analyze file
        result = ai_agent_service.analyze_ifc_file(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing IFC file: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500