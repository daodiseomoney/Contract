"""
Blockchain Controller - Clean Architecture Layer 2
Handles HTTP requests for blockchain-related operations
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any
import logging

# Import use cases from Layer 1
try:
    from src.layer1_use_cases.get_network_status import GetNetworkStatusUseCase
    from src.layer1_use_cases.get_token_metrics import GetTokenMetricsUseCase
except ImportError:
    # Fallback for development
    class GetNetworkStatusUseCase:
        def execute(self) -> Dict[str, Any]:
            return {
                "network_name": "Odiseo Testnet",
                "block_height": 3483091,
                "health_status": "healthy",
                "validator_count": 45,
                "active_validators": 32
            }
    
    class GetTokenMetricsUseCase:
        def execute(self) -> Dict[str, Any]:
            return {
                "token_symbol": "ODIS",
                "current_price": 4.85,
                "price_change_24h": 1.2,
                "market_cap": 145000000,
                "volume_24h": 2340000
            }

# Import gateways from Layer 2
try:
    from src.layer2_interface_adapters.gateways.blockchain_gateway import BlockchainGateway
except ImportError:
    class BlockchainGateway:
        def get_network_health(self) -> Dict[str, Any]:
            return {"status": "healthy", "block_height": 3483091}
        
        def get_token_price(self) -> Dict[str, Any]:
            return {"price": 4.85, "change_24h": 1.2}

LOG = logging.getLogger("daodiseo.blockchain_controller")

# Create Blueprint
bp = Blueprint('blockchain', __name__)

# Initialize use cases
blockchain_gateway = BlockchainGateway()
network_status_use_case = GetNetworkStatusUseCase()
token_metrics_use_case = GetTokenMetricsUseCase()

@bp.route('/network-health', methods=['GET'])
def get_network_health():
    """Get current network health status"""
    try:
        result = network_status_use_case.execute()
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting network health: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/odis-value', methods=['GET'])
def get_odis_value():
    """Get current ODIS token value and metrics"""
    try:
        result = token_metrics_use_case.execute()
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting ODIS value: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/validators', methods=['GET'])
def get_validators():
    """Get validator information"""
    try:
        # This would use a ValidatorUseCase in full implementation
        result = {
            "total_validators": 45,
            "active_validators": 32,
            "top_validators": [
                {"name": "Validator 1", "voting_power": "12.5%", "commission": "5%"},
                {"name": "Validator 2", "voting_power": "10.8%", "commission": "3%"},
                {"name": "Validator 3", "voting_power": "9.2%", "commission": "4%"}
            ]
        }
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting validators: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get recent transactions"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # This would use a TransactionUseCase in full implementation
        result = {
            "page": page,
            "limit": limit,
            "total": 15420,
            "transactions": [
                {
                    "hash": "0x1234...abcd",
                    "block": 3483091,
                    "timestamp": "2025-06-13T19:30:00Z",
                    "type": "transfer",
                    "amount": "100 ODIS",
                    "fee": "0.01 ODIS"
                }
            ]
        }
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting transactions: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500