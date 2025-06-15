"""
BIM Analysis Controller - Layer 2 Interface Adapter
Provides API endpoints for triggering BIM analysis orchestration
"""

import logging
from flask import Blueprint, jsonify, request
from src.layer2_interface_adapters.orchestrators.bim_analysis_orchestrator import BIMAnalysisOrchestrator
from src.security_utils import secure_endpoint

logger = logging.getLogger(__name__)

# Create blueprint
bim_analysis_bp = Blueprint("bim_analysis", __name__, url_prefix="/api/bim-analysis")

# Initialize orchestrator
bim_orchestrator = BIMAnalysisOrchestrator()

@bim_analysis_bp.route('/analyze/<model_id>', methods=['POST'])
@secure_endpoint
def analyze_building_model(model_id: str):
    """
    Trigger comprehensive BIM analysis using o3-mini and IfcOpenShell
    
    Args:
        model_id: Unique identifier for the building model
        
    Returns:
        Comprehensive analysis results with investment insights
    """
    try:
        data = request.get_json() or {}
        ifc_file_path = data.get('ifc_file_path')
        
        if not ifc_file_path:
            return jsonify({
                "success": False,
                "error": "IFC file path required",
                "error_type": "missing_parameter"
            }), 400
        
        # Trigger orchestrator workflow
        analysis_result = bim_orchestrator.analyze_building_model(model_id, ifc_file_path)
        
        if analysis_result.get("success", True) and analysis_result.get("status") != "failed":
            return jsonify({
                "success": True,
                "data": analysis_result
            })
        else:
            return jsonify({
                "success": False,
                "error": analysis_result.get("error_message", "Analysis failed"),
                "error_type": analysis_result.get("error_type", "analysis_error")
            }), 500
            
    except Exception as e:
        logger.error(f"BIM analysis controller error: {e}")
        return jsonify({
            "success": False,
            "error": "BIM analysis service unavailable",
            "error_type": "service_error"
        }), 500

@bim_analysis_bp.route('/status/<analysis_id>', methods=['GET'])
def get_analysis_status(analysis_id: str):
    """Get the status of a BIM analysis"""
    try:
        # In full implementation, would check analysis status from database
        # For now, return mock status
        return jsonify({
            "success": True,
            "data": {
                "analysis_id": analysis_id,
                "status": "completed",
                "progress": 100
            }
        })
        
    except Exception as e:
        logger.error(f"Analysis status error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def register_bim_analysis_routes(app):
    """Register BIM analysis routes with the Flask app"""
    app.register_blueprint(bim_analysis_bp)