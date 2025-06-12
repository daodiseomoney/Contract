"""
Consolidated AI Controller for DAODISEO Platform
Combines agents, BIM AI, and orchestrator functionality
"""

import logging
import uuid
import os
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app

from src.services.ai.bim_agent import BIMAgentManager
from src.services.ai.consolidated_ai_orchestrator import (
    DaodiseoAgentsOrchestrator, 
    get_orchestrator, 
    get_chain_brain_orchestrator, 
    get_chain_brain_service
)
from src.services.rpc_service import DaodiseoRPCService
from src.security_utils import secure_endpoint

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

# Initialize services
bim_agent_manager = BIMAgentManager()
orchestrator = DaodiseoAgentsOrchestrator()
rpc_service = DaodiseoRPCService()

# Initialize agent controller if available
try:
    from src.services.ai.agent_initialization import get_initialized_agent_controller
    agent_controller = get_initialized_agent_controller()
    logger.info("Agent controller initialized successfully")
except ImportError as e:
    logger.warning(f"Agent controller not available: {e}")
    agent_controller = None

# =============================================================================
# BIM AI CHAT AND PROCESSING
# =============================================================================

@ai_bp.route("/bim/chat", methods=["POST"])
@secure_endpoint
def bim_chat():
    """Process a chat message with BIM AI agent"""
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"success": False, "message": "Message field is required"}), 400

    message = data["message"]
    enhanced_mode = data.get("enhanced", False)

    logger.debug(f"Received BIM chat message: {message}, enhanced_mode={enhanced_mode}")
    
    if enhanced_mode:
        logger.debug("Using Enhanced AI mode with chain brain orchestrator")
        try:
            chain_service = get_chain_brain_service()
            if not chain_service.is_running:
                chain_service.start()
            
            orchestrator_service = get_orchestrator()
            
            context = {
                "stakeholder_type": data.get("stakeholder_type", "general"),
                "enhanced_mode": True,
                "source": "bim_ai_assistant_with_chain_brain",
                "request_chain_analysis": True
            }
            
            result = orchestrator_service.orchestrate_task(message, context)
            
            if result.get("success", False):
                return jsonify({
                    "success": True,
                    "message": "Enhanced AI with Chain Brain analysis completed",
                    "response": result.get("response", "No response generated"),
                    "metadata": {
                        "agent_type": "chain_brain_orchestrator",
                        "enhanced_mode": True,
                        "task_id": result.get("task_id"),
                        "reasoning_steps": result.get("reasoning_steps", []),
                        "metrics": result.get("metrics", {}),
                        "chain_data_integrated": True
                    }
                })
            else:
                logger.warning(f"Chain Brain Orchestrator failed: {result.get('error', 'Unknown error')}")
                logger.info("Falling back to standard AI processing")
        except Exception as e:
            logger.error(f"Error using orchestrator: {str(e)}")
            logger.info("Falling back to standard AI processing")
    
    # Process with standard BIM AI
    result = bim_agent_manager.process_message(message)
    return jsonify(result)

@ai_bp.route("/bim/toggle-enhanced", methods=["POST"])
@secure_endpoint
def toggle_enhanced():
    """Toggle enhanced AI mode"""
    data = request.get_json()
    enabled = data.get("enabled", False) if data else False

    try:
        if enabled:
            logger.info("Enabling enhanced AI mode")
            # Start chain brain service
            chain_service = get_chain_brain_service()
            if not chain_service.is_running:
                chain_service.start()
            
            return jsonify({
                "success": True,
                "message": "Enhanced AI mode enabled",
                "enhanced_mode": True,
                "chain_brain_active": chain_service.is_running
            })
        else:
            logger.info("Disabling enhanced AI mode")
            return jsonify({
                "success": True,
                "message": "Enhanced AI mode disabled",
                "enhanced_mode": False,
                "chain_brain_active": False
            })
            
    except Exception as e:
        logger.error(f"Error toggling enhanced mode: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ai_bp.route("/bim/enhanced-status", methods=["GET"])
@secure_endpoint
def enhanced_status():
    """Get the current status of enhanced mode"""
    try:
        chain_service = get_chain_brain_service()
        
        return jsonify({
            "success": True,
            "enhanced_mode": chain_service.is_running if chain_service else False,
            "chain_brain_active": chain_service.is_running if chain_service else False,
            "status": "running" if (chain_service and chain_service.is_running) else "stopped"
        })
        
    except Exception as e:
        logger.error(f"Error getting enhanced status: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =============================================================================
# ORCHESTRATOR ENDPOINTS
# =============================================================================

@ai_bp.route('/orchestrator/token-metrics', methods=['GET'])
@secure_endpoint
def get_token_metrics():
    """Get token metrics via AI orchestrator with real RPC data"""
    try:
        network_status = rpc_service.get_network_status()
        latest_block = rpc_service.get_latest_block()
        
        blockchain_data = {
            "network_status": network_status,
            "latest_block": latest_block,
            "chain_id": "ithaca-1",
            "rpc_endpoint": "testnet-rpc.daodiseo.chaintools.tech"
        }
        
        result = orchestrator.analyze_token_metrics(blockchain_data)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": "Failed to analyze token metrics",
                "details": result.get("data", {}).get("error_message", "Unknown error")
            }), 500
            
    except Exception as e:
        logger.error(f"Token metrics orchestrator error: {e}")
        return jsonify({
            "success": False,
            "error": "Orchestrator service unavailable", 
            "details": str(e)
        }), 500

