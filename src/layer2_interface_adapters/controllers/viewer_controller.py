"""
Viewer Controller - Layer 2 Interface Adapter
REST API controller for authentic IFC building visualization
"""

from flask import Blueprint, request, jsonify
import logging
from pathlib import Path
from src.layer2_interface_adapters.orchestrators.viewer_orchestrator import ViewerOrchestrator

logger = logging.getLogger(__name__)

# Create Blueprint for viewer endpoints
viewer_bp = Blueprint('viewer', __name__)

@viewer_bp.route('/api/viewer/<model_id>', methods=['GET'])
def get_viewer_data(model_id: str):
    """
    Get authentic IFC building data for 3D visualization
    
    Args:
        model_id: Unique model identifier
        
    Returns:
        JSON containing scene data, camera config, and building insights
    """
    try:
        orchestrator = ViewerOrchestrator()
        result = orchestrator.run(model_id)
        
        logger.info(f"Viewer data generated for model: {model_id}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Viewer API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Viewer failed: {str(e)}"
        }), 500

@viewer_bp.route('/api/viewer/ifc-geometry/<model_id>', methods=['GET'])
def get_ifc_geometry(model_id: str):
    """
    Get raw IFC geometry data for Three.js mesh creation
    
    Args:
        model_id: Unique model identifier
        
    Returns:
        JSON containing mesh groups and triangulation data
    """
    try:
        orchestrator = ViewerOrchestrator()
        result = orchestrator.run(model_id)
        
        if result.get("success") and result.get("scene"):
            geometry_data = {
                "success": True,
                "mesh_groups": result["scene"]["mesh_data"]["groups"],
                "bounds": result["scene"]["mesh_data"]["bounds"],
                "total_triangles": result["scene"]["mesh_data"]["total_triangles"],
                "building_metadata": result.get("building_metadata", {})
            }
            return jsonify(geometry_data)
        else:
            return jsonify({"success": False, "error": "No geometry data available"}), 404
            
    except Exception as e:
        logger.error(f"IFC geometry API error: {e}")
        return jsonify({
            "success": False,
            "error": f"Geometry extraction failed: {str(e)}"
        }), 500