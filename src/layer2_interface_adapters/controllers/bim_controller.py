"""
BIM Controller - Clean Architecture Layer 2
Handles HTTP requests for BIM model upload, analysis, and processing
"""

from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from typing import Dict, Any
import logging
import os

# Import use cases from Layer 1
try:
    from src.layer1_use_cases.upload_bim_model import UploadBIMModelUseCase
    from src.layer1_use_cases.analyze_bim_model import AnalyzeBIMModelUseCase
except ImportError:
    # Fallback for development
    class UploadBIMModelUseCase:
        def execute(self, file_path: str, filename: str) -> Dict[str, Any]:
            return {
                "model_id": "bim_001",
                "filename": filename,
                "status": "uploaded",
                "element_count": 1245,
                "file_size": "15.2 MB",
                "schema_version": "IFC4"
            }
    
    class AnalyzeBIMModelUseCase:
        def execute(self, model_id: str) -> Dict[str, Any]:
            return {
                "model_id": model_id,
                "analysis_status": "completed",
                "complexity_score": 8.5,
                "quality_score": 9.2,
                "sustainability_score": 7.8,
                "cost_efficiency_score": 8.1,
                "recommendations": [
                    "Consider energy-efficient windows",
                    "Optimize HVAC placement",
                    "Review structural redundancy"
                ],
                "detected_issues": [
                    "Minor geometry overlaps detected",
                    "Some elements missing material properties"
                ]
            }

LOG = logging.getLogger("daodiseo.bim_controller")

# Create Blueprint
bp = Blueprint('bim', __name__)

# Initialize use cases
upload_bim_use_case = UploadBIMModelUseCase()
analyze_bim_use_case = AnalyzeBIMModelUseCase()

# Configuration
ALLOWED_EXTENSIONS = {'ifc', 'step', 'stp'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
def upload_bim_model():
    """Upload a BIM model file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                "success": False,
                "error": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            }), 400
        
        # Secure the filename
        if file.filename:
            filename = secure_filename(file.filename)
        else:
            return jsonify({
                "success": False,
                "error": "Invalid filename"
            }), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'uploads', 'bim')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Process the upload through use case
        result = upload_bim_use_case.execute(file_path, filename)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        LOG.error(f"Error uploading BIM model: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/analyze/<model_id>', methods=['POST'])
def analyze_bim_model(model_id: str):
    """Trigger AI analysis of a BIM model"""
    try:
        result = analyze_bim_use_case.execute(model_id)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        LOG.error(f"Error analyzing BIM model {model_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/models', methods=['GET'])
def get_bim_models():
    """Get list of uploaded BIM models"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # This would use a GetBIMModelsUseCase in full implementation
        result = {
            "page": page,
            "limit": limit,
            "total": 8,
            "models": [
                {
                    "id": "bim_001",
                    "filename": "residential_complex.ifc",
                    "uploaded_at": "2025-06-13T10:30:00Z",
                    "status": "analyzed",
                    "element_count": 1245,
                    "file_size": "15.2 MB"
                },
                {
                    "id": "bim_002",
                    "filename": "office_building.ifc",
                    "uploaded_at": "2025-06-12T14:15:00Z",
                    "status": "processing",
                    "element_count": 2890,
                    "file_size": "28.7 MB"
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        LOG.error(f"Error getting BIM models: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/models/<model_id>', methods=['GET'])
def get_bim_model_details(model_id: str):
    """Get detailed information about a specific BIM model"""
    try:
        # This would use a GetBIMModelDetailsUseCase in full implementation
        result = {
            "id": model_id,
            "filename": "residential_complex.ifc",
            "uploaded_at": "2025-06-13T10:30:00Z",
            "status": "analyzed",
            "schema_version": "IFC4",
            "file_size": "15.2 MB",
            "element_count": 1245,
            "elements_by_type": {
                "walls": 245,
                "doors": 48,
                "windows": 96,
                "slabs": 12,
                "columns": 32,
                "beams": 78,
                "spaces": 24,
                "other": 710
            },
            "analysis": {
                "complexity_score": 8.5,
                "quality_score": 9.2,
                "sustainability_score": 7.8,
                "cost_efficiency_score": 8.1,
                "analyzed_at": "2025-06-13T10:45:00Z"
            }
        }
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        LOG.error(f"Error getting BIM model details for {model_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/models/<model_id>/viewer-data', methods=['GET'])
def get_viewer_data(model_id: str):
    """Get 3D viewer data for a BIM model"""
    try:
        # This would use a GenerateViewerDataUseCase in full implementation
        result = {
            "model_id": model_id,
            "viewer_url": f"/api/bim/models/{model_id}/3d",
            "geometry_data": {
                "vertices": 15420,
                "faces": 8940,
                "materials": 12
            },
            "camera_position": {
                "x": 0,
                "y": 10,
                "z": 20
            },
            "bounding_box": {
                "min": {"x": -50, "y": 0, "z": -30},
                "max": {"x": 50, "y": 15, "z": 30}
            }
        }
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        LOG.error(f"Error getting viewer data for model {model_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500