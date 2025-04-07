"""
BIM Agent Controller
Provides API routes for interacting with the OpenAI-powered BIM assistant
"""
import json
import os
import logging
from flask import Blueprint, request, jsonify, current_app
from src.bim.bim_agent import process_message_sync

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Blueprint
bim_agent_bp = Blueprint('bim_agent', __name__, url_prefix='/api/bim-agent')

@bim_agent_bp.route('/query', methods=['POST'])
def query_bim_agent():
    """Process a query to the BIM agent using OpenAI"""
    # Get request data
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    query = data['query']
    logger.debug(f"Received query: {query}")
    
    try:
        # Get API key from environment or use a default for testing
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            logger.warning("No OpenAI API key found in environment variables")
            return jsonify({
                'error': 'OpenAI API key not configured',
                'response': 'I cannot process your request at the moment as my API connection is not configured.',
                'stakeholderGroup': None,
                'metadata': {'error': 'Missing API key'}
            }), 500
        
        # Process the message
        result = process_message_sync(query, api_key)
        logger.debug(f"BIM Agent response: {result}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing BIM agent query: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'response': 'Sorry, I encountered an error while processing your request.',
            'stakeholderGroup': None,
            'metadata': {'error': str(e)}
        }), 500

@bim_agent_bp.route('/status', methods=['GET'])
def check_bim_agent_status():
    """Check if the BIM agent is properly configured"""
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        logger.warning("No OpenAI API key found in environment variables")
        return jsonify({
            'available': False,
            'message': 'OpenAI API key not configured'
        })
    
    return jsonify({
        'available': True,
        'message': 'BIM Agent is configured and ready'
    })
