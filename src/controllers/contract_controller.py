from flask import Blueprint, jsonify, request
from src.gateways.multisig_gateway import MultiSigBlockchainGateway, SignatureRole
import hashlib
import json

contract_bp = Blueprint('contract', __name__, url_prefix='/api')
blockchain = MultiSigBlockchainGateway(test_mode=True)  # Start in test mode

@contract_bp.route('/contracts', methods=['GET'])
def get_contracts():
    """Get all contracts/transactions"""
    try:
        contracts = blockchain.get_pending_transactions()
        return jsonify(contracts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/tokenize', methods=['POST'])
def tokenize_property():
    """Initialize a new multi-signature transaction"""
    try:
        data = request.json
        if not data or 'file_path' not in data or 'budget_splits' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        # Create content hash from file path and budget splits
        content = {
            'file_path': data['file_path'],
            'budget_splits': data['budget_splits']
        }
        content_hash = hashlib.sha256(json.dumps(content).encode()).hexdigest()

        # Create multi-signature transaction
        transaction_id = blockchain.create_transaction(
            content_hash=content_hash,
            metadata=content
        )

        return jsonify({
            'status': 'pending_signatures',
            'transaction_id': transaction_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/sign', methods=['POST'])
def sign_transaction():
    """Sign a transaction with a specific role"""
    try:
        data = request.json
        if not data or 'transaction_id' not in data or 'role' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        role = SignatureRole(data['role'])
        signature = data.get('signature', 'test_signature')  # Use test signature in test mode

        # Sign the transaction
        success = blockchain.sign_transaction(
            transaction_id=data['transaction_id'],
            role=role,
            signature=signature
        )

        if success:
            # Check if transaction is complete
            if blockchain.is_transaction_complete(data['transaction_id']):
                return jsonify({
                    'status': 'complete',
                    'message': 'Transaction fully signed'
                })
            return jsonify({
                'status': 'signed',
                'message': f'Successfully signed with role {role.value}'
            })
        return jsonify({
            'status': 'failed',
            'error': 'Signature verification failed'
        }), 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction_status(transaction_id):
    """Get the current status of a transaction"""
    try:
        status = blockchain.get_transaction_status(transaction_id)
        return jsonify(status)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500