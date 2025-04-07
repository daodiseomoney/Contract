"""
BIM Agent Controller for handling AI-related routes
"""

import logging
from flask import Blueprint, jsonify, request

from src.bim.bim_agent import BIMAgentManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a Flask Blueprint
bim_agent_bp = Blueprint('bim_agent', __name__, url_prefix='/api/bim-agent')

# Initialize the BIM Agent Manager
bim_agent_manager = BIMAgentManager()

@bim_agent_bp.route('/chat', methods=['POST'])
def chat():
    """
    Process a chat message and return the AI response
    Expects JSON: {"message": "user message here"}
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'message': 'Message field is required'
        }), 400
    
    message = data['message']
    
    # Log the incoming message
    logger.debug(f"Received chat message: {message}")
    
    # Process the message
    result = bim_agent_manager.process_message(message)
    
    # Return the result
    return jsonify(result)

@bim_agent_bp.route('/toggle-enhanced', methods=['POST'])
def toggle_enhanced():
    """
    Toggle enhanced AI mode
    Expects JSON: {"enabled": true/false}
    """
    data = request.get_json()
    
    if not data or 'enabled' not in data:
        return jsonify({
            'success': False,
            'message': 'Enabled field is required'
        }), 400
    
    enabled = data['enabled']
    
    # Log the toggle request
    logger.debug(f"Toggling enhanced mode: {enabled}")
    
    # Toggle enhanced mode
    result = bim_agent_manager.toggle_enhanced_mode(enabled)
    
    # Return the result
    return jsonify(result)

@bim_agent_bp.route('/enhanced-status', methods=['GET'])
def enhanced_status():
    """Get the current status of enhanced mode"""
    status = bim_agent_manager.get_enhanced_mode()
    
    return jsonify({
        'success': True,
        'enhanced_mode': status
    })

@bim_agent_bp.route('/building-data', methods=['GET'])
def building_data():
    """Get building data for the UI"""
    data = bim_agent_manager.get_building_data()
    
    return jsonify({
        'success': True,
        'data': data
    })

@bim_agent_bp.route('/element/<element_id>', methods=['GET'])
def get_element(element_id):
    """Get element details by ID"""
    result = bim_agent_manager.get_element_by_id(element_id)
    
    return jsonify(result)
