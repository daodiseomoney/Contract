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

@bim_agent_bp.route('/execute-staking', methods=['POST'])
def execute_staking():
    """
    Execute staking for validated IFC files
    Implementation of the CosmWasm staking contract logic
    Expects JSON: {"ifc_hash": "0x123...", "liquidity": 10000}
    """
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
        
        # Validate IFC file
        is_validated = validate_ifc_file(ifc_hash)
        
        if not is_validated:
            return jsonify({
                'success': False,
                'message': 'Unverified asset',
                'code': 'CONTRACT_ERROR_UNVERIFIED_ASSET'
            }), 400
            
        # Calculate ODIS reward
        odis_reward = calculate_odis_reward(liquidity)
        
        # Generate transaction ID
        tx_id = f"TX-{str(uuid.uuid4())[:8]}"
        
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

def analyze_ifc_file(file_name, file_size):
    """
    Analyze an IFC file using AI and return metrics
    This would integrate with the BIM Agent's actual IFC processing logic
    """
    # Mock implementation - generates metrics based on file name and size
    metrics = {
        "building_type": "Commercial High-Rise" if "tower" in file_name.lower() else "Office Complex",
        "total_area": round(file_size * 1000),  # Simplified calculation
        "stories": 17 if "tower" in file_name.lower() else 12,
        "construction_year": 2023,
        "estimated_value": round(file_size * 500000),  # Simplified calculation
        "risk_score": round(0.2 + (file_size % 10) / 100, 2)
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

def calculate_odis_reward(liquidity):
    """
    Calculate ODIS rewards for a given liquidity amount
    Implementation of the CosmWasm reward function:
    
    pub fn execute_staking(
        deps: DepsMut,
        env: Env,
        ifc_hash: String,
        liquidity: u128
    ) -> Result<Response, ContractError> {
        if bim_server::validate_ifc(&ifc_hash) {
            let odis = liquidity * 0.05; // Base reward
            // Add AI-adjusted bonus based on market volatility
            Ok(Response::new().add_attribute("ODIS_REWARD", odis.to_string()))
        } else {
            Err(ContractError::UnverifiedAsset {})
        }
    }
    """
    # Base reward is 5% of liquidity
    base_reward = liquidity * 0.05
    
    # Add market volatility adjustment
    market_volatility = 0.01  # 1% bonus
    
    # Total reward with bonus
    total_reward = base_reward * (1 + market_volatility)
    
    return round(total_reward, 2)

def validate_ifc_file(ifc_hash):
    """
    Check if an IFC file has been validated
    This would query the blockchain or database for the actual validation status
    """
    # Consider certain hash prefixes as validated
    valid_prefixes = ['0x71C', '0x31F', '0x28A']
    return any(ifc_hash.startswith(prefix) for prefix in valid_prefixes)

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
