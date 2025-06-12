"""
Consolidated Blockchain Controller for DAODISEO Platform
Combines blockchain, RPC, transaction, and proxy functionality
"""

import os
import json
import logging
import hashlib
import time
import uuid
import requests
from flask import Blueprint, request, jsonify, current_app, session, abort

from src.services.blockchain_service import BlockchainService
from src.services.rpc_service import DaodiseoRPCService
from src.services.transaction_service import TransactionService
from src.gateways.consolidated_blockchain_gateway import ConsolidatedBlockchainGateway, KeplerSignatureRole
from src.security_utils import secure_endpoint, verify_wallet_ownership

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api/blockchain')

# Initialize services
blockchain_service = BlockchainService()
rpc_service = DaodiseoRPCService()
transaction_service = TransactionService()

network_config = {
    "chain_id": "ithaca-1",
    "rpc_url": "https://odiseo.test.rpc.nodeshub.online",
    "api_url": "https://odiseo.test.api.nodeshub.online"
}
kepler_gateway = ConsolidatedBlockchainGateway()

# =============================================================================
# ACCOUNT MANAGEMENT
# =============================================================================

@blockchain_bp.route('/account', methods=['GET'])
@secure_endpoint
def get_account():
    """Get account information for a wallet address"""
    try:
        address = request.args.get('address')
        if not address:
            return jsonify({'error': 'Address parameter is required'}), 400
        
        if not current_app.debug:
            try:
                verify_wallet_ownership(address)
            except Exception as auth_error:
                logger.warning(f"Unauthorized wallet access attempt for address: {address}")
                return jsonify({'error': 'Unauthorized access to wallet data'}), 403
        
        account_info = blockchain_service.blockchain_gateway.get_account_info(address)
        logger.info(f"Account information retrieved for: {address} at {time.time()}")
        
        return jsonify(account_info), 200
    
    except Exception as e:
        logger.error(f"Error in get_account: {str(e)}")
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to retrieve account information'}), 500

# =============================================================================
# TRANSACTION MANAGEMENT
# =============================================================================

@blockchain_bp.route('/transactions', methods=['GET'])
@secure_endpoint
def get_transactions():
    """Retrieve blockchain transactions"""
    try:
        address = request.args.get("address")
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 30, type=int)
        
        if address:
            logger.debug(f"Querying transactions for address: {address}")
            result = rpc_service.search_transactions(
                query=f'message.sender="{address}"',
                page=page,
                per_page=per_page
            )
            return jsonify(result)
        else:
            # Get general transaction data
            result = rpc_service.search_transactions(
                query='tx.height>0',
                page=page,
                per_page=per_page
            )
            return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error querying transactions: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch transactions",
            "details": str(e)
        }), 500

