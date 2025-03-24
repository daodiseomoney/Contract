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

        # Log the complete data for debugging purposes
        logger.debug(f"Processing signed transaction data: {data}")
        
        # Log content type and headers for more context
        logger.debug(f"Request content type: {request.content_type}")
        logger.debug(f"Request headers: {dict(request.headers)}")

        # Validate required fields with detailed error messages
        if not data.get("signed"):
            logger.error(f"Missing 'signed' field in request data. Full data: {data}")
            return jsonify({"error": "Missing 'signed' field in transaction data"}), 400
        if not data.get("signature"):
            logger.error(f"Missing 'signature' field in request data. Full data: {data}")
            return jsonify({"error": "Missing 'signature' field in transaction data"}), 400

        # Verify memo format
        signed_data = data.get("signed", {})
        memo = signed_data.get("memo", "")

        # Check if memo is a simple string (not JSON)
        if memo.startswith("{") or memo.startswith("["):
            logger.error("Invalid memo format: JSON object not allowed")
            return jsonify({"error": "Memo must be a simple text string"}), 400

        # Validate memo format - support both formats:
        # 1. Legacy format: "tx:ID|hash:HASH|role:ROLE"
        # 2. New format: "ID:HASH:ROLE"
        is_legacy_format = False
        is_new_format = False
        
        # Check for legacy format with pipe separators
        if "|" in memo:
            expected_parts = ["tx:", "hash:", "role:"]
            is_legacy_format = all(part in memo for part in expected_parts)
        
        # Check for new simplified format with just colons
        elif memo.count(":") == 2:
            # Format is "ID:HASH:ROLE"
            parts = memo.split(":")
            is_new_format = len(parts) == 3 and all(parts)
        
        if not (is_legacy_format or is_new_format):
            logger.error(f"Invalid memo format. Expected either 'tx:ID|hash:HASH|role:ROLE' or 'ID:HASH:ROLE', got: {memo}")
            return jsonify({"error": "Invalid memo format"}), 400

        # Format the data for transaction service
        # We need to convert from Keplr's signAmino response format to the expected format for broadcast
        
        # Process the messages from signed_data to ensure they are in correct format
        msgs = signed_data.get('msgs', [])
        processed_msgs = []
        
        logger.debug(f"Processing messages from Keplr: {msgs}")
        
        for msg in msgs:
            # Check if this is a message object that needs to be transformed
            if isinstance(msg, dict):
                logger.debug(f"Processing message: {msg}")
                
                # Case 1: Already in correct Amino format with type and value
                if 'type' in msg and 'value' in msg:
                    processed_msgs.append(msg)
                    logger.debug(f"Message already in correct Amino format: {msg}")
                
                # Case 2: Proto format with typeUrl
                elif 'typeUrl' in msg and 'value' in msg:
                    # Convert Proto to Amino format for backend compatibility
                    logger.debug(f"Converting Proto format message to Amino: {msg}")
                    
                    if msg['typeUrl'] == '/cosmos.bank.v1beta1.MsgSend':
                        value = msg.get('value', {})
                        # Convert Proto field names to Amino format
                        amino_msg = {
                            'type': 'cosmos-sdk/MsgSend',
                            'value': {
                                'from_address': value.get('fromAddress', ''),
                                'to_address': value.get('toAddress', ''),
                                'amount': value.get('amount', [])
                            }
                        }
                        processed_msgs.append(amino_msg)
                        logger.debug(f"Converted Proto to Amino: {amino_msg}")
                    else:
                        logger.warning(f"Unknown Proto typeUrl: {msg.get('typeUrl')}")
                        # Still include the message to avoid losing data
                        processed_msgs.append(msg)
                
                # Case 3: Flat structure (no nested value)
                elif all(k in msg for k in ['from_address', 'to_address', 'amount']):
                    # Amino format without proper structure
                    logger.debug(f"Restructuring flat Amino message: {msg}")
                    reconstructed_msg = {
                        'type': 'cosmos-sdk/MsgSend',
                        'value': {
                            'from_address': msg.get('from_address', ''),
                            'to_address': msg.get('to_address', ''),
                            'amount': msg.get('amount', [])
                        }
                    }
                    processed_msgs.append(reconstructed_msg)
                    logger.debug(f"Restructured message: {reconstructed_msg}")
                
                # Case 4: Proto format flat structure
                elif all(k in msg for k in ['fromAddress', 'toAddress', 'amount']):
                    logger.debug(f"Restructuring flat Proto message: {msg}")
                    amino_msg = {
                        'type': 'cosmos-sdk/MsgSend',
                        'value': {
                            'from_address': msg.get('fromAddress', ''),
                            'to_address': msg.get('toAddress', ''),
                            'amount': msg.get('amount', [])
                        }
                    }
                    processed_msgs.append(amino_msg)
                    logger.debug(f"Converted Proto fields to Amino: {amino_msg}")
                
                # Case 5: Unknown format but still valid dictionary
                else:
                    logger.warning(f"Unknown message format, passing through as-is: {msg}")
                    # For compatibility, don't drop messages during testing phase
                    processed_msgs.append(msg)
            else:
                logger.error(f"Unexpected message format (not a dict): {msg}")
        
        tx_data = {
            'tx': {
                'msg': processed_msgs,  # Use processed messages
                'fee': signed_data.get('fee', {'amount': [], 'gas': '100000'}),
                'memo': memo,
                'signatures': [{
                    'signature': data.get('signature', {}).get('signature', ''),
                    'pub_key': data.get('signature', {}).get('pub_key', {})
                }]
            },
            'mode': 'block'  # Wait for block confirmation
        }
        
        logger.debug(f"Formatted transaction data for broadcast: {tx_data}")
        
        # Broadcast the signed transaction
        result = transaction_service.broadcast_transaction(tx_data)
        logger.debug(f"Broadcast result: {result}")

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
        # Include more detailed error information
        return jsonify({
            "error": str(e),
            "error_type": "ValueError",
            "details": "The transaction data format was invalid"
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error broadcasting transaction: {str(e)}", exc_info=True)
        # Include more information about the exception
        error_type = type(e).__name__
        error_details = {
            "error": "Failed to broadcast transaction",
            "error_type": error_type,
            "error_message": str(e),
        }
        return jsonify(error_details), 500