"""
Viewer Orchestrator - Layer 2 Interface Adapter
Coordinates IFC parsing, geometry extraction, and 3D mesh generation for authentic building rendering
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from src.layer2_interface_adapters.gateways.ifc.ifc_parser import IFCParser
from src.layer2_interface_adapters.repositories.bim_repository import BIMRepository
from src.layer1_entities.building import Building
from src.layer1_entities.ifc_model import IfcModel

logger = logging.getLogger(__name__)


class ViewerOrchestrator:
    """
    Orchestrates authentic IFC geometry rendering by bridging IFC parsing 
    with Three.js mesh generation for real building visualization
    """
    
    def __init__(self):
        self.bim_repo = BIMRepository()
        self.parser = IFCParser()
        
    def run(self, model_id: str) -> Dict[str, Any]:
        """
        Main orchestration method that processes IFC file and returns 
        authentic building geometry data for Three.js rendering
        
        Args:
            model_id: Unique identifier for the IFC model
            
        Returns:
            Dict containing scene data, camera config, and building insights
        """
        try:
            # 1. Retrieve IFC file path
            file_path = self.bim_repo.get_file_path(model_id)
            if not file_path or not Path(file_path).exists():
                file_path = self._get_default_ifc_file()
            
            # 2. Parse full IFC model
            logger.info(f"Parsing IFC model: {file_path}")
            ifc_model: IfcModel = self.parser.parse(file_path)
            
            if not ifc_model or not ifc_model.buildings:
                return self._create_fallback_response()
            
            # 3. Select the primary building instance
            building: Building = ifc_model.buildings[0]
            logger.info(f"Processing building: {building.name} with {len(building.elements)} elements")
            
            # 4. Extract authentic geometry data
            mesh_data = self._extract_mesh_data(building)
            
            # 5. Generate camera configuration based on building bounds
            camera_config = self._setup_camera(building.bounds)
            
            # 6. Create scene metadata for Three.js
            scene_data = self._export_scene_metadata(building, mesh_data)
            
            # 7. Generate building insights
            insights = self._analyze_building_structure(building)
            
            return {
                "success": True,
                "scene": scene_data,
                "camera": camera_config,
                "insights": insights,
                "building_metadata": {
                    "name": building.name,
                    "total_elements": len(building.elements),
                    "floors": building.floor_count,
                    "area_sqft": building.total_area,
                    "complexity": building.complexity_level
                }
            }
            
        except Exception as e:
            logger.error(f"ViewerOrchestrator error: {e}")
            return self._create_error_response(str(e))
    
    def _get_default_ifc_file(self) -> str:
        """Get the default TOP_RVT_V2.ifc file path"""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        return str(project_root / "attached_assets" / "TOP_RVT_V2_1750006296430.ifc")
    
    def _extract_mesh_data(self, building: Building) -> Dict[str, Any]:
        """
        Extract authentic mesh data from Building entity for Three.js rendering
        
        Args:
            building: Building entity with IFC elements
            
        Returns:
            Mesh data structure for Three.js
        """
        try:
            # Group elements by type for optimized rendering
            mesh_groups = {
                "structure": [],
                "walls": [],
                "floors": [],
                "roofs": [],
                "windows": [],
                "doors": []
            }
            
            for element in building.elements:
                mesh_group = self._categorize_element(element.type)
                if mesh_group in mesh_groups:
                    # Generate Three.js compatible geometry from authentic IFC element
                    geometry = self._create_element_geometry(element)
                    material = self._get_element_material(element)
                    
                    mesh_groups[mesh_group].append({
                        "id": element.id,
                        "type": element.type,
                        "name": element.name,
                        "level": element.level,
                        "geometry": geometry,
                        "material": material,
                        "position": element.position,
                        "rotation": element.rotation
                    })
            
            return {
                "groups": mesh_groups,
                "total_triangles": sum(len(group) for group in mesh_groups.values()),
                "bounds": building.bounds,
                "coordinate_system": getattr(building, 'coordinate_system', 'local')
            }
            
        except Exception as e:
            logger.error(f"Mesh extraction error: {e}")
            return self._create_fallback_mesh()
    
    def _categorize_element(self, element_type: str) -> str:
        """Categorize IFC element types for grouped rendering"""
        type_mapping = {
            "IfcWall": "walls",
            "IfcSlab": "floors", 
            "IfcRoof": "roofs",
            "IfcWindow": "windows",
            "IfcDoor": "doors",
            "IfcBeam": "structure",
            "IfcColumn": "structure"
        }
        return type_mapping.get(element_type, "structure")
    
    def _create_element_geometry(self, element) -> Dict[str, Any]:
        """Pass through authentic IFC geometry from IFCParser"""
        try:
            # Use authentic geometry data extracted by IFCParser with IfcOpenShell
            if hasattr(element, 'geometry_data') and element.geometry_data:
                geometry_data = element.geometry_data
                
                # Check if we have authentic IFC geometry
                if geometry_data.get('has_authentic_geometry', False):
                    logger.debug(f"Using authentic IFC geometry for element {element.id}")
                    return {
                        "type": geometry_data.get('type', 'BufferGeometry'),
                        "vertices": geometry_data.get('vertices', []),
                        "faces": geometry_data.get('faces', []),
                        "parameters": geometry_data.get('parameters', {}),
                        "has_authentic_geometry": True,
                        "vertex_count": geometry_data.get('vertex_count', 0),
                        "face_count": geometry_data.get('face_count', 0)
                    }
                
                # Use fallback geometry if available
                elif geometry_data.get('vertices') and geometry_data.get('faces'):
                    logger.debug(f"Using fallback geometry for element {element.id}")
                    return {
                        "type": geometry_data.get('type', 'BoxGeometry'),
                        "vertices": geometry_data.get('vertices', []),
                        "faces": geometry_data.get('faces', []),
                        "parameters": geometry_data.get('parameters', {}),
                        "has_authentic_geometry": False,
                        "vertex_count": geometry_data.get('vertex_count', 0),
                        "face_count": geometry_data.get('face_count', 0)
                    }
            
            # Final fallback - should not reach here with proper IFC parsing
            logger.warning(f"No geometry data available for element {element.id}, using minimal fallback")
            return {
                "type": "BoxGeometry",
                "parameters": {"width": 1, "height": 1, "depth": 1},
                "vertices": [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
                           [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]],
                "faces": [[0, 1, 2], [0, 2, 3], [4, 7, 6], [4, 6, 5], [0, 4, 5], [0, 5, 1],
                         [2, 6, 7], [2, 7, 3], [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2]],
                "has_authentic_geometry": False
            }
            
        except Exception as e:
            logger.error(f"Error processing geometry for element {element.id}: {e}")
            return {
                "type": "BoxGeometry",
                "parameters": {"width": 1, "height": 1, "depth": 1},
                "vertices": [],
                "faces": [],
                "has_authentic_geometry": False
            }
    
    def _get_element_material(self, element) -> Dict[str, Any]:
        """Get material properties for element rendering"""
        try:
            # Default materials by element type
            material_map = {
                "IfcWall": {"color": "#E0E0E0", "opacity": 0.9, "type": "concrete"},
                "IfcSlab": {"color": "#C0C0C0", "opacity": 0.9, "type": "concrete"},
                "IfcColumn": {"color": "#808080", "opacity": 0.9, "type": "concrete"},
                "IfcBeam": {"color": "#A0A0A0", "opacity": 0.9, "type": "steel"},
                "IfcWindow": {"color": "#87CEEB", "opacity": 0.7, "type": "glass"},
                "IfcDoor": {"color": "#8B4513", "opacity": 0.9, "type": "wood"},
                "IfcRoof": {"color": "#654321", "opacity": 0.9, "type": "tile"}
            }
            
            base_material = material_map.get(element.type, {
                "color": "#CCCCCC", 
                "opacity": 0.8,
                "type": "generic"
            })
            
            # Override with element-specific material if available
            if element.material_properties and "type" in element.material_properties:
                base_material["type"] = element.material_properties["type"]
            
            return {
                "color": base_material["color"],
                "opacity": base_material["opacity"],
                "material_type": base_material["type"],
                "wireframe": False,
                "transparent": base_material["opacity"] < 1.0
            }
            
        except Exception as e:
            logger.error(f"Error getting material for element {element.id}: {e}")
            return {
                "color": "#CCCCCC",
                "opacity": 0.8,
                "material_type": "generic",
                "wireframe": False,
                "transparent": False
            }
    
    def _generate_box_vertices(self, dimensions: List[float]) -> List[List[float]]:
        """Generate vertices for a box geometry"""
        w, h, d = dimensions[0]/2, dimensions[1]/2, dimensions[2]/2
        return [
            [-w, -h, -d], [w, -h, -d], [w, h, -d], [-w, h, -d],  # bottom face
            [-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d]       # top face
        ]
    
    def _generate_box_faces(self) -> List[List[int]]:
        """Generate face indices for a box geometry"""
        return [
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 7, 6], [4, 6, 5],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2]   # right
        ]
    
    def _setup_camera(self, bounds: Dict[str, float]) -> Dict[str, Any]:
        """Generate optimal camera configuration based on building bounds"""
        try:
            # Calculate building dimensions
            width = bounds["max_x"] - bounds["min_x"]
            height = bounds["max_y"] - bounds["min_y"]
            depth = bounds["max_z"] - bounds["min_z"]
            
            # Position camera to view entire building
            max_dim = max(width, height, depth)
            camera_distance = max_dim * 1.5
            
            # Center point of building
            center = [
                (bounds["max_x"] + bounds["min_x"]) / 2,
                (bounds["max_y"] + bounds["min_y"]) / 2,
                (bounds["max_z"] + bounds["min_z"]) / 2
            ]
            
            return {
                "position": [
                    center[0] + camera_distance,
                    center[1] + camera_distance * 0.8,
                    center[2] + camera_distance
                ],
                "target": center,
                "fov": 75,
                "near": 0.1,
                "far": camera_distance * 10
            }
            
        except Exception as e:
            logger.error(f"Camera setup error: {e}")
            return {
                "position": [60, 40, 60],
                "target": [0, 10, 0],
                "fov": 75,
                "near": 0.1,
                "far": 1000
            }
    
    def _export_scene_metadata(self, building: Building, mesh_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export scene metadata for Three.js renderer"""
        return {
            "type": "authentic_ifc_building",
            "building_id": building.id,
            "mesh_data": mesh_data,
            "lighting": {
                "ambient": {"color": 0x404040, "intensity": 0.6},
                "directional": {
                    "color": 0xffffff,
                    "intensity": 0.8,
                    "position": [50, 50, 50],
                    "cast_shadow": True
                }
            },
            "materials": {
                "concrete": {"color": 0x4a5568, "opacity": 0.9},
                "steel": {"color": 0x718096, "metalness": 0.8},
                "glass": {"color": 0x90cdf4, "opacity": 0.3, "transparent": True},
                "wood": {"color": 0x8b4513, "roughness": 0.8}
            }
        }
    
    def _analyze_building_structure(self, building: Building) -> Dict[str, Any]:
        """Generate structural insights for the building"""
        return {
            "architectural_style": building.architectural_style,
            "construction_type": building.construction_type,
            "structural_elements": len([e for e in building.elements if e.is_structural]),
            "non_structural_elements": len([e for e in building.elements if not e.is_structural]),
            "complexity_score": building.complexity_score,
            "bim_maturity_level": building.bim_maturity
        }
    
    def _create_fallback_mesh(self) -> Dict[str, Any]:
        """Create fallback mesh when IFC parsing fails"""
        return {
            "groups": {
                "structure": [{
                    "id": "fallback_building",
                    "type": "IfcBuilding",
                    "geometry": {
                        "type": "box",
                        "dimensions": [40, 25, 20]
                    },
                    "material": {"color": 0x9333ea},
                    "position": [0, 12.5, 0],
                    "rotation": [0, 0, 0]
                }]
            },
            "total_triangles": 12,
            "bounds": {"min_x": -20, "max_x": 20, "min_y": 0, "max_y": 25, "min_z": -10, "max_z": 10}
        }
    
    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create fallback response when no building data available"""
        return {
            "success": False,
            "scene": self._export_scene_metadata(None, self._create_fallback_mesh()),
            "camera": self._setup_camera({"min_x": -20, "max_x": 20, "min_y": 0, "max_y": 25, "min_z": -10, "max_z": 10}),
            "insights": {"error": "No building data available"},
            "building_metadata": {
                "name": "Fallback Building",
                "total_elements": 1,
                "complexity": "simple"
            }
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "success": False,
            "error": error_message,
            "scene": None,
            "camera": None,
            "insights": None
        }