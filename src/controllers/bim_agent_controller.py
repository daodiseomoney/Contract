"""
BIM Agent Controller for handling AI-related routes
"""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request

from src.bim.bim_agent import BIMAgentManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a Flask Blueprint
bim_agent_bp = Blueprint('bim_agent', __name__, url_prefix='/api/bim-agent')

# Initialize the BIM Agent Manager
bim_agent_manager = BIMAgentManager()

@bim_agent_bp.route('/chat', methods=['POST'])
def chat():
    """
    Process a chat message and return the AI response
    Expects JSON: {"message": "user message here"}
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'message': 'Message field is required'
        }), 400
    
    message = data['message']
    
    # Log the incoming message
    logger.debug(f"Received chat message: {message}")
    
    # Process the message
    result = bim_agent_manager.process_message(message)
    
    # Return the result
    return jsonify(result)

@bim_agent_bp.route('/toggle-enhanced', methods=['POST'])
def toggle_enhanced():
    """
    Toggle enhanced AI mode
    Expects JSON: {"enabled": true/false}
    """
    data = request.get_json()
    
    if not data or 'enabled' not in data:
        return jsonify({
            'success': False,
            'message': 'Enabled field is required'
        }), 400
    
    enabled = data['enabled']
    
    # Log the toggle request
    logger.debug(f"Toggling enhanced mode: {enabled}")
    
    # Toggle enhanced mode
    result = bim_agent_manager.toggle_enhanced_mode(enabled)
    
    # Return the result
    return jsonify(result)

@bim_agent_bp.route('/enhanced-status', methods=['GET'])
def enhanced_status():
    """Get the current status of enhanced mode"""
    status = bim_agent_manager.get_enhanced_mode()
    
    # Add additional enhanced features based on requirements
    return jsonify({
        'success': True,
        'enhanced_mode': status,
        'features': [
            "IFC validation",
            "AI-assisted analysis",
            "Stakeholder detection",
            "Due diligence automation",
            "Auto-ODIS rewards",
            "SPV/KYC verification"
        ]
    })

@bim_agent_bp.route('/building-data', methods=['GET'])
def building_data():
    """Get building data for the UI"""
    data = bim_agent_manager.get_building_data()
    
    return jsonify({
        'success': True,
        'data': data
    })

@bim_agent_bp.route('/element/<element_id>', methods=['GET'])
def get_element(element_id):
    """Get element details by ID"""
    result = bim_agent_manager.get_element_by_id(element_id)
    
    return jsonify(result)

@bim_agent_bp.route('/validate-ifc', methods=['POST'])
def validate_ifc():
    """
    Validate an IFC file and trigger ODIS rewards
    Expects JSON: {"ifc_hash": "0x123...", "file_size": 25.4, "file_name": "example.ifc"}
    """
    try:
        data = request.get_json()
        if not data or 'ifc_hash' not in data:
            return jsonify({
                'success': False,
                'message': 'IFC hash is required'
            }), 400
        
        ifc_hash = data.get('ifc_hash')
        file_size = data.get('file_size', 0)  # Size in MB
        file_name = data.get('file_name', 'Unknown')
        
        logger.debug(f"Validating IFC file: {file_name} ({ifc_hash})")
        
        # AI metrics analysis
        metrics = analyze_ifc_file(file_name, file_size)
        
        # Calculate ODIS rewards
        initial_liquidity = metrics.get('estimated_value', 0)
        odis_reward = calculate_odis_reward(initial_liquidity)
        
        return jsonify({
            'success': True,
            'validated': True,
            'ifc_hash': ifc_hash,
            'metrics': metrics,
            'odis_reward': odis_reward,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error validating IFC file: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bim_agent_bp.route('/due-diligence-status', methods=['GET'])
def due_diligence_status():
    """
    Get the due diligence status for a specific IFC file
    Query param: ?ifc_hash=0x123...
    """
    try:
        ifc_hash = request.args.get('ifc_hash')
        if not ifc_hash:
            return jsonify({
                'success': False,
                'message': 'IFC hash is required'
            }), 400
        
        logger.debug(f"Getting due diligence status for: {ifc_hash}")
        
        # Determine status based on hash prefix
        if ifc_hash.startswith('0x71C'):
            status = 'verified'
            spv_kyc = True
            steps_completed = 5
        elif ifc_hash.startswith('0x94B'):
            status = 'in_progress'
            spv_kyc = False
            steps_completed = 2
        else:
            status = 'pending'
            spv_kyc = False
            steps_completed = 1
            
        steps = [
            {
                "name": "IFC File Validation",
                "status": "complete",
                "timestamp": "2025-04-01T14:32:45Z"
            },
            {
                "name": "Legal Document Review",
                "status": "complete" if steps_completed > 1 else "pending",
                "timestamp": "2025-04-02T10:15:30Z" if steps_completed > 1 else None
            },
            {
                "name": "SPV Formation",
                "status": "complete" if steps_completed > 2 else "pending",
                "timestamp": "2025-04-03T16:45:22Z" if steps_completed > 2 else None
            },
            {
                "name": "Validator Approval (3/5)",
                "status": "complete" if steps_completed > 3 else "pending",
                "timestamp": "2025-04-04T09:12:18Z" if steps_completed > 3 else None
            },
            {
                "name": "KYC Verification",
                "status": "complete" if steps_completed > 4 else "pending",
                "timestamp": "2025-04-05T11:30:45Z" if steps_completed > 4 else None
            }
        ]
        
        return jsonify({
            'success': True,
            'ifc_hash': ifc_hash,
            'status': status,
            'spv_kyc_verified': spv_kyc,
            'steps': steps,
            'nft_minting_eligible': spv_kyc
        })
    except Exception as e:
        logger.error(f"Error getting due diligence status: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Dictionary to keep track of active staking transactions
# In a real implementation, this would be stored in a database or Redis
_staking_locks = {}

def acquire_staking_lock(asset_id):
    """Acquire a lock for a specific asset"""
    if asset_id in _staking_locks:
        return False
    _staking_locks[asset_id] = True
    return True

def release_staking_lock(asset_id):
    """Release the lock for a specific asset"""
    if asset_id in _staking_locks:
        del _staking_locks[asset_id]

def record_transaction(tx_id, ifc_hash, liquidity, odis_reward):
    """Record transaction in a persistent store"""
    # In a real implementation, this would store the transaction in a database
    logger.info(f"Recording transaction {tx_id} for {ifc_hash} with liquidity {liquidity} and reward {odis_reward}")
    # db.session.add(Transaction(tx_id=tx_id, ifc_hash=ifc_hash, liquidity=liquidity, odis_reward=odis_reward))
    # db.session.commit()
    pass

@bim_agent_bp.route('/execute-staking', methods=['POST'])
def execute_staking():
    """
    Execute staking for validated IFC files
    Implementation of the CosmWasm staking contract logic
    Expects JSON: {"ifc_hash": "0x123...", "liquidity": 10000}
    """
    ifc_hash = None  # Initialize outside try block to avoid "unbound" error
    
    try:
        data = request.get_json()
        if not data or 'ifc_hash' not in data or 'liquidity' not in data:
            return jsonify({
                'success': False,
                'message': 'IFC hash and liquidity amount are required'
            }), 400
        
        ifc_hash = data.get('ifc_hash')
        liquidity = float(data.get('liquidity', 0))
        
        logger.debug(f"Executing staking for: {ifc_hash} with liquidity: {liquidity}")
        
        # Validate IFC file first
        is_validated = validate_ifc_file(ifc_hash)
        
        if not is_validated:
            return jsonify({
                'success': False,
                'message': 'Unverified asset',
                'code': 'CONTRACT_ERROR_UNVERIFIED_ASSET'
            }), 400
        
        # Acquire a lock to prevent reentrancy
        lock_acquired = acquire_staking_lock(ifc_hash)
        if not lock_acquired:
            return jsonify({
                'success': False,
                'message': 'Transaction already in progress for this asset',
                'code': 'CONTRACT_ERROR_LOCK'
            }), 429
        
        # Calculate ODIS reward
        odis_reward = calculate_odis_reward(liquidity)
        
        # Generate transaction ID
        tx_id = f"TX-{str(uuid.uuid4())[:8]}"
        
        # Record transaction in database BEFORE returning
        record_transaction(tx_id, ifc_hash, liquidity, odis_reward)
        
        # Transaction successful, release lock before returning
        release_staking_lock(ifc_hash)
        
        return jsonify({
            'success': True,
            'tx_id': tx_id,
            'ifc_hash': ifc_hash,
            'liquidity': liquidity,
            'odis_reward': odis_reward,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error executing staking: {e}")
        
        # Release lock if acquired and there was an error
        if ifc_hash and ifc_hash in _staking_locks:
            release_staking_lock(ifc_hash)
            
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bim_agent_bp.route('/auto-suggest-liquidity', methods=['POST'])
def auto_suggest_liquidity():
    """
    Let the AI suggest optimal liquidity amounts based on user history and asset metrics
    Expects JSON: {"ifc_hash": "0x123...", "user_history": [1000, 1500, 2000]}
    """
    try:
        data = request.get_json()
        if not data or 'ifc_hash' not in data:
            return jsonify({
                'success': False,
                'message': 'IFC hash is required'
            }), 400
        
        ifc_hash = data.get('ifc_hash')
        user_history = data.get('user_history', [])
        
        logger.debug(f"Suggesting liquidity for: {ifc_hash}")
        
        # Get asset metrics
        metrics = analyze_ifc_file_by_hash(ifc_hash)
        estimated_value = metrics.get('estimated_value', 0)
        
        # Calculate suggested liquidity
        suggested_liquidity = suggest_liquidity(user_history, estimated_value)
        
        return jsonify({
            'success': True,
            'ifc_hash': ifc_hash,
            'suggested_liquidity': suggested_liquidity,
            'estimated_value': estimated_value,
            'odis_reward_estimate': calculate_odis_reward(suggested_liquidity)
        })
    except Exception as e:
        logger.error(f"Error suggesting liquidity: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Helper functions

# Define reasonable bounds for building metrics
MAX_AREA = 1000000  # Maximum area in square meters
MAX_STORIES = 200  # Maximum number of stories
MIN_STORIES = 1  # Minimum number of stories
MAX_VALUE = 5000000000  # Maximum building value (5 billion)
MIN_VALUE = 100000  # Minimum building value (100,000)
MAX_FILE_SIZE = 500  # Maximum IFC file size in MB

def analyze_ifc_file(file_name, file_size):
    """
    Analyze an IFC file using AI and return metrics with secure bounds
    """
    # Validate inputs
    if not file_name or not isinstance(file_name, str):
        logger.warning(f"Invalid file name: {file_name}")
        file_name = "unknown.ifc"
    
    # Sanitize file name to prevent injection
    file_name = ''.join(c for c in file_name if c.isalnum() or c in '._- ')
    
    # Enforce file size limits
    if file_size <= 0 or file_size > MAX_FILE_SIZE:
        logger.warning(f"Invalid file size (capped): {file_size}")
        file_size = min(max(1, file_size), MAX_FILE_SIZE)
    
    # Use a more predictable algorithm for metrics calculation
    is_tower = "tower" in file_name.lower() or "highrise" in file_name.lower()
    is_office = "office" in file_name.lower() or "commercial" in file_name.lower()
    is_residential = "residential" in file_name.lower() or "apartment" in file_name.lower()
    
    # Determine building type based on file name keywords
    if is_tower:
        building_type = "Commercial High-Rise"
        base_stories = 25
        area_multiplier = 800
        value_multiplier = 550000
    elif is_office:
        building_type = "Office Complex"
        base_stories = 12
        area_multiplier = 1200
        value_multiplier = 450000
    elif is_residential:
        building_type = "Residential Building"
        base_stories = 8
        area_multiplier = 1000
        value_multiplier = 350000
    else:
        building_type = "Mixed Use"
        base_stories = 10
        area_multiplier = 900
        value_multiplier = 400000
    
    # Calculate metrics with bounds
    stories = min(MAX_STORIES, max(MIN_STORIES, round(base_stories * (0.5 + file_size / 100))))
    total_area = min(MAX_AREA, round(file_size * area_multiplier))
    estimated_value = min(MAX_VALUE, max(MIN_VALUE, round(file_size * value_multiplier)))
    
    # Create metrics with bounded values
    metrics = {
        "building_type": building_type,
        "total_area": total_area,
        "stories": stories,
        "construction_year": min(2030, max(1900, 2023)),
        "estimated_value": estimated_value,
        "risk_score": min(1.0, max(0.1, round(0.2 + (file_size % 10) / 100, 2)))
    }
    
    return metrics

def analyze_ifc_file_by_hash(ifc_hash):
    """
    Get metrics for an IFC file using its hash
    This would query the database for the actual IFC file metrics
    """
    # Mock implementation - returns predefined values based on hash prefix
    if ifc_hash.startswith('0x71C'):
        return {
            "building_type": "Commercial High-Rise",
            "total_area": 25000,
            "stories": 17,
            "construction_year": 2023,
            "estimated_value": 15811040,
            "risk_score": 0.2
        }
    elif ifc_hash.startswith('0x94B'):
        return {
            "building_type": "Office Complex",
            "total_area": 32000,
            "stories": 12,
            "construction_year": 2022,
            "estimated_value": 12500000,
            "risk_score": 0.25
        }
    else:
        return {
            "building_type": "Mixed Use",
            "total_area": 18000,
            "stories": 8,
            "construction_year": 2024,
            "estimated_value": 9000000,
            "risk_score": 0.3
        }

# Constants for rewards
MIN_LIQUIDITY = 100.0  # Minimum liquidity amount
MAX_LIQUIDITY = 10000000.0  # Maximum liquidity amount (10 million)
MAX_REWARD = 1000000.0  # Maximum reward (1 million ODIS)
REWARD_RATE = 0.05  # Base reward rate (5%)
VOLATILITY_BONUS = 0.01  # Volatility bonus (1%)

def get_verified_market_volatility():
    """Get market volatility from a trusted source"""
    # In production, this would pull from a secure oracle
    return VOLATILITY_BONUS

def calculate_odis_reward(liquidity):
    """
    Calculate ODIS rewards for a given liquidity amount with security bounds
    Implementation of the CosmWasm reward function with additional security checks
    """
    # Validate liquidity is within allowed bounds
    if liquidity < MIN_LIQUIDITY:
        logger.warning(f"Liquidity below minimum threshold: {liquidity} < {MIN_LIQUIDITY}")
        liquidity = MIN_LIQUIDITY
    
    if liquidity > MAX_LIQUIDITY:
        logger.warning(f"Liquidity capped from {liquidity} to {MAX_LIQUIDITY}")
        liquidity = MAX_LIQUIDITY
    
    # Base reward calculation with rate limiting
    base_reward = liquidity * REWARD_RATE
    
    # Get market volatility from trusted source
    market_volatility = get_verified_market_volatility()
    
    # Calculate total reward with volatility bonus
    total_reward = base_reward * (1 + market_volatility)
    
    # Apply absolute maximum cap
    if total_reward > MAX_REWARD:
        logger.warning(f"Reward capped from {total_reward} to {MAX_REWARD}")
        total_reward = MAX_REWARD
    
    return round(total_reward, 2)

# Dictionary to simulate a secure database of validated IFC files with signatures
# In production, this would be stored in a secure database with cryptographic verification
_validated_ifc_files = {
    '0x71C9E3f5A2B7D1': {'signatures': ['sig1', 'sig2', 'sig3'], 'validators': 3, 'timestamp': '2025-04-01T14:32:45Z'},
    '0x31F7A2c8D9E0F1': {'signatures': ['sig1', 'sig2', 'sig3'], 'validators': 3, 'timestamp': '2025-03-21T10:15:30Z'},
    '0x28A1R7t6S5P4O': {'signatures': ['sig1', 'sig2', 'sig3'], 'validators': 3, 'timestamp': '2025-04-05T11:30:45Z'},
}

def verify_validator_signatures(ifc_hash, signatures):
    """
    Verify cryptographic signatures from validators
    In production, this would use actual crypto verification against validators' public keys
    """
    # Require at least 3 valid signatures for security
    return len(signatures) >= 3

def validate_ifc_file(ifc_hash):
    """
    Check if an IFC file has been validated using cryptographic verification
    """
    # Input validation - require proper hash format
    if not ifc_hash or not isinstance(ifc_hash, str) or not ifc_hash.startswith('0x'):
        logger.warning(f"Invalid IFC hash format: {ifc_hash}")
        return False
    
    # Get validation data from secure store
    validation_data = _validated_ifc_files.get(ifc_hash)
    
    # If not found in our secure validated list, reject it
    if not validation_data:
        logger.warning(f"IFC hash not found in validated list: {ifc_hash}")
        return False
    
    # Verify cryptographic signatures
    signatures = validation_data.get('signatures', [])
    if verify_validator_signatures(ifc_hash, signatures):
        logger.info(f"IFC hash validated with {len(signatures)} signatures: {ifc_hash}")
        return True
    
    logger.warning(f"IFC hash failed signature verification: {ifc_hash}")
    return False

def suggest_liquidity(user_history, estimated_value):
    """
    AI model to recommend staking amounts based on user history and asset value
    As described in the original requirements:
    
    def suggest_liquidity(self, user_history: list) -> float:
        # ML model to recommend staking amounts
        return user_history[-1] * 1.1 if user_history else 1000
    """
    # If user has history, suggest 10% more than their last transaction
    if user_history and len(user_history) > 0:
        last_amount = user_history[-1]
        return round(last_amount * 1.1, 2)
    
    # Otherwise suggest 5% of the estimated value
    return round(estimated_value * 0.05, 2)
