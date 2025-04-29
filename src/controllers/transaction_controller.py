import logging
import uuid
import json
from flask import Blueprint, jsonify, request
from src.services.transaction_service import TransactionService
from src.gateways.kepler_gateway import KeplerGateway, KeplerSignatureRole

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
transaction_bp = Blueprint("transaction", __name__, url_prefix="/api")

# Initialize service
transaction_service = TransactionService()
network_config = {
    "chain_id": "ithaca-1",  # Updated to match the testnet chain ID
    "rpc_url": "https://odiseo.test.rpc.nodeshub.online",
    "api_url": "https://odiseo.test.api.nodeshub.online"
}
kepler_gateway = KeplerGateway(network_config)


@transaction_bp.route("/transactions", methods=["GET"])
def get_transactions():
    """Retrieve blockchain transactions"""
    # Get from blockchain or return test data if no address is provided
    address = request.args.get("address")
    
    # ------------------------------------------------------------
    # TODO(DDS_TEAM): Replace mock transaction data with real blockchain queries
    # TODO(DDS_TEAM): Implement proper pagination for transaction results
    # TODO(DDS_TEAM): Add caching layer to reduce blockchain API calls
    # TODO(DDS_TEAM): Add proper error handling for blockchain query failures
    # ------------------------------------------------------------
    if address:
        # Try to get real transaction data for the address
        try:
            # This would be replaced with actual blockchain query
            logger.debug(f"Querying transactions for address: {address}")
            # Placeholder - real implementation would query blockchain
            return jsonify([
                {
                    "id": f"tx-{uuid.uuid4().hex[:8]}",
                    "type": "Property Tokenization",
                    "hash": f"0x{uuid.uuid4().hex}",
                    "timestamp": "2025-04-04T12:34:56Z",
                    "status": "confirmed",
                    "address": address,
                }
            ])
        except Exception as e:
            logger.error(f"Error querying transactions: {str(e)}")
            # Fall back to sample data
    
    # Sample transactions for display
    transactions = [
        {
            "id": "tx1",
            "type": "Property Tokenization",
            "hash": "0x7a3bc8e4f82b5d98f3c8bd71904a31c9e4d77d18e76d9b4d60bb598af3c9a8b2",
            "block": 10245678,
            "timestamp": "2025-04-04T12:34:56Z",
            "status": "confirmed",
            "value": "1500000",
            "currency": "ODIS",
        },
        {
            "id": "tx2",
            "type": "Document Upload",
            "hash": "0x9d2e7c6b45a3f2e89d364c5f7e8b9a1c2d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a",
            "block": 10245621,
            "timestamp": "2025-04-03T09:12:34Z",
            "status": "confirmed",
            "document": "Property Deed.pdf",
        },
        {
            "id": "tx3",
            "type": "Multi-sig Approval",
            "hash": "0x3f8e2d9c15b7a6f4d8e2c9b1a7d6f5e4d3c2b1a9f8e7d6c5b4a3f2e1d9c8b7a6",
            "block": 10245589,
            "timestamp": "2025-04-02T15:45:30Z",
            "status": "confirmed",
            "signatures": "3/4",
        },
    ]

    return jsonify(transactions)


@transaction_bp.route("/transactions/<tx_id>", methods=["GET"])
def get_transaction(tx_id):
    """Retrieve a specific transaction by ID"""
    # ------------------------------------------------------------
    # TODO(DDS_TEAM): Implement real blockchain query to fetch transaction details
    # TODO(DDS_TEAM): Add error handling for non-existent transaction IDs
    # TODO(DDS_TEAM): Add transaction verification using blockchain API
    # ------------------------------------------------------------
    logger.debug(f"Getting transaction details for: {tx_id}")

    mock_transactions = {
        "tx1": {
            "id": "tx1",
            "type": "Property Tokenization",
            "hash": "0x7a3bc8e4f82b5d98f3c8bd71904a31c9e4d77d18e76d9b4d60bb598af3c9a8b2",
            "block": 10245678,
            "timestamp": "2025-04-04T12:34:56Z",
            "status": "confirmed",
            "value": "1500000",
            "currency": "ODIS",
            "sender": "odiseo1a2b3c4d5e6f7g8h9i0j",
            "receiver": "odiseo0j9i8h7g6f5e4d3c2b1a",
            "gas_used": 21000,
            "gas_price": "0.000000001",
            "fees": "0.000021",
            "details": {
                "property_id": "prop123",
                "property_name": "Cosmic Tower",
                "token_count": 1500000,
                "token_price": "1.00",
                "total_value": "1500000.00",
            },
        }
    }

    if tx_id not in mock_transactions:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify(mock_transactions[tx_id])


