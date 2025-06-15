"""
Dashboard Controller - Layer 2 Interface Adapter
Handles HTTP requests for dashboard metrics and converts them to/from domain objects.
"""
import asyncio
from typing import Dict, Any
from flask import Blueprint, jsonify, current_app

from src.layer1_use_cases.dashboard_metrics_use_case import DashboardMetricsUseCase
from src.layer2_interface_adapters.gateways.blockchain_gateway import BlockchainGateway
from src.security_utils import secure_endpoint


# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


class DashboardController:
    """
    Controller for dashboard-related HTTP endpoints.
    Orchestrates between HTTP layer and use cases.
    """
    
    def __init__(self):
        self.blockchain_gateway = BlockchainGateway()
        self.dashboard_use_case = DashboardMetricsUseCase(self.blockchain_gateway)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics.
        
        Returns:
            Dict containing all dashboard metrics
        """
        try:
            # Execute use case to get dashboard aggregate
            dashboard_aggregate = await self.dashboard_use_case.execute()
            
            # Convert to API response format
            return {
                "status": "success",
                "data": dashboard_aggregate.to_dict(),
                "timestamp": dashboard_aggregate.generated_at.isoformat()
            }
        
        except Exception as e:
            current_app.logger.error(f"Dashboard metrics error: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to retrieve dashboard metrics",
                "error": str(e)
            }


# Initialize controller
dashboard_controller = DashboardController()


@dashboard_bp.route('/metrics', methods=['GET'])
@secure_endpoint
def get_dashboard_metrics():
    """
    GET /api/dashboard/metrics
    
    Returns comprehensive dashboard metrics including:
    - ODIS token price and market data
    - Network health and block information  
    - Asset distribution and TVL
    - Featured hot asset
    """
    try:
        # Run async use case in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(dashboard_controller.get_metrics())
        loop.close()
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        current_app.logger.error(f"Dashboard endpoint error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "error": str(e)
        }), 500


@dashboard_bp.route('/health', methods=['GET'])
def dashboard_health():
    """
    GET /api/dashboard/health
    
    Quick health check for dashboard services
    """
    return jsonify({
        "status": "ok",
        "service": "dashboard",
        "endpoints": ["/metrics"]
    }), 200