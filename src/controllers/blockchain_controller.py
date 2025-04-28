"""
Blockchain Controller for handling blockchain-related API endpoints
"""

import os
import json
import logging
import hashlib
import time
from flask import Blueprint, request, jsonify, current_app, session, abort

from src.services.blockchain_service import BlockchainService
from src.security_utils import secure_endpoint, verify_wallet_ownership

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api')

# Initialize services
blockchain_service = BlockchainService()

@blockchain_bp.route('/account', methods=['GET'])
@secure_endpoint
def get_account():
    """Get account information for a wallet address"""
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({'error': 'Address parameter is required'}), 400
        
        # Security: Verify wallet ownership if not in debug mode
        # In production, this will reject requests for addresses not owned by the user
        if not current_app.debug:
            try:
                verify_wallet_ownership(address)
            except Exception as auth_error:
                logger.warning(f"Unauthorized wallet access attempt for address: {address}")
                return jsonify({'error': 'Unauthorized access to wallet data'}), 403
        
        # Get account information from the blockchain
        account_info = blockchain_service.pingpub_gateway.get_account_info(address)
        
        # Security: Log access timestamp
        logger.info(f"Account information retrieved for: {address} at {time.time()}")
        
        return jsonify(account_info), 200
    
    except Exception as e:
        logger.error(f"Error in get_account: {str(e)}")
        # Security: Don't expose detailed error message in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to retrieve account information'}), 500

@blockchain_bp.route('/broadcast', methods=['POST'])
@secure_endpoint
def broadcast_transaction():
    """Broadcast a signed transaction to the blockchain"""
    try:
        # Security: Get and validate request data
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Security: Validate transaction format
        if not isinstance(data, dict):
            return jsonify({'error': 'Transaction data must be a JSON object'}), 400
            
        # Security: Basic transaction validation
        if 'tx' not in data:
            return jsonify({'error': 'Missing tx field in transaction data'}), 400
            
        tx_data = data.get('tx', {})
        if not tx_data.get('signatures'):
            return jsonify({'error': 'Missing signatures in transaction data'}), 400
        
        # Security: Check for valid sender address if available
        from_address = None
        try:
            # Try to extract sender address from transaction
            msgs = tx_data.get('msg', [])
            if msgs and len(msgs) > 0:
                from_address = msgs[0].get('value', {}).get('fromAddress') or msgs[0].get('value', {}).get('from_address')
                
                # Verify wallet ownership in production
                if from_address and not current_app.debug:
                    try:
                        verify_wallet_ownership(from_address)
                    except Exception:
                        logger.warning(f"Unauthorized transaction broadcast attempt for address: {from_address}")
                        return jsonify({'error': 'Unauthorized transaction broadcast'}), 403
        except Exception as e:
            logger.warning(f"Failed to extract sender address: {str(e)}")
            # Continue processing as this is just an additional security check
            
        # Security: Rate limiting for transaction broadcasts
        # Implemented via @secure_endpoint decorator
        
        # Broadcast the transaction
        result = blockchain_service.broadcast_signed_transaction(data)
        
        # Security: Enhanced logging
        tx_hash = result.get('transaction_hash')
        logger.info(f"Transaction broadcast: {tx_hash} by {from_address or 'unknown'} at {time.time()}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in broadcast_transaction: {str(e)}")
        # Security: Don't expose internal errors in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to broadcast transaction'}), 500

@blockchain_bp.route('/verify/<tx_hash>', methods=['GET'])
@secure_endpoint
def verify_transaction(tx_hash):
    """Verify a transaction on the blockchain with enhanced security"""
    try:
        # Security: Validate transaction hash format
        if not tx_hash or len(tx_hash) < 10:
            return jsonify({'error': 'Invalid transaction hash'}), 400
            
        # Get expected content hash if available
        content_hash = request.args.get('content_hash')
        user_address = request.args.get('address')
        
        # Create complete transaction data for enhanced verification
        transaction_data = {
            'transaction_hash': tx_hash,
            'content_hash': content_hash,
            'user_address': user_address
        }
        
        # Basic transaction verification
        result = blockchain_service.verify_transaction(tx_hash)
        
        # Enhanced security verification if content hash provided
        if content_hash:
            # Verify content hash matches transaction memo
            memo = result.get('status', {}).get('memo', '')
            
            # Try to extract memo data
            memo_data = {}
            try:
                # Try parsing as JSON
                memo_data = json.loads(memo)
            except:
                # Try legacy format (key:value|key:value)
                if '|' in memo and ':' in memo:
                    pairs = memo.split('|')
                    for pair in pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            memo_data[key.strip()] = value.strip()
                # Try simple format (id:hash:role)
                elif ':' in memo:
                    parts = memo.split(':')
                    if len(parts) >= 2:
                        memo_data['hash'] = parts[1]
            
            # Verify hash if found in memo data
            memo_hash = memo_data.get('hash')
            if memo_hash and memo_hash != content_hash:
                logger.warning(f"Content hash mismatch: {memo_hash} != {content_hash}")
                result['hash_verified'] = False
                result['security_warning'] = 'Content hash mismatch'
            else:
                result['hash_verified'] = bool(memo_hash and memo_hash == content_hash)
        
        # Security: Add verification timestamp
        result['verification_timestamp'] = time.time()
        
        # Security: Enhanced logging
        logger.info(f"Transaction verification: {tx_hash} at {time.time()}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in verify_transaction: {str(e)}")
        # Security: Don't expose internal errors in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to verify transaction'}, {'verified': False}), 500

