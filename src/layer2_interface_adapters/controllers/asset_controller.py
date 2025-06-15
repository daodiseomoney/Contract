"""
Asset Controller - Clean Architecture Layer 2
Handles HTTP requests for asset and property management
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any
import logging

# Import use cases from Layer 1
try:
    from src.layer1_use_cases.tokenize_property import TokenizePropertyUseCase
    from src.layer1_use_cases.get_asset_metrics import GetAssetMetricsUseCase
except ImportError:
    # Fallback for development
    class TokenizePropertyUseCase:
        def execute(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "token_id": "PROP001",
                "contract_address": "0x1234...abcd",
                "total_tokens": 1000,
                "token_price": 1000.0,
                "status": "tokenized"
            }
    
    class GetAssetMetricsUseCase:
        def execute(self) -> Dict[str, Any]:
            return {
                "total_assets": 12,
                "total_value": 15600000,
                "assets_in_pipeline": 5,
                "tokenized_assets": 7,
                "avg_roi": 14.2
            }

LOG = logging.getLogger("daodiseo.asset_controller")

# Create Blueprint
bp = Blueprint('asset', __name__)

# Initialize use cases
tokenize_property_use_case = TokenizePropertyUseCase()
asset_metrics_use_case = GetAssetMetricsUseCase()

@bp.route('/asset-metrics', methods=['GET'])
def get_asset_metrics():
    """Get portfolio asset metrics"""
    try:
        result = asset_metrics_use_case.execute()
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting asset metrics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/hot-asset', methods=['GET'])
def get_hot_asset():
    """Get featured/hot asset information"""
    try:
        # This would use a FeaturedAssetUseCase in full implementation
        result = {
            "name": "Ithaca Village",
            "location": "Ithaca, NY",
            "property_type": "Residential Complex",
            "token_symbol": "ITHACA",
            "roi_percentage": 14.1,
            "total_value": 2500000,
            "available_tokens": 750,
            "total_tokens": 1000,
            "token_price": 2500.0,
            "image_url": "/assets/properties/ithaca-village.jpg",
            "features": ["Pool", "Gym", "Parking", "Garden"],
            "expected_return": "12-16% APY"
        }
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting hot asset: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/properties', methods=['GET'])
def get_properties():
    """Get list of available properties"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        property_type = request.args.get('type', None)
        
        # This would use a GetPropertiesUseCase in full implementation
        result = {
            "page": page,
            "limit": limit,
            "total": 25,
            "properties": [
                {
                    "id": "prop_001",
                    "name": "Ithaca Village",
                    "type": "residential",
                    "location": "Ithaca, NY",
                    "value": 2500000,
                    "roi": 14.1,
                    "status": "tokenized"
                },
                {
                    "id": "prop_002", 
                    "name": "Downtown Commercial Plaza",
                    "type": "commercial",
                    "location": "Austin, TX",
                    "value": 5200000,
                    "roi": 11.8,
                    "status": "pending"
                }
            ]
        }
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting properties: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/tokenize', methods=['POST'])
def tokenize_property():
    """Tokenize a property"""
    try:
        property_data = request.get_json()
        
        if not property_data:
            return jsonify({
                "success": False,
                "error": "Property data is required"
            }), 400
        
        result = tokenize_property_use_case.execute(property_data)
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error tokenizing property: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get user's investment portfolio"""
    try:
        # This would use a GetPortfolioUseCase in full implementation
        result = {
            "total_invested": 50000,
            "current_value": 57000,
            "total_return": 7000,
            "return_percentage": 14.0,
            "holdings": [
                {
                    "property": "Ithaca Village",
                    "tokens": 20,
                    "invested": 50000,
                    "current_value": 57000,
                    "return": 7000
                }
            ]
        }
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        LOG.error(f"Error getting portfolio: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500