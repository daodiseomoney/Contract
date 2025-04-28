"""
BIM Controller for handling building information model routes.
"""

import logging
import uuid
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
import json

from src.services.ai.bim_agent import BIMAgentManager

# Configure logging
logger = logging.getLogger(__name__)

# Create a Flask Blueprint
bim_bp = Blueprint("bim", __name__, url_prefix="/api/bim")

# Initialize BIM Agent Manager
bim_agent_manager = BIMAgentManager()


@bim_bp.route("/enhanced-status", methods=["GET"])
def get_enhanced_status():
    """Get the current status of enhanced AI mode"""
    try:
        enhanced_mode = bim_agent_manager.get_enhanced_mode()
        return jsonify({
            "success": True,
            "enhanced_mode": enhanced_mode
        })
    except Exception as e:
        logger.error(f"Error getting enhanced status: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@bim_bp.route("/toggle-enhanced", methods=["POST"])
def toggle_enhanced_mode():
    """Toggle the enhanced AI mode"""
    try:
        data = request.json
        enabled = data.get("enabled", True)
        result = bim_agent_manager.toggle_enhanced_mode(enabled)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error toggling enhanced mode: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@bim_bp.route("/message", methods=["POST"])
def process_message():
    """Process a user message to the BIM AI assistant"""
    try:
        data = request.json
        message = data.get("message")
        
        if not message:
            return jsonify({
                "success": False,
                "message": "No message provided"
            }), 400
            
        result = bim_agent_manager.process_message(message)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@bim_bp.route("/building", methods=["GET"])
def get_building_data():
    """Get building data for the UI"""
    try:
        result = bim_agent_manager.get_building_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting building data: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@bim_bp.route("/element/<element_id>", methods=["GET"])
def get_element(element_id):
    """Get a specific element by ID"""
    try:
        result = bim_agent_manager.get_element_by_id(element_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting element: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@bim_bp.route("/element-types", methods=["GET"])
def get_element_types():
    """Get all element types in the loaded IFC file"""
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
            "message": str(e)
        }), 500


@bim_bp.route("/elements-by-type/<element_type>", methods=["GET"])
def get_elements_by_type(element_type):
    """Get all elements of a specific type"""
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
            "message": str(e)
        }), 500


@bim_bp.route("/load-ifc", methods=["POST"])
def load_ifc_file():
    """Load a specific IFC file"""
    try:
        data = request.json
        file_path = data.get("file_path")
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
            
        result = bim_agent_manager.load_ifc_file(file_path)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error loading IFC file: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500