@transaction_bp.route("/transactions/sign", methods=["POST"])
def sign_transaction():
    """Sign a transaction with a wallet"""
    try:
        data = request.json
        logger.debug(f"Received data for signing: {data}")

        if not data:
            return jsonify({"error": "Transaction data is required"}), 400

        if "wallet_address" not in data:
            return jsonify({"error": "Wallet address is required"}), 400
        
        # Extract transaction parameters
        wallet_address = data.get("wallet_address")
        transaction_id = data.get("transaction_id", f"tx-{uuid.uuid4().hex[:8]}")
        content_hash = data.get("content_hash", "")
        role = data.get("role", "owner")
        
        # Create transaction parameters
        tx_data = {
            "from_address": wallet_address,
            "to_address": data.get("to_address", "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"),
            "amount": data.get("amount", [{"denom": "uodis", "amount": "1000"}]),
            "transaction_id": transaction_id,
            "content_hash": content_hash,
            "role": role
        }
        
        # Try to get account info from blockchain
        try:
            # Get real account information for transaction parameters
            from src.gateways.pingpub_gateway import PingPubGateway
            pingpub_gateway = PingPubGateway()
            account_info = pingpub_gateway.get_account_info(wallet_address)
            
            # Add account info to transaction data
            tx_data["account_number"] = account_info.get("account_number", "0")
            tx_data["sequence"] = account_info.get("sequence", "0")
            
            logger.debug(f"Using account info from blockchain: {account_info}")
        except Exception as acc_error:
            logger.warning(f"Error retrieving account info: {str(acc_error)}")
            # Continue without account info, will use defaults
        
        # Create sign doc for Keplr wallet using Kepler gateway
        sign_doc = kepler_gateway.sign_transaction(tx_data)
        
        return jsonify({
            "success": True,
            "sign_doc": sign_doc,
            "transaction_id": transaction_id,
            "broadcast_url": "/api/transactions/broadcast"
        })
    except Exception as e:
        logger.error(f"Error preparing transaction for signing: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@transaction_bp.route("/transactions/broadcast", methods=["POST"])
def broadcast_transaction():
    """Broadcast a signed transaction to the blockchain"""
    try:
        data = request.json
        logger.debug(f"Received data for broadcasting: {data}")

        # Validate input data
        if not data:
            return jsonify({"error": "Transaction data is required"}), 400
            
        if "signature" not in data:
            return jsonify({"error": "Signature is required"}), 400
            
        if "transaction" not in data:
            return jsonify({"error": "Transaction data is required"}), 400
            
        # Extract signature and transaction data
        signature = data["signature"]
        transaction = data["transaction"]
        
        # Get signature components
        signature_value = signature.get("signature")
        pub_key = signature.get("pub_key")
        
        # Get signed transaction details for formatting
        signed_tx = signature.get("signed", {})
        
        # Validate signature components
        if not signature_value or not pub_key:
            return jsonify({"error": "Invalid signature format"}), 400
            
        # Convert Amino messages to Proto format
        amino_msgs = signed_tx.get("msgs", [])
        proto_msgs = []
        
        for msg in amino_msgs:
            proto_msg = kepler_gateway.convert_amino_to_proto(msg)
            proto_msgs.append(proto_msg)
            
        logger.debug(f"Converted messages to Proto format: {proto_msgs}")
        
        # Prepare broadcast data
        broadcast_tx = {
            "tx": {
                "msg": proto_msgs,
                "fee": signed_tx.get("fee", {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"}),
                "signatures": [{
                    "pub_key": pub_key,
                    "signature": signature_value
                }],
                "memo": signed_tx.get("memo", "")
            },
            "mode": "block"  # Wait for confirmation
        }
        
        # Broadcast the transaction
        result = transaction_service.broadcast_transaction(broadcast_tx)
        
        # Format response with transaction hash
        tx_hash = result.get("txhash", "")
        explorer_url = f"https://testnet.explorer.nodeshub.online/odiseo/tx/{tx_hash}"
        
        return jsonify({
            "success": True,
            "message": "Transaction broadcasted successfully",
            "txhash": tx_hash,
            "explorer_url": explorer_url,
            "result": result
        })
    except Exception as e:
        logger.error(f"Error broadcasting transaction: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@transaction_bp.route("/transactions/create", methods=["POST"])
def create_transaction():
    """Create a transaction for tokenizing a property"""
    try:
        data = request.json
        logger.debug(f"Received data for creating transaction: {data}")

        # ------------------------------------------------------------
        # TODO(DDS_TEAM): Implement proper property validation
        # TODO(DDS_TEAM): Add token distribution calculations
        # TODO(DDS_TEAM): Connect to smart contract for token creation
        # TODO(DDS_TEAM): Implement multi-signature requirements
        # ------------------------------------------------------------

        if not data or "property_id" not in data:
            return jsonify({"error": "Property ID is required"}), 400

        property_id = data["property_id"]
        property_value = data.get("property_value", "1000000")
        token_count = data.get("token_count", "1000000")
        
        # Generate transaction ID
        transaction_id = f"tx-{uuid.uuid4().hex[:8]}"
        
        # Create a message with proper structure for Cosmos SDK
        msg = {
            "type": "cosmos-sdk/MsgSend",
            "property_id": property_id,
            "property_value": property_value,
            "token_count": token_count,
            "transaction_id": transaction_id
        }
        
        # Return the transaction data
        return jsonify({
            "success": True,
            "transaction_id": transaction_id,
            "msg": msg,
            "next_steps": {
                "sign": f"/api/transactions/sign",
                "broadcast": f"/api/transactions/broadcast"
            }
        })
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