@blockchain_bp.route('/stats', methods=['GET'])
@secure_endpoint
def get_blockchain_stats():
    """Get blockchain statistics for the dashboard"""
    try:
        # Get stats from blockchain service or use cached data
        stats = blockchain_service.get_dashboard_stats()
        
        # Security: Add timestamp for freshness verification
        stats['timestamp'] = time.time()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error in get_blockchain_stats: {str(e)}")
        # Security: Don't expose internal errors in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to retrieve blockchain statistics'}), 500

@blockchain_bp.route('/asset-distribution', methods=['GET'])
@secure_endpoint
def get_asset_distribution():
    """Get asset distribution data for dashboard charts"""
    try:
        # Get asset distribution from blockchain service
        distribution = blockchain_service.get_asset_distribution()
        
        # Security: Add timestamp for freshness verification
        distribution['timestamp'] = time.time()
        
        return jsonify(distribution), 200
        
    except Exception as e:
        logger.error(f"Error in get_asset_distribution: {str(e)}")
        # Security: Don't expose internal errors in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to retrieve asset distribution data'}), 500

@blockchain_bp.route('/stakeholder-distribution', methods=['GET'])
@secure_endpoint
def get_stakeholder_distribution():
    """Get stakeholder distribution data for dashboard charts"""
    try:
        # Get stakeholder distribution from blockchain service
        distribution = blockchain_service.get_stakeholder_distribution()
        
        # Security: Add timestamp for freshness verification
        distribution['timestamp'] = time.time()
        
        return jsonify(distribution), 200
        
    except Exception as e:
        logger.error(f"Error in get_stakeholder_distribution: {str(e)}")
        # Security: Don't expose internal errors in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to retrieve stakeholder distribution data'}), 500

@blockchain_bp.route('/validators', methods=['GET'])
@secure_endpoint
def get_validators():
    """Get list of active validators"""
    try:
        # Get validators with caching for rate limiting
        validators = blockchain_service.get_validators()
        
        # Security: Add timestamp for freshness verification
        response_data = {
            'validators': validators,
            'timestamp': time.time(),
            'count': len(validators)
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Error in get_validators: {str(e)}")
        # Security: Don't expose internal errors in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to retrieve validators'}), 500

@blockchain_bp.route('/prepare-upload', methods=['POST'])
@secure_endpoint
def prepare_upload():
    """Prepare a transaction for uploading an IFC file hash"""
    try:
        # Check if file and address are provided
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        user_address = request.form.get('address')
        if not user_address:
            return jsonify({'error': 'User address is required'}), 400
        
        # Security: Verify wallet ownership if not in debug mode
        if not current_app.debug:
            try:
                verify_wallet_ownership(user_address)
            except Exception as auth_error:
                logger.warning(f"Unauthorized file upload attempt for address: {user_address}")
                return jsonify({'error': 'Unauthorized wallet access'}), 403
        
        # Get file data
        file = request.files['file']
        
        # Security: Validate file extension
        if not file.filename or '.' not in file.filename:
            return jsonify({'error': 'Invalid filename'}), 400
            
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in ['ifc']:
            return jsonify({'error': 'Only IFC files are allowed'}), 400
        
        # Security: Limit file size (100MB)
        file_data = file.read()
        if len(file_data) > 100 * 1024 * 1024:  # 100MB
            return jsonify({'error': 'File too large (max 100MB)'}), 400
            
        # Security: Validate IFC file format
        try:
            from src.security_utils import validate_ifc_file
            validate_ifc_file(file_data)
        except ValueError as validation_error:
            logger.warning(f"Invalid IFC file uploaded: {str(validation_error)}")
            return jsonify({'error': f'Invalid IFC file: {str(validation_error)}'}), 400
        
        # Get metadata if provided
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata_str = request.form.get('metadata')
                # Security: Limit metadata size
                if len(metadata_str) > 10 * 1024:  # 10KB
                    return jsonify({'error': 'Metadata too large'}), 400
                    
                metadata = json.loads(metadata_str)
                
                # Security: Validate metadata structure
                if not isinstance(metadata, dict):
                    return jsonify({'error': 'Metadata must be a JSON object'}), 400
                    
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid metadata format'}), 400
        
        # Add filename and timestamp to metadata
        metadata['filename'] = file.filename
        metadata['upload_timestamp'] = time.time()
        metadata['file_size'] = len(file_data)
        
        # Security: Add hash verification to metadata
        from src.security_utils import secure_hash_file
        file_hash = secure_hash_file(file_data)
        metadata['file_hash'] = file_hash
        
        # Process the file upload
        result = blockchain_service.process_ifc_upload(file_data, user_address, metadata)
        
        # Security: Verify the returned content hash matches our calculated hash
        if result.get('content_hash') != file_hash:
            logger.error(f"Hash mismatch: {result.get('content_hash')} != {file_hash}")
            return jsonify({'error': 'Security validation failed: hash mismatch'}), 500
        
        # Security: Log the upload
        logger.info(f"IFC file uploaded: {file.filename} by {user_address} at {time.time()}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in prepare_upload: {str(e)}")
        # Security: Don't expose detailed error message in production
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to process upload'}), 500