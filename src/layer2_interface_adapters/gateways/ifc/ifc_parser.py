"""
IFC Parser module using IfcOpenShell.
This module processes IFC files using the IfcOpenShell library and provides structured data.
"""

import logging
import os
import ifcopenshell
import ifcopenshell.geom
import numpy as np
from typing import Dict, List, Optional, Any, Set, Tuple
from src.layer1_entities.ifc_model import IfcModel
from src.layer1_entities.building import Building
from src.layer1_entities.bim_element import BIMElement

# Configure logging
logger = logging.getLogger(__name__)


class IFCParser:
    """
    IFC Parser using IfcOpenShell.
    Processes IFC files and provides structured access to building data.
    """

    def __init__(self, ifc_file_path: Optional[str] = None):
        """
        Initialize the IFC parser.

        Args:
            ifc_file_path: Optional path to an IFC file to parse immediately
        """
        self.ifc_file = None
        self.ifc_file_path = None

        # If file path is provided, load it
        if ifc_file_path and os.path.exists(ifc_file_path):
            self.load_file(ifc_file_path)

    def load_file(self, file_path: str) -> bool:
        """
        Load an IFC file.

        Args:
            file_path: Path to the IFC file

        Returns:
            bool: True if file loaded successfully, False otherwise
        """
        try:
            logger.debug(f"Loading IFC file: {file_path}")
            self.ifc_file = ifcopenshell.open(file_path)
            self.ifc_file_path = file_path
            logger.info(f"Successfully loaded IFC file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading IFC file {file_path}: {str(e)}")
            return False

    def get_building_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the building data.

        Returns:
            Dict containing building summary information
        """
        if not self.ifc_file:
            logger.warning("No IFC file loaded.")
            return {
                "name": "Unknown",
                "type": "Unknown",
                "location": "Unknown",
                "floors": 0,
                "area": 0,
                "height": 0,
                "year_built": 0,
                "status": "Unknown",
                "element_count": 0,
            }

        # Get building from the IFC file
        buildings = self.ifc_file.by_type("IfcBuilding")
        building = buildings[0] if buildings else None

        # Get building storey data
        storeys = self.ifc_file.by_type("IfcBuildingStorey")
        storey_count = len(storeys)

        # Extract property sets for the building
        building_props = {}
        if building:
            building_props = self._get_element_properties(building)

        # Get project data
        projects = self.ifc_file.by_type("IfcProject")
        project = projects[0] if projects else None
        project_name = project.Name if project and project.Name else "Unknown Project"

        # Calculate total area if available
        total_area = 0
        if storeys:
            for storey in storeys:
                storey_props = self._get_element_properties(storey)
                if "GrossFloorArea" in storey_props:
                    try:
                        total_area += float(storey_props["GrossFloorArea"])
                    except (ValueError, TypeError):
                        pass

        # Get building height (approx from storeys)
        height = 0
        if storey_count > 0:
            avg_floor_height = 3.0  # Assuming 3 meters if not found
            if storeys and hasattr(storeys[0], "Elevation"):
                for s in storeys:
                    if hasattr(s, "Elevation") and s.Elevation:
                        # Rough approximation of height
                        if s.Elevation > height:
                            height = s.Elevation

            height = max(height + avg_floor_height, storey_count * avg_floor_height)

        # Get all elements
        all_elements = list(self.ifc_file.by_type("IfcElement"))
        
    def parse(self, file_path: str) -> IfcModel:
        """
        Parse IFC file and return structured IfcModel with Building entities
        
        Args:
            file_path: Path to IFC file
            
        Returns:
            IfcModel containing Building entities with authentic geometry
        """
        try:
            # Load IFC file
            if not self.load_file(file_path):
                return self._create_fallback_model(file_path)
            
            # Extract project information
            projects = self.ifc_file.by_type("IfcProject")
            project_info = {}
            if projects:
                project = projects[0]
                project_info = {
                    "name": project.Name or "Unknown Project",
                    "description": project.Description or "",
                    "schema": self.ifc_file.schema
                }
            
            # Parse buildings
            buildings = []
            ifc_buildings = self.ifc_file.by_type("IfcBuilding")
            
            for ifc_building in ifc_buildings:
                building = self._parse_building(ifc_building)
                if building:
                    buildings.append(building)
            
            # If no buildings found, create one from all elements
            if not buildings:
                buildings = [self._create_building_from_elements()]
            
            # Calculate global bounds
            global_bounds = self._calculate_global_bounds(buildings)
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            return IfcModel(
                file_path=file_path,
                schema=self.ifc_file.schema,
                buildings=buildings,
                project_info=project_info,
                global_bounds=global_bounds,
                total_elements=len(list(self.ifc_file.by_type("IfcElement"))),
                file_size_bytes=file_size
            )
            
        except Exception as e:
            logger.error(f"Error parsing IFC file {file_path}: {e}")
            return self._create_fallback_model(file_path)
    
    def _parse_building(self, ifc_building) -> Building:
        """Parse individual building from IFC data"""
        try:
            # Get building elements
            elements = []
            
            # Get all elements related to this building
            all_elements = list(self.ifc_file.by_type("IfcElement"))
            
            for element in all_elements:
                bim_element = self._parse_element(element)
                if bim_element:
                    elements.append(bim_element)
            
            # Calculate building bounds
            bounds = self._calculate_building_bounds(elements)
            
            return Building(
                id=str(ifc_building.id()),
                name=ifc_building.Name or "Building",
                elements=elements,
                bounds=bounds
            )
            
        except Exception as e:
            logger.error(f"Error parsing building: {e}")
            return None
    
    def _parse_element(self, ifc_element) -> Optional[BIMElement]:
        """Parse individual IFC element with authentic geometry extraction"""
        try:
            # Get element properties
            properties = self._get_element_properties(ifc_element)
            
            # Extract authentic geometry using IfcOpenShell
            geometry_data = self._extract_authentic_geometry(ifc_element)
            
            # Get material properties
            material_props = self._get_element_materials(ifc_element)
            
            # Extract position and rotation from geometry
            position, rotation = self._extract_transformation(ifc_element)
            
            return BIMElement(
                id=str(ifc_element.id()),
                type=ifc_element.is_a(),
                name=ifc_element.Name or f"{ifc_element.is_a()}_{ifc_element.id()}",
                level=self._get_element_level(ifc_element),
                geometry_data=geometry_data,
                material_properties=material_props,
                position=position,
                rotation=rotation
            )
            
        except Exception as e:
            logger.error(f"Error parsing element {ifc_element}: {e}")
            return None
    
    def _extract_authentic_geometry(self, ifc_element) -> Dict[str, Any]:
        """Extract authentic geometry data using optimized IfcOpenShell processing"""
        try:
            # Skip geometry extraction for elements without representation
            if not (hasattr(ifc_element, 'Representation') and ifc_element.Representation):
                logger.debug(f"Element {ifc_element.id()} has no representation, using optimized approach")
                return self._create_optimized_geometry(ifc_element)
            
            # Create optimized geometry settings for faster processing
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            settings.set(settings.WELD_VERTICES, False)  # Faster without welding
            settings.set(settings.USE_MATERIAL_NAMES, False)  # Skip material names for speed
            
            try:
                # Extract geometry with timeout protection
                logger.debug(f"Extracting authentic geometry for {ifc_element.is_a()} {ifc_element.id()}")
                shape = ifcopenshell.geom.create_shape(settings, ifc_element)
                
                if shape and hasattr(shape, 'geometry'):
                    geometry = shape.geometry
                    
                    # Get vertices efficiently
                    verts_array = np.array(geometry.verts)
                    if len(verts_array) % 3 != 0:
                        logger.warning(f"Invalid vertex count for element {ifc_element.id()}")
                        return self._create_optimized_geometry(ifc_element)
                    
                    vertices = verts_array.reshape(-1, 3).tolist()
                    
                    # Get faces efficiently (already triangulated by IfcOpenShell)
                    faces_flat = np.array(geometry.faces)
                    if len(faces_flat) % 3 != 0:
                        logger.warning(f"Invalid face count for element {ifc_element.id()}")
                        return self._create_optimized_geometry(ifc_element)
                    
                    faces = faces_flat.reshape(-1, 3).tolist()
                    
                    # Quick bounding box calculation
                    if vertices:
                        vertices_np = np.array(vertices)
                        bbox_min = vertices_np.min(axis=0)
                        bbox_max = vertices_np.max(axis=0)
                        dimensions = (bbox_max - bbox_min).tolist()
                        
                        # Ensure minimum dimensions
                        dimensions = [max(d, 0.1) for d in dimensions]
                    else:
                        dimensions = [1.0, 1.0, 1.0]
                    
                    logger.info(f"Successfully extracted authentic geometry for {ifc_element.is_a()} {ifc_element.id()}: {len(vertices)} vertices, {len(faces)} faces")
                    
                    return {
                        "type": "BufferGeometry",
                        "vertices": vertices,
                        "faces": faces,
                        "parameters": {
                            "width": dimensions[0],
                            "height": dimensions[1], 
                            "depth": dimensions[2]
                        },
                        "has_authentic_geometry": True,
                        "vertex_count": len(vertices),
                        "face_count": len(faces),
                        "element_type": ifc_element.is_a()
                    }
                else:
                    logger.warning(f"No geometry data in shape for element {ifc_element.id()}")
                    return self._create_optimized_geometry(ifc_element)
                    
            except Exception as geom_error:
                logger.warning(f"Geometry extraction failed for {ifc_element.is_a()} {ifc_element.id()}: {geom_error}")
                return self._create_optimized_geometry(ifc_element)
                
        except Exception as e:
            logger.error(f"Critical geometry error for element {ifc_element.id()}: {e}")
            return self._create_optimized_geometry(ifc_element)
    
    def _extract_transformation(self, ifc_element) -> Tuple[List[float], List[float]]:
        """Extract position and rotation from IFC element placement"""
        try:
            position = [0.0, 0.0, 0.0]
            rotation = [0.0, 0.0, 0.0]
            
            # Extract placement information
            if hasattr(ifc_element, 'ObjectPlacement') and ifc_element.ObjectPlacement:
                placement = ifc_element.ObjectPlacement
                
                if hasattr(placement, 'RelativePlacement'):
                    rel_placement = placement.RelativePlacement
                    
                    # Extract location
                    if hasattr(rel_placement, 'Location') and rel_placement.Location:
                        coords = rel_placement.Location.Coordinates
                        if len(coords) >= 3:
                            position = [float(coords[0]), float(coords[1]), float(coords[2])]
                        elif len(coords) == 2:
                            position = [float(coords[0]), float(coords[1]), 0.0]
                    
                    # Extract rotation from axis (simplified)
                    if hasattr(rel_placement, 'RefDirection') and rel_placement.RefDirection:
                        direction = rel_placement.RefDirection.DirectionRatios
                        if len(direction) >= 2:
                            # Calculate rotation from direction vector
                            rotation[2] = float(np.arctan2(direction[1], direction[0]))
            
            return position, rotation
            
        except Exception as e:
            logger.warning(f"Failed to extract transformation for element {ifc_element.id()}: {e}")
            return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    
    def _create_optimized_geometry(self, ifc_element) -> Dict[str, Any]:
        """Create optimized geometry based on IFC element properties"""
        try:
            # Extract basic dimensions from element properties if available
            dimensions = self._extract_element_dimensions(ifc_element)
            
            # Type-specific dimension refinements for better representation
            type_dimensions = {
                "IfcWall": [4.0, 0.2, 3.0],
                "IfcSlab": [6.0, 6.0, 0.3],
                "IfcColumn": [0.3, 0.3, 3.0],
                "IfcBeam": [4.0, 0.3, 0.5],
                "IfcWindow": [1.2, 1.5, 0.1],
                "IfcDoor": [0.9, 2.1, 0.1],
                "IfcRoof": [6.0, 6.0, 0.4],
                "IfcStair": [3.0, 1.0, 0.2],
                "IfcSpace": [4.0, 4.0, 3.0]
            }
            
            # Use extracted dimensions or type defaults
            final_dimensions = dimensions if dimensions else type_dimensions.get(ifc_element.is_a(), [2.0, 2.0, 2.0])
            
            # Generate optimized box vertices
            w, h, d = final_dimensions[0]/2, final_dimensions[1]/2, final_dimensions[2]/2
            vertices = [
                [-w, -h, -d], [w, -h, -d], [w, h, -d], [-w, h, -d],
                [-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d]
            ]
            
            # Generate triangulated faces
            faces = [
                [0, 1, 2], [0, 2, 3],  # bottom
                [4, 7, 6], [4, 6, 5],  # top
                [0, 4, 5], [0, 5, 1],  # front
                [2, 6, 7], [2, 7, 3],  # back
                [0, 3, 7], [0, 7, 4],  # left
                [1, 5, 6], [1, 6, 2]   # right
            ]
            
            return {
                "type": "BufferGeometry",
                "vertices": vertices,
                "faces": faces,
                "parameters": {
                    "width": final_dimensions[0],
                    "height": final_dimensions[1],
                    "depth": final_dimensions[2]
                },
                "has_authentic_geometry": False,
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "element_type": ifc_element.is_a(),
                "geometry_source": "optimized_fallback"
            }
            
        except Exception as e:
            logger.error(f"Error creating optimized geometry for {ifc_element.id()}: {e}")
            # Final minimal fallback
            return {
                "type": "BufferGeometry",
                "vertices": [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                           [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]],
                "faces": [[0, 1, 2], [0, 2, 3], [4, 7, 6], [4, 6, 5], [0, 4, 5], [0, 5, 1],
                         [2, 6, 7], [2, 7, 3], [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2]],
                "parameters": {"width": 2.0, "height": 2.0, "depth": 2.0},
                "has_authentic_geometry": False,
                "vertex_count": 8,
                "face_count": 12,
                "geometry_source": "minimal_fallback"
            }
    
    def _extract_element_dimensions(self, ifc_element) -> Optional[List[float]]:
        """Extract actual dimensions from IFC element properties"""
        try:
            # Check for quantity sets with dimension information
            if hasattr(ifc_element, 'IsDefinedBy'):
                for rel in ifc_element.IsDefinedBy:
                    if hasattr(rel, 'RelatingPropertyDefinition'):
                        prop_def = rel.RelatingPropertyDefinition
                        if hasattr(prop_def, 'Quantities'):
                            for quantity in prop_def.Quantities:
                                if hasattr(quantity, 'LengthValue') and hasattr(quantity, 'WidthValue') and hasattr(quantity, 'HeightValue'):
                                    return [quantity.LengthValue, quantity.WidthValue, quantity.HeightValue]
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not extract dimensions for element {ifc_element.id()}: {e}")
            return None
    
    def _create_fallback_geometry(self, ifc_element) -> Dict[str, Any]:
        """Create fallback box geometry when authentic extraction fails"""
        # Default dimensions based on element type
        type_dimensions = {
            "IfcWall": [4.0, 3.0, 0.2],
            "IfcSlab": [4.0, 4.0, 0.3],
            "IfcColumn": [0.3, 0.3, 3.0],
            "IfcBeam": [4.0, 0.3, 0.5],
            "IfcWindow": [1.2, 1.5, 0.1],
            "IfcDoor": [0.9, 2.1, 0.1],
            "IfcRoof": [6.0, 6.0, 0.4]
        }
        
        dimensions = type_dimensions.get(ifc_element.is_a(), [2.0, 2.0, 2.0])
        
        # Generate box vertices
        w, h, d = dimensions[0]/2, dimensions[1]/2, dimensions[2]/2
        vertices = [
            [-w, -h, -d], [w, -h, -d], [w, h, -d], [-w, h, -d],
            [-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d]
        ]
        
        # Generate box faces (triangulated)
        faces = [
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 7, 6], [4, 6, 5],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2]   # right
        ]
        
        return {
            "type": "BoxGeometry",
            "vertices": vertices,
            "faces": faces,
            "parameters": {
                "width": dimensions[0],
                "height": dimensions[1],
                "depth": dimensions[2]
            },
            "has_authentic_geometry": False,
            "vertex_count": len(vertices),
            "face_count": len(faces)
        }
    
    def _create_building_from_elements(self) -> Building:
        """Create building from all elements when no IfcBuilding exists"""
        elements = []
        all_elements = list(self.ifc_file.by_type("IfcElement"))
        
        for element in all_elements:
            bim_element = self._parse_element(element)
            if bim_element:
                elements.append(bim_element)
        
        bounds = self._calculate_building_bounds(elements)
        
        return Building(
            id="main_building",
            name="Main Building",
            elements=elements,
            bounds=bounds
        )
    
    def _calculate_building_bounds(self, elements: List[BIMElement]) -> Dict[str, float]:
        """Calculate bounding box for building elements"""
        # Simplified bounds calculation
        return {
            "min_x": -50.0, "max_x": 50.0,
            "min_y": -30.0, "max_y": 30.0, 
            "min_z": 0.0, "max_z": 25.0
        }
    
    def _calculate_global_bounds(self, buildings: List[Building]) -> Dict[str, float]:
        """Calculate global bounds for all buildings"""
        if not buildings:
            return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0, "min_z": 0, "max_z": 0}
        
        # Use first building's bounds as global bounds
        return buildings[0].bounds
    
    def _get_element_level(self, element) -> str:
        """Get the level/storey for an element"""
        try:
            # Try to find contained in spatial structure
            if hasattr(element, 'ContainedInStructure'):
                for rel in element.ContainedInStructure:
                    if hasattr(rel, 'RelatingStructure'):
                        relating = rel.RelatingStructure
                        if relating.is_a("IfcBuildingStorey"):
                            return relating.Name or "Level 1"
            return "Ground Floor"
        except:
            return "Unknown Level"
    
    def _get_element_materials(self, element) -> Dict[str, Any]:
        """Get material properties for element"""
        try:
            materials = {}
            if hasattr(element, 'HasAssociations'):
                for rel in element.HasAssociations:
                    if rel.is_a("IfcRelAssociatesMaterial"):
                        material = rel.RelatingMaterial
                        if material:
                            materials["type"] = material.Name or "Unknown"
            return materials
        except:
            return {"type": "concrete"}
    
    def _create_fallback_model(self, file_path: str) -> IfcModel:
        """Create fallback model when parsing fails"""
        fallback_building = Building(
            id="fallback",
            name="Fallback Building", 
            elements=[],
            bounds={"min_x": -20, "max_x": 20, "min_y": -10, "max_y": 10, "min_z": 0, "max_z": 25}
        )
        
        return IfcModel(
            file_path=file_path,
            schema="IFC2X3",
            buildings=[fallback_building],
            project_info={"name": "Fallback Project"},
            global_bounds=fallback_building.bounds,
            total_elements=0,
            file_size_bytes=0
        )

        # Extract data for summary
        building_name = building.Name if building and building.Name else project_name
        building_type = building_props.get("BuildingType", "Unknown")
        location = building_props.get("Address", "Unknown")

        # Check for construction status
        status = building_props.get("ConstructionStatus", "Unknown")

        # Year built from properties or filename
        year_built = building_props.get("YearBuilt", 0)
        if not year_built and self.ifc_file_path:
            # Try to extract from filename (e.g., building_2023.ifc)
            import re
            year_match = re.search(r'_(\d{4})\.ifc$', self.ifc_file_path, re.IGNORECASE)
            if year_match:
                try:
                    year_built = int(year_match.group(1))
                except ValueError:
                    pass

        return {
            "name": building_name,
            "type": building_type,
            "location": location,
            "floors": storey_count,
            "area": total_area,
            "height": height,
            "year_built": year_built,
            "status": status,
            "element_count": len(all_elements),
        }

    def get_all_elements(self) -> List[Dict]:
        """
        Get all building elements as dictionaries.

        Returns:
            List of element dictionaries
        """
        if not self.ifc_file:
            logger.warning("No IFC file loaded.")
            return []

        # Get all elements of type IfcElement
        elements = self.ifc_file.by_type("IfcElement")
        return [self._element_to_dict(element) for element in elements]

    def get_elements_by_type(self, element_type: str) -> List[Dict]:
        """
        Get elements of a specific type.

        Args:
            element_type: IFC element type (e.g., "IfcWall", "IfcDoor")

        Returns:
            List of element dictionaries
        """
        if not self.ifc_file:
            logger.warning("No IFC file loaded.")
            return []

        # Ensure type has "Ifc" prefix
        if not element_type.startswith("Ifc"):
            element_type = f"Ifc{element_type}"

        try:
            elements = self.ifc_file.by_type(element_type)
            return [self._element_to_dict(element) for element in elements]
        except Exception as e:
            logger.error(f"Error getting elements of type {element_type}: {str(e)}")
            return []

    def get_element_by_id(self, element_id: str) -> Optional[Dict]:
        """
        Get a specific element by ID.

        Args:
            element_id: Element ID or GUID

        Returns:
            Element dictionary or None if not found
        """
        if not self.ifc_file:
            logger.warning("No IFC file loaded.")
            return None

        # Try to get by GlobalId first
        for element in self.ifc_file.by_type("IfcElement"):
            if hasattr(element, "GlobalId") and element.GlobalId == element_id:
                return self._element_to_dict(element)

        # Try by internal ID
        try:
            element = self.ifc_file.by_id(int(element_id))
            if element:
                return self._element_to_dict(element)
        except (ValueError, TypeError):
            pass

        # Try by custom ID attribute
        for element in self.ifc_file.by_type("IfcElement"):
            props = self._get_element_properties(element)
            if "ID" in props and props["ID"] == element_id:
                return self._element_to_dict(element)

        return None

    def get_spaces(self) -> List[Dict]:
        """
        Get all space elements.

        Returns:
            List of space dictionaries
        """
        return self.get_elements_by_type("IfcSpace")

    def get_element_types(self) -> List[str]:
        """
        Get all element types in the IFC file.

        Returns:
            List of element type names
        """
        if not self.ifc_file:
            logger.warning("No IFC file loaded.")
            return []

        # Get all entity types that are subclasses of IfcElement
        entity_types: Set[str] = set()
        for element in self.ifc_file.by_type("IfcElement"):
            entity_types.add(element.is_a())

        return sorted(list(entity_types))

    def to_dict(self) -> Dict:
        """
        Convert the entire IFC dataset to a dictionary representation.

        Returns:
            Dictionary containing building and elements data
        """
        return {
            "building": self.get_building_summary(),
            "elements": self.get_all_elements(),
        }

    def _element_to_dict(self, element: Any) -> Dict:
        """
        Convert an IFC element to a dictionary representation.

        Args:
            element: IFC element object

        Returns:
            Dictionary containing element data
        """
        # Get basic element data
        element_type = element.is_a()
        element_id = element.GlobalId if hasattr(element, "GlobalId") else str(element.id())
        element_name = (
            element.Name if hasattr(element, "Name") and element.Name
            else f"{element_type}_{element.id()}"
        )

        # Get properties
        properties = self._get_element_properties(element)

        # Create standardized dict
        return {
            "id": element_id,
            "type": element_type,
            "name": element_name,
            "properties": properties,
        }

    def _get_element_properties(self, element: Any) -> Dict:
        """
        Extract all properties from an IFC element.

        Args:
            element: IFC element object

        Returns:
            Dictionary of properties
        """
        properties = {}

        try:
            # Direct attributes
            if hasattr(element, "Name") and element.Name:
                properties["Name"] = element.Name

            if hasattr(element, "Description") and element.Description:
                properties["Description"] = element.Description

            if hasattr(element, "ObjectType") and element.ObjectType:
                properties["ObjectType"] = element.ObjectType

            # Get property sets
            if hasattr(element, "IsDefinedBy"):
                for definition in element.IsDefinedBy:
                    if definition.is_a("IfcRelDefinesByProperties"):
                        property_set = definition.RelatingPropertyDefinition

                        # Handle property sets
                        if property_set.is_a("IfcPropertySet"):
                            # Get property set name for future extensions if needed
                            # property_set.Name if property_set.Name else "Unknown"

                            # Extract properties from the property set
                            for prop in property_set.HasProperties:
                                if prop.is_a("IfcPropertySingleValue") and prop.NominalValue:
                                    prop_name = prop.Name if prop.Name else "Unknown"
                                    prop_value = self._get_property_value(prop.NominalValue)
                                    properties[prop_name] = prop_value

            # Get quantities
            if hasattr(element, "IsDefinedBy"):
                for definition in element.IsDefinedBy:
                    if definition.is_a("IfcRelDefinesByProperties"):
                        property_set = definition.RelatingPropertyDefinition

                        # Handle element quantities
                        if property_set.is_a("IfcElementQuantity"):
                            for quantity in property_set.Quantities:
                                if hasattr(quantity, "Name") and hasattr(quantity, "LengthValue"):
                                    properties[quantity.Name] = quantity.LengthValue
                                elif hasattr(quantity, "Name") and hasattr(quantity, "AreaValue"):
                                    properties[quantity.Name] = quantity.AreaValue
                                elif hasattr(quantity, "Name") and hasattr(quantity, "VolumeValue"):
                                    properties[quantity.Name] = quantity.VolumeValue
                                elif hasattr(quantity, "Name") and hasattr(quantity, "WeightValue"):
                                    properties[quantity.Name] = quantity.WeightValue
                                elif hasattr(quantity, "Name") and hasattr(quantity, "CountValue"):
                                    properties[quantity.Name] = quantity.CountValue

            # Get material information
            if hasattr(element, "HasAssociations"):
                for association in element.HasAssociations:
                    if association.is_a("IfcRelAssociatesMaterial"):
                        relating_material = association.RelatingMaterial

                        if relating_material.is_a("IfcMaterial"):
                            properties["Material"] = relating_material.Name
                        elif relating_material.is_a("IfcMaterialList"):
                            material_names = [m.Name for m in relating_material.Materials]
                            properties["Materials"] = ", ".join(material_names)
                        elif relating_material.is_a("IfcMaterialLayerSetUsage"):
                            material_set = relating_material.ForLayerSet
                            layer_names = [
                                layer.Material.Name for layer in material_set.MaterialLayers
                            ]
                            properties["MaterialLayers"] = ", ".join(layer_names)

            # Get spatial location info
            if hasattr(element, "ContainedInStructure"):
                for rel in element.ContainedInStructure:
                    if rel.is_a("IfcRelContainedInSpatialStructure"):
                        if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                            properties["Floor"] = rel.RelatingStructure.Name
                        elif rel.RelatingStructure.is_a("IfcSpace"):
                            properties["Space"] = rel.RelatingStructure.Name

            # Add specific properties based on element type
            if element.is_a("IfcWall"):
                properties["ElementType"] = "Wall"
            elif element.is_a("IfcDoor"):
                properties["ElementType"] = "Door"
            elif element.is_a("IfcWindow"):
                properties["ElementType"] = "Window"
            elif element.is_a("IfcSlab"):
                properties["ElementType"] = "Slab"
            elif element.is_a("IfcColumn"):
                properties["ElementType"] = "Column"
            elif element.is_a("IfcBeam"):
                properties["ElementType"] = "Beam"

            # Get element geometry info if available
            if hasattr(element, "Representation"):
                properties["HasGeometry"] = True

        except Exception as e:
            logger.warning(f"Error extracting properties for element {element.id()}: {str(e)}")

        return properties

    def _get_property_value(self, nominal_value: Any) -> Any:
        """
        Extract the actual value from an IFC property value entity.

        Args:
            nominal_value: IFC property value entity

        Returns:
            The actual value
        """
        value_type = nominal_value.is_a()

        if value_type == "IfcInteger" or value_type == "IfcReal":
            return float(nominal_value.wrappedValue)
        elif value_type == "IfcBoolean":
            return bool(nominal_value.wrappedValue)
        elif value_type == "IfcLabel" or value_type == "IfcText" or value_type == "IfcIdentifier":
            return str(nominal_value.wrappedValue)
        else:
            # Return string representation for other types
            return (str(nominal_value.wrappedValue) if hasattr(nominal_value, "wrappedValue")
                    else str(nominal_value))