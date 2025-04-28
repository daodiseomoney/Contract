"""
BIM Controller for the Real Estate Tokenization platform.
Handles BIM-related API endpoints and view rendering.
"""

import logging
import os
from typing import Dict, List
from flask import Blueprint, jsonify, render_template, request, current_app

from src.services.ai.bim_agent import BIMAgentManager
from src.services.ai.ai_agent_service import AIAgentService
from src.gateways.ifc.ifc_gateway import IFCGateway

# Configure logging
logger = logging.getLogger(__name__)

# Create a Flask Blueprint
bim_bp = Blueprint("bim", __name__, url_prefix="/api/bim")

# Initialize services
bim_agent_manager = BIMAgentManager()
ai_service = AIAgentService()

@bim_bp.route("/load", methods=["POST"])
def load_bim_file():
    """API endpoint to load a BIM file"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
            
        # Ensure file exists
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "message": f"File not found: {file_path}"
            }), 404
            
        # Attempt to load file using BIM agent manager
        result = bim_agent_manager.load_ifc_file(file_path)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error loading BIM file: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/building-data", methods=["GET"])
def get_building_data():
    """API endpoint to get building data"""
    try:
        result = bim_agent_manager.get_building_data()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting building data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/process-message", methods=["POST"])
def process_message():
    """API endpoint to process a message using the BIM agent"""
    try:
        data = request.json
        message = data.get("message")
        
        if not message:
            return jsonify({
                "success": False,
                "message": "No message provided"
            }), 400
            
        # Process the message using BIM agent manager
        result = bim_agent_manager.process_message(message)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/element/<element_id>", methods=["GET"])
def get_element(element_id):
    """API endpoint to get element details by ID"""
    try:
        result = bim_agent_manager.get_element_by_id(element_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting element: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/element-types", methods=["GET"])
def get_element_types():
    """API endpoint to get all element types"""
    try:
        element_types = bim_agent_manager.get_element_types()
        return jsonify({
            "success": True,
            "element_types": element_types
        })
        
    except Exception as e:
        logger.error(f"Error getting element types: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/elements/<element_type>", methods=["GET"])
def get_elements_by_type(element_type):
    """API endpoint to get all elements of a specific type"""
    try:
        elements = bim_agent_manager.get_elements_by_type(element_type)
        return jsonify({
            "success": True,
            "elements": elements
        })
        
    except Exception as e:
        logger.error(f"Error getting elements by type: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/enhanced-mode", methods=["POST"])
def toggle_enhanced_mode():
    """API endpoint to toggle enhanced mode"""
    try:
        data = request.json
        enabled = data.get("enabled", True)
        
        result = bim_agent_manager.toggle_enhanced_mode(enabled)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error toggling enhanced mode: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/enhanced-status", methods=["GET"])
def get_enhanced_status():
    """API endpoint to get enhanced mode status"""
    try:
        is_enhanced = bim_agent_manager.get_enhanced_mode()
        return jsonify({
            "success": True,
            "enhanced_mode": is_enhanced
        })
        
    except Exception as e:
        logger.error(f"Error getting enhanced mode status: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@bim_bp.route("/analyze", methods=["POST"])
def analyze_bim_file():
    """API endpoint to perform AI analysis on a BIM file"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
            
        # Ensure file exists
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "message": f"File not found: {file_path}"
            }), 404
            
        # Use AI service to analyze file
        analysis = ai_service.analyze_ifc_file(file_path)
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing BIM file: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500