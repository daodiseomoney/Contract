import logging
from flask import Blueprint, jsonify, request
from src.gateways.kepler_gateway import KeplerGateway

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
account_bp = Blueprint("account", __name__, url_prefix="/api")

# Initialize kepler gateway with network configuration
network_config = {
    "chain_id": "odiseotestnet_1234-1",
    "rpc_url": "https://odiseo.test.rpc.nodeshub.online",
    "api_url": "https://odiseo.test.api.nodeshub.online"
}
kepler_gateway = KeplerGateway(network_config)


@account_bp.route("/account", methods=["GET"])
def get_account():
    """Get current user account information"""
    # In a real implementation, this would retrieve user data from database
    # based on authenticated session
    mock_account = {
        "username": "demo_user",
        "wallet_address": request.args.get("address", ""),
        "role": "admin",
        "permissions": ["upload", "view", "edit", "delete"],
    }

    return jsonify(mock_account)


@account_bp.route("/account/wallet", methods=["POST"])
def connect_wallet():
    """Connect a wallet address to the user account"""
    try:
        data = request.json

        if not data or "address" not in data:
            return jsonify({"error": "Wallet address is required"}), 400

        address = data["address"]

        # In a real implementation, this would update the user's wallet in the database
        logger.debug(f"Wallet connected: {address}")

        return jsonify(
            {
                "success": True,
                "message": "Wallet connected successfully",
                "address": address,
            }
        )
    except Exception as e:
        logger.error(f"Error connecting wallet: {str(e)}")
        return jsonify({"error": str(e)}), 500


@account_bp.route("/network-config", methods=["GET"])
def get_network_config():
    """Get Cosmos network configuration for Keplr wallet integration"""
    try:
        # Get network configuration from the gateway
        config = kepler_gateway.get_network_config()
        logger.debug(f"Returning network config: {config}")
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting network config: {str(e)}")
        return jsonify({"error": str(e)}), 500