@blockchain_bp.route('/transactions/<tx_id>', methods=['GET'])
@secure_endpoint
def get_transaction(tx_id):
    """Retrieve a specific transaction by ID"""
    try:
        logger.debug(f"Getting transaction details for: {tx_id}")
        
        # Query blockchain for transaction details
        result = rpc_service.get_transaction(tx_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching transaction {tx_id}: {str(e)}")
        return jsonify({"error": "Transaction not found"}), 404

@blockchain_bp.route('/transactions/sign', methods=['POST'])
@secure_endpoint
def sign_transaction():
    """Sign a transaction with a wallet"""
    try:
        data = request.json
        logger.debug(f"Received data for signing: {data}")

        if not data:
            return jsonify({"error": "Transaction data is required"}), 400

        if "wallet_address" not in data:
            return jsonify({"error": "Wallet address is required"}), 400
        
        wallet_address = data.get("wallet_address")
        transaction_id = data.get("transaction_id", f"tx-{uuid.uuid4().hex[:8]}")
        content_hash = data.get("content_hash", "")
        role = data.get("role", "owner")

        logger.debug(f"Signing transaction {transaction_id} for {wallet_address} as {role}")

        # Use Kepler gateway for signing
        signature_role = KeplerSignatureRole(role)
        signature_result = kepler_gateway.sign_transaction(
            wallet_address, content_hash, transaction_id, signature_role
        )

        if signature_result.get("success"):
            logger.info(f"Transaction {transaction_id} signed successfully")
            return jsonify({
                "success": True,
                "transaction_id": transaction_id,
                "signature": signature_result.get("signature"),
                "signed_at": signature_result.get("timestamp"),
                "role": role
            })
        else:
            logger.error(f"Failed to sign transaction: {signature_result.get('error')}")
            return jsonify({
                "success": False,
                "error": signature_result.get("error", "Unknown signing error")
            }), 400

    except Exception as e:
        logger.error(f"Error in sign_transaction: {str(e)}")
        return jsonify({"error": f"Signing failed: {str(e)}"}), 500

@blockchain_bp.route('/broadcast', methods=['POST'])
@secure_endpoint
def broadcast_transaction():
    """Broadcast a signed transaction to the blockchain"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not isinstance(data, dict):
            return jsonify({'error': 'Transaction data must be a JSON object'}), 400
            
        if 'tx' not in data:
            return jsonify({'error': 'Missing tx field in transaction data'}), 400
            
        tx_data = data.get('tx', {})
        if not tx_data.get('signatures'):
            return jsonify({'error': 'Missing signatures in transaction data'}), 400
        
        # Extract sender address for security verification
        from_address = None
        try:
            msgs = tx_data.get('msg', [])
            if msgs and len(msgs) > 0:
                from_address = msgs[0].get('value', {}).get('fromAddress') or msgs[0].get('value', {}).get('from_address')
                
                if from_address and not current_app.debug:
                    try:
                        verify_wallet_ownership(from_address)
                    except Exception:
                        logger.warning(f"Unauthorized transaction broadcast attempt for address: {from_address}")
                        return jsonify({'error': 'Unauthorized transaction broadcast'}), 403
        except Exception as e:
            logger.warning(f"Failed to extract sender address: {str(e)}")
        
        # Broadcast the transaction
        result = blockchain_service.broadcast_signed_transaction(data)
        
        tx_hash = result.get('transaction_hash')
        logger.info(f"Transaction broadcast: {tx_hash} by {from_address or 'unknown'} at {time.time()}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in broadcast_transaction: {str(e)}")
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to broadcast transaction'}), 500

@blockchain_bp.route('/verify/<tx_hash>', methods=['GET'])
@secure_endpoint
def verify_transaction(tx_hash):
    """Verify a transaction on the blockchain"""
    try:
        if not tx_hash or len(tx_hash) < 10:
            return jsonify({'error': 'Invalid transaction hash'}), 400
            
        content_hash = request.args.get('content_hash')
        user_address = request.args.get('address')
        
        result = blockchain_service.verify_transaction(tx_hash)
        
        # Enhanced verification if content hash provided
        if content_hash:
            memo = result.get('status', {}).get('memo', '')
            memo_data = {}
            try:
                memo_data = json.loads(memo)
            except:
                if '|' in memo and ':' in memo:
                    pairs = memo.split('|')
                    for pair in pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            memo_data[key.strip()] = value.strip()
                elif ':' in memo:
                    parts = memo.split(':')
                    if len(parts) >= 2:
                        memo_data['hash'] = parts[1]
            
            memo_hash = memo_data.get('hash')
            if memo_hash and memo_hash != content_hash:
                logger.warning(f"Content hash mismatch: {memo_hash} != {content_hash}")
                result['hash_verified'] = False
                result['security_warning'] = 'Content hash mismatch'
            else:
                result['hash_verified'] = bool(memo_hash and memo_hash == content_hash)
        
        result['verification_timestamp'] = time.time()
        logger.info(f"Transaction verification: {tx_hash} at {time.time()}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in verify_transaction: {str(e)}")
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Failed to verify transaction'}, {'verified': False}), 500

# =============================================================================
# RPC ENDPOINTS
# =============================================================================

@blockchain_bp.route('/rpc/network-status', methods=['GET'])
@secure_endpoint
def get_network_status():
    """Get current network status and health from RPC"""
    try:
        result = rpc_service.get_network_status()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RPC network status error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch network status from RPC",
            "details": str(e)
        }), 500

@blockchain_bp.route('/rpc/validators', methods=['GET'])
@secure_endpoint
def get_validators():
    """Get current validators from RPC"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        
        result = rpc_service.get_validators(page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        logger.error(f"RPC validators error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch validators from RPC",
            "details": str(e)
        }), 500

@blockchain_bp.route('/rpc/latest-block', methods=['GET'])
@secure_endpoint
def get_latest_block():
    """Get latest block information from RPC"""
    try:
        result = rpc_service.get_latest_block()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RPC latest block error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch latest block from RPC",
            "details": str(e)
        }), 500

