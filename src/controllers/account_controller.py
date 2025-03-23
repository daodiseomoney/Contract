from flask import Blueprint, request, jsonify
from src.services.account_service import AccountService
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

account_bp = Blueprint('account', __name__)
account_service = AccountService()

@account_bp.route('/api/account', methods=['GET'])
def get_account_data():
    """Get account data for an address"""
    try:
        address = request.args.get('address')
        logger.debug(f"Received request for address: {address}")

        if not address:
            logger.warning("No address provided in request")
            return jsonify({"error": "Address parameter is required"}), 400

        if not address.startswith('odiseo1'):
            logger.error(f"Invalid address format: {address}")
            return jsonify({"error": "Invalid address format. Must start with 'odiseo1'"}), 400

        # Log the incoming request
        logger.info(f"Fetching account data for address: {address}")

        # Get account data from service
        try:
            account_data = account_service.get_account_data(address)
            logger.debug(f"Account data retrieved: {account_data}")
            return jsonify(account_data)
        except ConnectionError as ce:
            logger.error(f"Network connection error: {str(ce)}")
            return jsonify({"error": "Failed to connect to blockchain network. Please try again later."}), 503
        except ValueError as ve:
            if "403" in str(ve) or "401" in str(ve):
                logger.error(f"Authentication error accessing RPC: {str(ve)}")
                return jsonify({"error": "Unable to access blockchain network. Please try again later."}), 503
            logger.error(f"Account data validation error: {str(ve)}")
            return jsonify({"error": str(ve)}), 400

    except Exception as e:
        logger.error(f"Unexpected error getting account data: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error while fetching account data"}), 500