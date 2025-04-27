import logging
import json
from flask import Blueprint, jsonify, request
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
contract_bp = Blueprint("contract", __name__, url_prefix="/api")

# Path to JSON file storing contract data
CONTRACTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "contracts.json"
)

# Ensure contracts file exists
if not os.path.exists(CONTRACTS_FILE):
    with open(CONTRACTS_FILE, "w") as f:
        json.dump([], f)


@contract_bp.route("/contracts", methods=["GET"])
def get_contracts():
    """Retrieve all contracts"""
    logger.debug("Fetching contracts")
    try:
        with open(CONTRACTS_FILE, "r") as f:
            contracts = json.load(f)
        return jsonify(contracts)
    except Exception as e:
        logger.error(f"Error fetching contracts: {str(e)}")
        return jsonify({"error": str(e)}), 500


@contract_bp.route("/contracts/<contract_id>", methods=["GET"])
def get_contract(contract_id):
    """Retrieve a specific contract by ID"""
    try:
        with open(CONTRACTS_FILE, "r") as f:
            contracts = json.load(f)

        contract = next((c for c in contracts if c.get("id") == contract_id), None)

        if not contract:
            return jsonify({"error": "Contract not found"}), 404

        return jsonify(contract)
    except Exception as e:
        logger.error(f"Error fetching contract {contract_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@contract_bp.route("/contracts", methods=["POST"])
def create_contract():
    """Create a new contract"""
    try:
        contract_data = request.json

        if not contract_data:
            return jsonify({"error": "No contract data provided"}), 400

        with open(CONTRACTS_FILE, "r") as f:
            contracts = json.load(f)

        # Generate simple ID
        contract_id = str(len(contracts) + 1)
        contract_data["id"] = contract_id

        contracts.append(contract_data)

        with open(CONTRACTS_FILE, "w") as f:
            json.dump(contracts, f, indent=2)

        logger.debug(f"Contract created with ID: {contract_id}")
        return jsonify(contract_data), 201
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}")
        return jsonify({"error": str(e)}), 500
