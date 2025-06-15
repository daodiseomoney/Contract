import logging
from flask import Blueprint, jsonify, request
from src.layer3_interface_adapters.gateways.consolidated_blockchain_gateway import ConsolidatedBlockchainGateway, NetworkConfig

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
account_bp = Blueprint("account", __name__, url_prefix="/api")

# Initialize consolidated blockchain gateway
network_config = NetworkConfig(
    chain_id="ithaca-1",
    rpc_url="https://testnet-rpc.daodiseo.chaintools.tech",
    api_url="https://testnet-api.daodiseo.chaintools.tech"
)
blockchain_gateway = ConsolidatedBlockchainGateway(network_config)




@account_bp.route("/account", methods=["GET"])
def get_account():
    """Get current user account information"""
    # Get wallet address from query parameters
    wallet_address = request.args.get("address", "")
    
    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400
    
    try:
        # Get real account information from the blockchain
        account_info = blockchain_gateway.get_account_info(wallet_address)
        
        # Add additional user information
        # TODO(DDS_TEAM): Replace with real database lookup for user profile
        account_info.update({
            "username": f"user_{wallet_address[:8]}",  # Generated username based on address
            "role": "user",
            "permissions": ["upload", "view"],
        })
        
        logger.debug(f"Returning account info for {wallet_address}: {account_info}")
        return jsonify(account_info)
    except Exception as e:
        logger.error(f"Error retrieving account info: {str(e)}")
        return jsonify({"error": f"Failed to retrieve account info: {str(e)}"}), 500


@account_bp.route("/account/wallet", methods=["POST"])
def connect_wallet():
    """Connect a wallet address to the user account"""
    try:
        data = request.json

        if not data or "address" not in data:
            return jsonify({"error": "Wallet address is required"}), 400

        address = data["address"]

        # Store the connected address locally (note: address stored in session)
        # blockchain_gateway.connected_address = address
        logger.info(f"Wallet connected: {address}")

        # Get account info from blockchain
        try:
            # Get real account information from the blockchain
            account_info = blockchain_gateway.get_account_info(address)
            logger.debug(f"Retrieved account info: {account_info}")
        except Exception as account_error:
            logger.warning(f"Error retrieving account info: {str(account_error)}")
            account_info = {"address": address}
            
        # TODO(DDS_TEAM): Store connection in database with user profile

        return jsonify(
            {
                "success": True,
                "message": "Wallet connected successfully",
                "address": address,
                "account_info": account_info
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
        config = {
            "chainId": blockchain_gateway.network_config.chain_id,
            "chainName": "Odiseo Testnet",
            "rpc": blockchain_gateway.network_config.rpc_url,
            "rest": blockchain_gateway.network_config.api_url,
            "bip44": {"coinType": 118},
            "currencies": [{"coinDenom": "ODIS", "coinMinimalDenom": "uodis", "coinDecimals": 6}],
            "feeCurrencies": [{"coinDenom": "ODIS", "coinMinimalDenom": "uodis", "coinDecimals": 6}],
            "stakeCurrency": {"coinDenom": "ODIS", "coinMinimalDenom": "uodis", "coinDecimals": 6}
        }
        logger.debug(f"Returning network config: {config}")
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting network config: {str(e)}")
        return jsonify({"error": str(e)}), 500