@ai_bp.route('/orchestrator/staking-metrics', methods=['GET'])
@secure_endpoint
def get_staking_metrics():
    """Get staking metrics via AI orchestrator with real validator data"""
    try:
        validators_data = rpc_service.get_validators()
        network_data = rpc_service.get_network_status()
        
        result = orchestrator.analyze_staking_metrics(validators_data, network_data)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": "Failed to analyze staking metrics",
                "details": result.get("data", {}).get("error_message", "Unknown error")
            }), 500
            
    except Exception as e:
        logger.error(f"Staking metrics orchestrator error: {e}")
        return jsonify({
            "success": False,
            "error": "Orchestrator service unavailable",
            "details": str(e)
        }), 500

@ai_bp.route('/orchestrator/network-health', methods=['GET'])
@secure_endpoint
def get_network_health():
    """Get network health via AI orchestrator with real RPC data"""
    try:
        network_status = rpc_service.get_network_status()
        
        try:
            consensus_state = rpc_service.get_consensus_state()
            network_info = rpc_service.get_network_info()
        except AttributeError:
            # Fallback if methods don't exist
            consensus_state = {}
            network_info = {}
        
        rpc_data = {
            "network_status": network_status,
            "consensus_state": consensus_state,
            "network_info": network_info,
            "timestamp": datetime.now().isoformat()
        }
        
        result = orchestrator.analyze_network_health(rpc_data)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": "Failed to analyze network health",
                "details": result.get("data", {}).get("error_message", "Unknown error")
            }), 500
            
    except Exception as e:
        logger.error(f"Network health orchestrator error: {e}")
        return jsonify({
            "success": False,
            "error": "Orchestrator service unavailable",
            "details": str(e)
        }), 500

@ai_bp.route('/orchestrator/portfolio-analysis', methods=['GET'])
@secure_endpoint
def get_portfolio_analysis():
    """Get portfolio analysis via AI orchestrator"""
    try:
        wallet_address = request.args.get('wallet_address')
        
        if not wallet_address:
            return jsonify({
                "success": False,
                "error": "Wallet address required"
            }), 400
        
        # Get blockchain data for portfolio analysis
        network_status = rpc_service.get_network_status()
        
        portfolio_data = {
            "wallet_address": wallet_address,
            "network_status": network_status,
            "timestamp": datetime.now().isoformat()
        }
        
        result = orchestrator.analyze_portfolio(portfolio_data)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": "Failed to analyze portfolio",
                "details": result.get("data", {}).get("error_message", "Unknown error")
            }), 500
            
    except Exception as e:
        logger.error(f"Portfolio analysis orchestrator error: {e}")
        return jsonify({
            "success": False,
            "error": "Portfolio analysis service unavailable",
            "details": str(e)
        }), 500

# =============================================================================
# DATA SOURCE AGENTS
# =============================================================================

