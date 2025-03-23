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

        # Verify memo format
        signed_data = data.get("signed", {})
        memo = signed_data.get("memo", "")

        # Check if memo is a simple string (not JSON)
        if memo.startswith("{") or memo.startswith("["):
            logger.error("Invalid memo format: JSON object not allowed")
            return jsonify({"error": "Memo must be a simple text string"}), 400

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


@transaction_bp.route('/api/broadcast', methods=['POST'])
def broadcast_transaction():
    """Broadcast a signed transaction to the blockchain"""
    try:
        # Get transaction data from request
        transaction_data = request.get_json()
        logger.debug(f"Received broadcast request: {transaction_data}")

        if not transaction_data or not transaction_data.get('tx'):
            logger.warning("No transaction data provided in request")
            return jsonify({"error": "Transaction data is required"}), 400

        # Validate transaction structure
        tx = transaction_data.get('tx', {})
        required_fields = ['msg', 'fee', 'signatures', 'memo']
        missing_fields = [field for field in required_fields if field not in tx]

        if missing_fields:
            error_msg = f"Missing required fields in transaction: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400

        # Log the incoming broadcast request
        logger.info("Broadcasting transaction to blockchain")

        # Broadcast transaction via service
        result = transaction_service.broadcast_transaction(transaction_data)
        logger.debug(f"Broadcast result: {result}")

        if not result.get("success"):
            return jsonify({"error": result.get("error")}), 400

        # Return successful response with transaction details
        return jsonify({
            "success": True,
            "txhash": result.get("txhash"),
            "height": result.get("height"),
            "code": result.get("code", 0),
            "gas_used": result.get("gas_used"),
            "raw_log": result.get("raw_log", "")
        })

    except ValueError as e:
        logger.error(f"Transaction broadcast error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"Unexpected error broadcasting transaction: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to broadcast transaction"}), 500