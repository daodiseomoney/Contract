from flask import Blueprint, request, jsonify
from src.services.transaction_service import TransactionService
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

transaction_bp = Blueprint('transaction', __name__)
transaction_service = TransactionService()

@transaction_bp.route('/api/sign', methods=['POST'])
def sign_transaction():
    """Handle signed transaction from Keplr and broadcast it"""
    try:
        logger.debug("Received sign request")
        data = request.get_json()

        if not data:
            logger.error("No data received in sign request")
            return jsonify({"error": "No data provided"}), 400

        logger.debug(f"Processing signed transaction data: {data}")

        # Validate required fields
        if not data.get("signed"):
            logger.error("Missing 'signed' field in request data")
            return jsonify({"error": "Missing 'signed' field in transaction data"}), 400
        if not data.get("signature"):
            logger.error("Missing 'signature' field in request data")
            return jsonify({"error": "Missing 'signature' field in transaction data"}), 400

        # Broadcast the signed transaction
        result = transaction_service.broadcast_signed_tx(data)

        if not result.get("success"):
            logger.error(f"Failed to broadcast transaction: {result.get('error')}")
            return jsonify({"error": result.get("error")}), 400

        logger.info(f"Successfully broadcasted transaction: {result}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing sign request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500