@blockchain_bp.route('/rpc/network-info', methods=['GET'])
@secure_endpoint
def get_network_info():
    """Get network peer information from RPC"""
    try:
        result = rpc_service.get_network_info()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RPC network info error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch network info from RPC",
            "details": str(e)
        }), 500

@blockchain_bp.route('/rpc/consensus-state', methods=['GET'])
@secure_endpoint
def get_consensus_state():
    """Get consensus state from RPC"""
    try:
        result = rpc_service.get_consensus_state()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RPC consensus state error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch consensus state from RPC",
            "details": str(e)
        }), 500

# =============================================================================
# PROXY ENDPOINTS
# =============================================================================

@blockchain_bp.route('/proxy/rpc', methods=['POST', 'OPTIONS'])
@secure_endpoint
def rpc_proxy():
    """Proxy blockchain RPC requests to bypass CORS restrictions"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        rpc_data = request.get_json()
        if not rpc_data:
            return jsonify({"error": "No RPC data provided"}), 400
        
        required_fields = ["jsonrpc", "method", "id"]
        for field in required_fields:
            if field not in rpc_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        rpc_endpoints = [
            "https://testnet-rpc.daodiseo.chaintools.tech",
            "https://rpc.odiseotestnet.chaintools.tech",
            "https://testnet-rpc.odiseo.nodeshub.online"
        ]
        
        logger.debug(f"Proxying RPC request: {rpc_data.get('method')}")
        
        last_error = None
        for rpc_url in rpc_endpoints:
            try:
                logger.debug(f"Attempting RPC call to: {rpc_url}")
                
                response = requests.post(
                    rpc_url,
                    json=rpc_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'DAODISEO-Platform/1.0'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"Successful RPC response from {rpc_url}")
                    
                    json_response = jsonify(result)
                    json_response.headers.add('Access-Control-Allow-Origin', '*')
                    return json_response
                
                else:
                    logger.warning(f"RPC endpoint {rpc_url} returned {response.status_code}")
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.RequestException as e:
                logger.warning(f"RPC endpoint {rpc_url} failed: {str(e)}")
                last_error = str(e)
                continue
        
        logger.error(f"All RPC endpoints failed. Last error: {last_error}")
        return jsonify({
            "error": "All blockchain RPC endpoints are currently unavailable",
            "details": last_error
        }), 503
        
    except Exception as e:
        logger.error(f"RPC proxy error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500

@blockchain_bp.route('/proxy/broadcast', methods=['POST', 'OPTIONS'])
@secure_endpoint
def broadcast_proxy():
    """Proxy transaction broadcast requests with proper format handling"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        tx_data = request.get_json()
        if not tx_data:
            return jsonify({"error": "No transaction data provided"}), 400
        
        logger.debug(f"Proxying transaction broadcast: {json.dumps(tx_data, indent=2)}")
        
        rest_endpoints = [
            "https://testnet-api.daodiseo.chaintools.tech/txs",
            "https://api.odiseotestnet.chaintools.tech/txs",
            "https://testnet-api.odiseo.nodeshub.online/txs"
        ]
        
        rpc_endpoints = [
            "https://testnet-rpc.daodiseo.chaintools.tech/broadcast_tx_sync",
            "https://rpc.odiseotestnet.chaintools.tech/broadcast_tx_sync",
            "https://testnet-rpc.odiseo.nodeshub.online/broadcast_tx_sync"
        ]
        
        # Try REST API endpoints first
        for endpoint in rest_endpoints:
            try:
                logger.debug(f"Attempting broadcast to REST endpoint: {endpoint}")
                
                response = requests.post(
                    endpoint,
                    json=tx_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'DAODISEO-Platform/1.0'
                    },
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"Successful broadcast via REST: {endpoint}")
                    
                    json_response = jsonify(result)
                    json_response.headers.add('Access-Control-Allow-Origin', '*')
                    return json_response
                    
            except requests.RequestException as e:
                logger.warning(f"REST endpoint {endpoint} failed: {str(e)}")
                continue
        
        # Try RPC endpoints as fallback
        for endpoint in rpc_endpoints:
            try:
                logger.debug(f"Attempting broadcast to RPC endpoint: {endpoint}")
                
                rpc_data = {
                    "jsonrpc": "2.0",
                    "method": "broadcast_tx_sync",
                    "params": {"tx": tx_data.get("tx_bytes", "")},
                    "id": 1
                }
                
                response = requests.post(
                    endpoint,
                    json=rpc_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'DAODISEO-Platform/1.0'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successful broadcast via RPC: {endpoint}")
                    
                    json_response = jsonify(result)
                    json_response.headers.add('Access-Control-Allow-Origin', '*')
                    return json_response
                    
            except requests.RequestException as e:
                logger.warning(f"RPC endpoint {endpoint} failed: {str(e)}")
                continue
        
        return jsonify({
            "error": "All broadcast endpoints are currently unavailable"
        }), 503
        
    except Exception as e:
        logger.error(f"Broadcast proxy error: {str(e)}")
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500

# =============================================================================
# DASHBOARD STATISTICS
# =============================================================================

@blockchain_bp.route('/stats', methods=['GET'])
@secure_endpoint
def get_blockchain_stats():
    """Get blockchain statistics for the dashboard"""
    try:
        stats = blockchain_service.get_dashboard_stats()
        stats['timestamp'] = time.time()
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error in get_blockchain_stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve blockchain statistics'}), 500

@blockchain_bp.route('/asset-distribution', methods=['GET'])
@secure_endpoint
def get_asset_distribution():
    """Get asset distribution data for dashboard charts"""
    try:
        distribution = blockchain_service.get_asset_distribution()
        return jsonify(distribution), 200
    
    except Exception as e:
        logger.error(f"Error in get_asset_distribution: {str(e)}")
        return jsonify({'error': 'Failed to retrieve asset distribution'}), 500

@blockchain_bp.route('/stakeholder-distribution', methods=['GET'])
@secure_endpoint
def get_stakeholder_distribution():
    """Get stakeholder distribution data for dashboard charts"""
    try:
        distribution = blockchain_service.get_stakeholder_distribution()
        return jsonify(distribution), 200
    
    except Exception as e:
        logger.error(f"Error in get_stakeholder_distribution: {str(e)}")
        return jsonify({'error': 'Failed to retrieve stakeholder distribution'}), 500

@blockchain_bp.route('/network-stats', methods=['GET'])
@secure_endpoint
def get_network_stats():
    """Get comprehensive network statistics"""
    try:
        stats = blockchain_service.get_network_stats()
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error in get_network_stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve network statistics'}), 500

@blockchain_bp.route('/token-price', methods=['GET'])
@secure_endpoint
def get_token_price():
    """Get current ODIS token price and market data"""
    try:
        price_data = blockchain_service.get_token_price()
        return jsonify(price_data), 200
    
    except Exception as e:
        logger.error(f"Error in get_token_price: {str(e)}")
        return jsonify({'error': 'Failed to retrieve token price'}), 500

@blockchain_bp.route('/recent-transactions', methods=['GET'])
@secure_endpoint
def get_recent_transactions():
    """Get recent blockchain transactions"""
    try:
        limit = request.args.get('limit', 10, type=int)
        transactions = blockchain_service.get_recent_transactions(limit=limit)
        return jsonify(transactions), 200
    
    except Exception as e:
        logger.error(f"Error in get_recent_transactions: {str(e)}")
        return jsonify({'error': 'Failed to retrieve recent transactions'}), 500

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

@blockchain_bp.route('/prepare-upload', methods=['POST'])
@secure_endpoint
def prepare_upload():
    """Prepare a transaction for uploading an IFC file hash"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        ifc_hash = data.get('ifc_hash')
        if not ifc_hash:
            return jsonify({'error': 'IFC hash is required'}), 400
        
        prepared_tx = blockchain_service.prepare_upload_transaction(ifc_hash)
        return jsonify(prepared_tx), 200
    
    except Exception as e:
        logger.error(f"Error in prepare_upload: {str(e)}")
        return jsonify({'error': 'Failed to prepare upload transaction'}), 500

@blockchain_bp.route('/proxy/health', methods=['GET'])
def proxy_health():
    """Check the health of blockchain proxy service"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "service": "blockchain-proxy"
    }), 200

def register_blockchain_routes(app):
    """Register consolidated blockchain routes with the Flask app"""
    app.register_blueprint(blockchain_bp)
    logger.info("Consolidated blockchain routes registered successfully")