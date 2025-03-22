from flask import Blueprint, jsonify, request
from src.gateways.blockchain_gateway import MockBlockchainGateway
from src.gateways.llm_gateway import SimpleLLMGateway

contract_bp = Blueprint('contract', __name__, url_prefix='/api')

blockchain = MockBlockchainGateway()
llm = SimpleLLMGateway()

@contract_bp.route('/contracts', methods=['GET'])
def get_contracts():
    try:
        contracts = blockchain.get_active_contracts()
        return jsonify(contracts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/tokenize', methods=['POST'])
async def tokenize_property():
    try:
        data = request.json
        if not data or 'file_path' not in data or 'budget_splits' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        # Mock contract deployment
        contract_address = await blockchain.deploy_contract(
            bim_hash=data['file_path'],
            budget_splits=data['budget_splits']
        )

        return jsonify({
            'status': 'success',
            'contract_address': contract_address
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500