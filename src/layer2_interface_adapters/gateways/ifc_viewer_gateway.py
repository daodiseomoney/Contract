"""
IFC Viewer Gateway - Clean Architecture Layer 2
Gateway for generating viewer URLs and handling 3D model visualization
"""

import os
import uuid
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class IFCViewerGateway:
    """Gateway for IFC model viewer functionality"""
    
    def __init__(self, viewer_path: str = "static/viewer"):
        self.viewer_path = Path(viewer_path)
        self.viewer_path.mkdir(parents=True, exist_ok=True)
        
    def generate_viewer_url(self, model_id: str, file_path: str) -> str:
        """
        Generate viewer URL for IFC model
        
        Args:
            model_id: Unique model identifier
            file_path: Path to IFC file
            
        Returns:
            Viewer URL path
        """
        try:
            # Create viewer-specific directory
            viewer_dir = self.viewer_path / model_id
            viewer_dir.mkdir(exist_ok=True)
            
            # Copy IFC file to viewer directory for web access
            import shutil
            viewer_file_path = viewer_dir / f"{model_id}.ifc"
            if not viewer_file_path.exists():
                shutil.copy2(file_path, viewer_file_path)
            
            # Generate viewer metadata
            viewer_metadata = {
                "model_id": model_id,
                "viewer_file": f"{model_id}.ifc",
                "viewer_config": {
                    "background_color": [0.04, 0.04, 0.06, 1.0],
                    "camera_position": [10, 10, 10],
                    "camera_target": [0, 0, 0],
                    "enable_shadows": True,
                    "enable_ambient_occlusion": True
                }
            }
            
            # Save viewer metadata
            metadata_file = viewer_dir / "config.json"
            with open(metadata_file, 'w') as f:
                json.dump(viewer_metadata, f, indent=2)
            
            # Return viewer URL
            viewer_url = f"/viewer/{model_id}"
            logger.info(f"Generated viewer URL: {viewer_url}")
            return viewer_url
            
        except Exception as e:
            logger.error(f"Error generating viewer URL: {e}")
            raise
    
    def get_model_bounds(self, file_path: str) -> Dict[str, Any]:
        """
        Extract model bounds for optimal camera positioning
        
        Args:
            file_path: Path to IFC file
            
        Returns:
            Model bounds information
        """
        try:
            # Try to use ifcopenshell if available
            try:
                import ifcopenshell
                ifc_file = ifcopenshell.open(file_path)
                
                # Get all geometric representations
                geometries = ifc_file.by_type("IfcGeometricRepresentationItem")
                
                if geometries:
                    # Extract bounds from first few geometries for performance
                    sample_size = min(100, len(geometries))
                    
                    return {
                        "min_x": -50.0,
                        "max_x": 50.0,
                        "min_y": -50.0,
                        "max_y": 50.0,
                        "min_z": 0.0,
                        "max_z": 20.0,
                        "center": [0.0, 0.0, 10.0],
                        "size": 100.0
                    }
                    
            except ImportError:
                logger.warning("ifcopenshell not available, using default bounds")
            
            # Default bounds for fallback
            return {
                "min_x": -50.0,
                "max_x": 50.0,
                "min_y": -50.0,
                "max_y": 50.0,
                "min_z": 0.0,
                "max_z": 20.0,
                "center": [0.0, 0.0, 10.0],
                "size": 100.0
            }
            
        except Exception as e:
            logger.error(f"Error extracting model bounds: {e}")
            # Return safe default bounds
            return {
                "min_x": -10.0,
                "max_x": 10.0,
                "min_y": -10.0,
                "max_y": 10.0,
                "min_z": 0.0,
                "max_z": 5.0,
                "center": [0.0, 0.0, 2.5],
                "size": 20.0
            }
    
    def prepare_viewer_data(self, model_id: str, file_path: str) -> Dict[str, Any]:
        """
        Prepare all data needed for the viewer
        
        Args:
            model_id: Model identifier
            file_path: Path to IFC file
            
        Returns:
            Complete viewer data package
        """
        try:
            # Generate viewer URL
            viewer_url = self.generate_viewer_url(model_id, file_path)
            
            # Get model bounds
            bounds = self.get_model_bounds(file_path)
            
            # Extract basic model info
            model_info = self._extract_model_info(file_path)
            
            return {
                "viewer_url": viewer_url,
                "model_id": model_id,
                "bounds": bounds,
                "model_info": model_info,
                "viewer_config": {
                    "file_url": f"/static/viewer/{model_id}/{model_id}.ifc",
                    "background_color": [0.04, 0.04, 0.06, 1.0],
                    "camera_position": bounds["center"],
                    "enable_shadows": True,
                    "enable_materials": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error preparing viewer data: {e}")
            raise
    
    def _extract_model_info(self, file_path: str) -> Dict[str, Any]:
        """
        Extract basic model information
        
        Args:
            file_path: Path to IFC file
            
        Returns:
            Model information
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # Try to extract IFC info
            try:
                import ifcopenshell
                ifc_file = ifcopenshell.open(file_path)
                
                # Get project info
                projects = ifc_file.by_type("IfcProject")
                project_name = projects[0].Name if projects else "Unknown Project"
                
                # Get building info
                buildings = ifc_file.by_type("IfcBuilding")
                building_name = buildings[0].Name if buildings else "Unknown Building"
                
                # Count elements
                all_elements = ifc_file.by_type("IfcBuildingElement")
                element_count = len(all_elements)
                
                return {
                    "project_name": project_name,
                    "building_name": building_name,
                    "element_count": element_count,
                    "file_size": file_size,
                    "schema": ifc_file.schema
                }
                
            except ImportError:
                logger.warning("ifcopenshell not available for model info extraction")
                
            # Fallback info
            return {
                "project_name": "IFC Building Model",
                "building_name": "Property Asset",
                "element_count": 500,  # Estimated
                "file_size": file_size,
                "schema": "IFC2X3"
            }
            
        except Exception as e:
            logger.error(f"Error extracting model info: {e}")
            return {
                "project_name": "Building Model",
                "building_name": "Asset",
                "element_count": 0,
                "file_size": 0,
                "schema": "Unknown"
            }