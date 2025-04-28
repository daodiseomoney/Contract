"""
Blockchain Controller for handling blockchain-related API endpoints
"""

import os
import json
import logging
import hashlib
from flask import Blueprint, request, jsonify, current_app

from src.services.blockchain_service import BlockchainService

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api')

# Initialize services
blockchain_service = BlockchainService()

@blockchain_bp.route('/account', methods=['GET'])
def get_account():
    """Get account information for a wallet address"""
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({'error': 'Address parameter is required'}), 400
        
        # Get account information from the blockchain
        account_info = blockchain_service.pingpub_gateway.get_account_info(address)
        
        return jsonify(account_info), 200
    
    except Exception as e:
        logger.error(f"Error in get_account: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blockchain_bp.route('/broadcast', methods=['POST'])
def broadcast_transaction():
    """Broadcast a signed transaction to the blockchain"""
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Broadcast the transaction
        result = blockchain_service.broadcast_signed_transaction(data)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in broadcast_transaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blockchain_bp.route('/verify/<tx_hash>', methods=['GET'])
def verify_transaction(tx_hash):
    """Verify a transaction on the blockchain"""
    try:
        # Verify the transaction
        result = blockchain_service.verify_transaction(tx_hash)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in verify_transaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blockchain_bp.route('/validators', methods=['GET'])
def get_validators():
    """Get list of active validators"""
    try:
        # Get validators
        validators = blockchain_service.get_validators()
        
        return jsonify(validators), 200
    
    except Exception as e:
        logger.error(f"Error in get_validators: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blockchain_bp.route('/prepare-upload', methods=['POST'])
def prepare_upload():
    """Prepare a transaction for uploading an IFC file hash"""
    try:
        # Check if file and address are provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        user_address = request.form.get('address')
        if not user_address:
            return jsonify({'error': 'User address is required'}), 400
        
        # Get file data
        file = request.files['file']
        file_data = file.read()
        
        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form.get('metadata'))
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid metadata format'}), 400
        
        # Add filename to metadata
        metadata['filename'] = file.filename
        
        # Process the file upload
        result = blockchain_service.process_ifc_upload(file_data, user_address, metadata)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in prepare_upload: {str(e)}")
        return jsonify({'error': str(e)}), 500