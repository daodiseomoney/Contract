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

        # Log the incoming request
        logger.info(f"Fetching account data for address: {address}")

        # Get account data from service
        account_data = account_service.get_account_data(address)
        logger.debug(f"Account data retrieved: {account_data}")

        return jsonify(account_data)

    except ValueError as e:
        logger.error(f"Account data error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error getting account data: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to fetch account data"}), 500