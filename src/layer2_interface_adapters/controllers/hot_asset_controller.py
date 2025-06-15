"""
Hot Asset Controller - Clean Architecture Layer 2
REST API controller for hot asset data with IFC viewer integration
"""

import logging
from flask import Blueprint, jsonify, request
from src.layer1_use_cases.get_hot_asset_use_case import GetHotAssetUseCase
from src.layer2_interface_adapters.repositories.bim_repository import BIMRepository
from src.layer2_interface_adapters.gateways.ifc_viewer_gateway import IFCViewerGateway

logger = logging.getLogger(__name__)

# Initialize dependencies
bim_repository = BIMRepository()
ifc_viewer_gateway = IFCViewerGateway()
hot_asset_use_case = GetHotAssetUseCase(bim_repository, ifc_viewer_gateway)

# Create Blueprint
hot_asset_bp = Blueprint('hot_asset', __name__)


@hot_asset_bp.route('/api/hot_asset', methods=['GET'])
def get_hot_asset():
    """
    Get hot asset data with 3D model viewer URL
    
    Returns:
        JSON response with asset data and viewer information
    """
    try:
        # Execute use case
        result = hot_asset_use_case.execute()
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "data": {
                    "name": result["name"],
                    "project_name": result.get("project_name"),
                    "roi": result["roi"],
                    "viewer_url": result["viewer_url"],
                    "model_id": result.get("model_id"),
                    "element_count": result.get("element_count"),
                    "file_size_mb": result.get("file_size_mb"),
                    "schema": result.get("schema"),
                    "has_3d_model": result["viewer_url"] is not None,
                    "viewer_config": result.get("viewer_config")
                }
            }), 200
        else:
            return jsonify({
                "status": "warning",
                "data": {
                    "name": result["name"],
                    "roi": result["roi"],
                    "viewer_url": None,
                    "has_3d_model": False,
                    "message": result.get("message", "No 3D model available")
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error in get_hot_asset: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve hot asset data",
            "error": str(e)
        }), 500


@hot_asset_bp.route('/api/hot_asset/<model_id>/details', methods=['GET'])
def get_asset_details(model_id):
    """
    Get detailed asset information for a specific model
    
    Args:
        model_id: Model identifier
        
    Returns:
        JSON response with detailed asset information
    """
    try:
        result = hot_asset_use_case.get_asset_details(model_id)
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "data": result
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": result.get("error", "Asset not found")
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting asset details for {model_id}: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve asset details",
            "error": str(e)
        }), 500


@hot_asset_bp.route('/api/upload_ifc', methods=['POST'])
def upload_ifc_file():
    """
    Upload IFC file and process for hot asset integration
    
    Returns:
        JSON response with upload results
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file provided"
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
            
        # Validate file extension
        if not file.filename.lower().endswith('.ifc'):
            return jsonify({
                "status": "error",
                "message": "Only IFC files are supported"
            }), 400
            
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
            
        try:
            # Save to repository
            model_id = bim_repository.save_ifc_file(temp_path, file.filename)
            
            # Prepare viewer data
            stored_file_path = bim_repository.get_model_file_path(model_id)
            viewer_data = ifc_viewer_gateway.prepare_viewer_data(model_id, stored_file_path)
            
            return jsonify({
                "status": "success",
                "message": "IFC file uploaded and processed successfully",
                "data": {
                    "model_id": model_id,
                    "filename": file.filename,
                    "viewer_url": viewer_data["viewer_url"],
                    "model_info": viewer_data["model_info"]
                }
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Error uploading IFC file: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to upload IFC file",
            "error": str(e)
        }), 500


@hot_asset_bp.route('/viewer/<model_id>')
def viewer_page(model_id):
    """
    Serve the 3D viewer page for a specific model
    
    Args:
        model_id: Model identifier
        
    Returns:
        HTML viewer page
    """
    try:
        # Get model metadata
        metadata = bim_repository.get_model_metadata(model_id)
        if not metadata:
            return "Model not found", 404
            
        # Get viewer configuration
        file_path = metadata["file_path"]
        viewer_data = ifc_viewer_gateway.prepare_viewer_data(model_id, file_path)
        
        # Return simple viewer HTML for now
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>3D Model Viewer - {viewer_data['model_info']['building_name']}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ margin: 0; padding: 0; background: #0a0a0f; color: white; font-family: system-ui; }}
                #viewer {{ width: 100vw; height: 100vh; }}
                .info {{ position: absolute; top: 20px; left: 20px; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div id="viewer">
                <div class="info">
                    <h3>{viewer_data['model_info']['building_name']}</h3>
                    <p>Elements: {viewer_data['model_info']['element_count']}</p>
                    <p>Schema: {viewer_data['model_info']['schema']}</p>
                    <p>Size: {viewer_data['model_info']['file_size'] / (1024*1024):.1f} MB</p>
                </div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <h2>3D Viewer Integration</h2>
                    <p>Model ID: {model_id}</p>
                    <p>Ready for xeokit or Three.js integration</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        logger.error(f"Error serving viewer page for {model_id}: {e}")
        return f"Error loading viewer: {e}", 500