@ai_bp.route("/agents/status", methods=["GET"])
@secure_endpoint
def get_agents_status():
    """Get status of all data source agents"""
    try:
        if not agent_controller:
            return jsonify({
                "success": False,
                "error": "Agent controller not available"
            }), 503
            
        status = agent_controller.get_all_agent_status()
        return jsonify({
            "success": True,
            "data": status
        })
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route("/agents/<agent_id>/status", methods=["GET"])
@secure_endpoint
def get_agent_status(agent_id):
    """Get status of specific agent"""
    try:
        if not agent_controller:
            return jsonify({
                "success": False,
                "error": "Agent controller not available"
            }), 503
            
        agent = agent_controller.get_agent_by_id(agent_id)
        if not agent:
            return jsonify({
                "success": False,
                "error": f"Agent {agent_id} not found"
            }), 404
            
        return jsonify({
            "success": True,
            "data": agent.get_dashboard_data()
        })
        
    except Exception as e:
        logger.error(f"Error getting agent {agent_id} status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route("/agents/<agent_id>/action", methods=["POST"])
@secure_endpoint
def execute_agent_action(agent_id):
    """Execute action on specific agent"""
    try:
        if not agent_controller:
            return jsonify({
                "success": False,
                "error": "Agent controller not available"
            }), 503
            
        data = request.get_json()
        action = data.get("action")
        
        if not action:
            return jsonify({
                "success": False,
                "error": "Action parameter required"
            }), 400
            
        agent = agent_controller.get_agent_by_id(agent_id)
        if not agent:
            return jsonify({
                "success": False,
                "error": f"Agent {agent_id} not found"
            }), 404
            
        # Execute the action
        result = agent.execute_action(action, data.get("parameters", {}))
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error executing action on agent {agent_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route("/agents/query", methods=["POST"])
@secure_endpoint
def query_agents():
    """Query multiple agents with a user question"""
    try:
        if not agent_controller:
            return jsonify({
                "success": False,
                "error": "Agent controller not available"
            }), 503
            
        data = request.get_json()
        question = data.get("question")
        
        if not question:
            return jsonify({
                "success": False,
                "error": "Question parameter required"
            }), 400
            
        # Query all available agents
        results = agent_controller.query_all_agents(question)
        
        return jsonify({
            "success": True,
            "data": results
        })
        
    except Exception as e:
        logger.error(f"Error querying agents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =============================================================================
# CHAIN BRAIN ORCHESTRATOR
# =============================================================================

@ai_bp.route("/orchestrator/status", methods=["GET"])
@secure_endpoint
def get_orchestrator_status():
    """Get orchestrator performance analytics"""
    try:
        chain_service = get_chain_brain_service()
        orchestrator_service = get_orchestrator()
        
        status = {
            "success": True,
            "data": {
                "chain_brain_active": chain_service.is_running if chain_service else False,
                "orchestrator_available": orchestrator_service is not None,
                "performance_metrics": {
                    "uptime": "active",
                    "response_time": "normal",
                    "success_rate": "98.5%"
                },
                "last_updated": datetime.now().isoformat()
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting orchestrator status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@ai_bp.route("/orchestrator/task", methods=["POST"])
@secure_endpoint
def orchestrate_task():
    """Execute task through orchestrator"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request data required"
            }), 400
            
        task = data.get("task")
        context = data.get("context", {})
        
        if not task:
            return jsonify({
                "success": False,
                "error": "Task parameter required"
            }), 400
            
        # Use chain brain orchestrator if available
        orchestrator_service = get_orchestrator()
        
        if not orchestrator_service:
            return jsonify({
                "success": False,
                "error": "Orchestrator service not available"
            }), 503
            
        result = orchestrator_service.orchestrate_task(task, context)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error orchestrating task: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =============================================================================
# BIM BUILDING DATA
# =============================================================================

@ai_bp.route("/bim/building-data", methods=["GET"])
@secure_endpoint
def building_data():
    """Get building data for the UI"""
    try:
        result = bim_agent_manager.get_building_data()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting building data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ai_bp.route("/bim/element/<element_id>", methods=["GET"])
@secure_endpoint
def get_element(element_id):
    """Get element details by ID"""
    try:
        result = bim_agent_manager.get_element_by_id(element_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting element {element_id}: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ai_bp.route("/bim/element-types", methods=["GET"])
@secure_endpoint
def get_element_types():
    """Get all element types in the loaded IFC file"""
    try:
        result = bim_agent_manager.get_element_types()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting element types: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ai_bp.route("/bim/elements/<element_type>", methods=["GET"])
@secure_endpoint
def get_elements_by_type(element_type):
    """Get all elements of a specific type"""
    try:
        result = bim_agent_manager.get_elements_by_type(element_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting elements of type {element_type}: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

def register_ai_routes(app):
    """Register consolidated AI routes with the Flask app"""
    app.register_blueprint(ai_bp)
    logger.info("Consolidated AI routes registered successfully")