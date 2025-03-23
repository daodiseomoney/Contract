import logging
from flask import Blueprint, jsonify, request, current_app
from src.gateways.multisig_gateway import MultiSigBlockchainGateway, SignatureRole
from src.gateways.kepler_gateway import KeplerGateway
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.tx import Transaction
import hashlib
import json

contract_bp = Blueprint('contract', __name__, url_prefix='/api')

# Initialize gateways
blockchain = MultiSigBlockchainGateway(test_mode=True)
kepler = KeplerGateway({
    'chain_id': 'odiseo_1234-1',
    'rpc_url': 'https://odiseo.test.rpc.nodeshub.online',
    'api_url': 'https://odiseo.test.api.nodeshub.online'
})

@contract_bp.route('/tokenize', methods=['POST'])
def tokenize_property():
    """Initialize a new tokenization transaction"""
    try:
        current_app.logger.debug("Received tokenization request")
        data = request.json
        current_app.logger.debug(f"Request data: {data}")

        if not data:
            current_app.logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400

        if 'file_path' not in data:
            current_app.logger.error("Missing file_path in request")
            return jsonify({'error': 'Missing file_path'}), 400

        if 'budget_splits' not in data:
            current_app.logger.error("Missing budget_splits in request")
            return jsonify({'error': 'Missing budget_splits'}), 400

        # Validate budget splits
        try:
            budget_splits = data['budget_splits']
            total = sum(float(split) for split in budget_splits.values())
            if abs(total - 100) > 0.01:  # Allow for small floating point differences
                current_app.logger.error(f"Invalid budget splits total: {total}%")
                return jsonify({'error': 'Budget splits must total 100%'}), 400
        except (ValueError, AttributeError) as e:
            current_app.logger.error(f"Invalid budget splits format: {str(e)}")
            return jsonify({'error': 'Invalid budget splits format'}), 400

        # Create content hash
        content = {
            'file_path': data['file_path'],
            'budget_splits': data['budget_splits']
        }
        content_hash = hashlib.sha256(json.dumps(content).encode()).hexdigest()
        current_app.logger.debug(f"Generated content hash: {content_hash}")

        try:
            # Initialize network configuration
            current_app.logger.debug("Initializing network configuration")
            network = NetworkConfig(
                chain_id="odiseo_1234-1",
                url="grpc+https://odiseo.test.rpc.nodeshub.online",
                fee_minimum_gas_price=0.025,
                fee_denomination="uodis",
                staking_denomination="uodis"
            )

            client = LedgerClient(network)
            current_app.logger.debug(f"Connected to network: {network.chain_id}")

            # Create tokenization transaction
            current_app.logger.debug("Creating blockchain transaction")
            tx = Transaction()
            tx.add_message(
                "/cosmos.bank.v1beta1.MsgSend",
                {
                    "from_address": client.address(),
                    "to_address": content_hash,
                    "amount": [{
                        "denom": "uodis",
                        "amount": "1"
                    }],
                    "metadata": json.dumps(content)
                }
            )
            current_app.logger.debug("Transaction message added")

            # Create blockchain transaction
            transaction_id = blockchain.create_transaction(
                content_hash=content_hash,
                metadata=content
            )
            current_app.logger.info(f"Created transaction with ID: {transaction_id}")

            # Get full transaction details
            transaction = blockchain.get_transaction_status(transaction_id)
            current_app.logger.debug(f"Transaction details: {transaction}")

            return jsonify({
                'status': 'success',
                'transaction': transaction
            })

        except Exception as e:
            current_app.logger.error(f"Failed to create blockchain transaction: {str(e)}", exc_info=True)
            return jsonify({'error': f'Failed to create transaction: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"Tokenization error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/sign', methods=['POST'])
def sign_transaction():
    """Sign a transaction with Kepler wallet"""
    try:
        data = request.json
        if not data or 'transaction_id' not in data or 'role' not in data:
            current_app.logger.error("Missing required fields in sign request")
            return jsonify({'error': 'Missing required fields'}), 400

        role = SignatureRole(data['role'])
        signature = data.get('signature')

        if not signature:
            current_app.logger.error("Missing Kepler signature")
            return jsonify({'error': 'Missing Kepler signature'}), 400

        # Sign the transaction
        success = blockchain.sign_transaction(
            transaction_id=data['transaction_id'],
            role=role,
            signature=signature
        )

        if success:
            # Get updated transaction status
            transaction = blockchain.get_transaction_status(data['transaction_id'])
            return jsonify({
                'status': 'success',
                'transaction': transaction
            })
        current_app.logger.error("Signature verification failed")
        return jsonify({
            'status': 'failed',
            'error': 'Signature verification failed'
        }), 400

    except ValueError as e:
        current_app.logger.error(f"Invalid input: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to sign transaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts', methods=['GET'])
def get_contracts():
    """Get all contracts/transactions"""
    try:
        current_app.logger.debug("Fetching contracts")
        contracts = blockchain.get_active_contracts()
        return jsonify(contracts)
    except Exception as e:
        current_app.logger.error(f"Failed to get contracts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction_status(transaction_id):
    """Get the current status of a transaction"""
    try:
        transaction = blockchain.get_transaction_status(transaction_id)
        return jsonify(transaction)
    except ValueError as e:
        current_app.logger.error(f"Invalid transaction ID: {str(e)}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to get transaction status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/network-config', methods=['GET'])
def get_network_config():
    """Get Odiseo network configuration for Kepler wallet"""
    try:
        return jsonify(kepler.get_network_config())
    except Exception as e:
        current_app.logger.error(f"Failed to get network config: {str(e)}")
        return jsonify({'error': str(e)}), 500