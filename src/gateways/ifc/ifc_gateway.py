"""
IFC Gateway for the Real Estate Tokenization platform.
Handles interaction with IFC files using ifcopenshell.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime

try:
    import ifcopenshell
except ImportError:
    logging.warning("ifcopenshell not found. IFC functionality will be limited.")
    ifcopenshell = None

from src.entities.bim_model import BIMModel, BIMElement, ElementType


# Configure logging
logger = logging.getLogger(__name__)


class IFCGateway:
    """
    Gateway for interacting with IFC files using ifcopenshell.
    This is part of the infrastructure layer in clean architecture.
    """
    
    def __init__(self, file_path: Optional[str] = None):
        """Initialize the IFC Gateway"""
        self.model = None
        self.ifc_file = None
        self.file_path = None
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path: str) -> bool:
        """
        Load an IFC file using ifcopenshell
        
        Args:
            file_path: Path to IFC file
            
        Returns:
            bool: True if file was loaded successfully, False otherwise
        """
        if not ifcopenshell:
            logger.error("ifcopenshell is not available")
            return False
            
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        try:
            # Load IFC file
            self.ifc_file = ifcopenshell.open(file_path)
            self.file_path = file_path
            
            # Extract file metadata
            schema_version = self.ifc_file.schema
            site_name = "Unknown Site"
            building_name = "Unknown Building"
            
            # Try to get site and building names
            sites = self.ifc_file.by_type("IfcSite")
            if sites:
                site = sites[0]
                site_name = site.Name or "Unknown Site"
                
            buildings = self.ifc_file.by_type("IfcBuilding")
            if buildings:
                building = buildings[0]
                building_name = building.Name or "Unknown Building"
                
            # Create domain model
            self.model = BIMModel(
                file_name=os.path.basename(file_path),
                schema_version=schema_version,
                site_name=site_name,
                building_name=building_name
            )
            
            # We don't load all elements by default for performance reasons
            # Elements can be loaded on demand
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            self.ifc_file = None
            self.file_path = None
            self.model = None
            return False
            
    def summary(self) -> Dict:
        """
        Get summary information about the loaded IFC file
        
        Returns:
            Dict: Summary information
        """
        if not self.ifc_file:
            logger.warning("No IFC file loaded")
            return {
                "success": False,
                "message": "No IFC file loaded"
            }
            
        try:
            # Get basic site and building information
            sites = self.ifc_file.by_type("IfcSite")
            site_name = sites[0].Name if sites else "Unknown Site"
            
            buildings = self.ifc_file.by_type("IfcBuilding")
            building_name = buildings[0].Name if buildings else "Unknown Building"
            
            # Get element types and counts
            element_types = self.get_element_types()
            element_counts = {}
            
            for element_type in element_types:
                elements = self.get_elements_by_type(element_type)
                element_counts[element_type] = len(elements)
                
            # Create summary
            file_name = os.path.basename(self.file_path) if self.file_path else "Unknown file"
            summary = {
                "success": True,
                "file_name": file_name,
                "schema": self.ifc_file.schema,
                "elements": self.count_all_elements(),
                "site_name": site_name,
                "building_name": building_name,
                "element_types": element_types,
                "element_counts": element_counts
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    def count_all_elements(self) -> int:
        """Count all elements in the IFC file"""
        if not self.ifc_file:
            return 0
            
        # Count all entities, but exclude abstract types
        excluded_types = ["IfcOwnerHistory", "IfcRelationship", "IfcPropertySet"]
        count = 0
        
        for entity in self.ifc_file:
            entity_type = entity.is_a()
            if not any(excluded in entity_type for excluded in excluded_types):
                count += 1
                
        return count
        
    def get_element_types(self) -> List[str]:
        """
        Get all element types in the IFC file
        
        Returns:
            List[str]: List of element type names
        """
        if not self.ifc_file:
            return []
            
        # Get common IFC element types
        common_types = [
            "IfcWall", "IfcWindow", "IfcDoor", "IfcSlab", "IfcBeam",
            "IfcColumn", "IfcSpace", "IfcFurnishingElement", "IfcStair"
        ]
        
        # Filter only types that actually exist in the file
        available_types = []
        for element_type in common_types:
            elements = self.ifc_file.by_type(element_type)
            if elements:
                available_types.append(element_type)
                
        return available_types
        
    def get_elements_by_type(self, element_type: str) -> List[Dict]:
        """
        Get all elements of a specific type
        
        Args:
            element_type: IFC element type (e.g. "IfcWall")
            
        Returns:
            List[Dict]: List of element dictionaries
        """
        if not self.ifc_file:
            return []
            
        try:
            elements = self.ifc_file.by_type(element_type)
            result = []
            
            for element in elements:
                # Get basic properties
                element_id = element.id()
                global_id = element.GlobalId
                name = element.Name if hasattr(element, "Name") else None
                
                # Get element properties
                properties = self._get_element_properties(element)
                
                # Map to domain element type
                domain_type = ElementType.from_ifc_class(element_type)
                
                # Create element dictionary
                element_dict = {
                    "id": str(element_id),
                    "global_id": global_id,
                    "name": name,
                    "type": str(domain_type),
                    "ifc_class": element_type,
                    "properties": properties
                }
                
                result.append(element_dict)
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting elements of type {element_type}: {e}")
            return []
            
    def get_element_by_id(self, element_id: str) -> Optional[Dict]:
        """
        Get element details by ID
        
        Args:
            element_id: Element ID
            
        Returns:
            Optional[Dict]: Element dictionary or None if not found
        """
        if not self.ifc_file or not element_id:
            return None
            
        try:
            # Convert string ID to integer
            id_int = int(element_id)
            element = self.ifc_file.by_id(id_int)
            
            if not element:
                return None
                
            # Get basic properties
            element_type = element.is_a()
            global_id = element.GlobalId
            name = element.Name if hasattr(element, "Name") else None
            
            # Get related objects
            related_elements = self._get_related_elements(element)
            
            # Get element properties
            properties = self._get_element_properties(element)
            
            # Map to domain element type
            domain_type = ElementType.from_ifc_class(element_type)
            
            # Create element dictionary
            element_dict = {
                "id": element_id,
                "global_id": global_id,
                "name": name,
                "type": str(domain_type),
                "ifc_class": element_type,
                "properties": properties,
                "related_elements": related_elements
            }
            
            return element_dict
            
        except Exception as e:
            logger.error(f"Error getting element with ID {element_id}: {e}")
            return None
            
    def _get_element_properties(self, element: Any) -> Dict:
        """
        Get properties for an IFC element
        
        Args:
            element: IFC element
            
        Returns:
            Dict: Element properties
        """
        if not self.ifc_file or not element:
            return {}
            
        try:
            properties = {}
            
            # Get property sets
            property_sets = {}
            for definition in element.IsDefinedBy:
                if definition.is_a("IfcRelDefinesByProperties"):
                    property_set = definition.RelatingPropertyDefinition
                    if property_set.is_a("IfcPropertySet"):
                        property_sets[property_set.Name] = property_set
                        
            # Extract properties from property sets
            for pset_name, pset in property_sets.items():
                properties[pset_name] = {}
                
                for prop in pset.HasProperties:
                    if prop.is_a("IfcPropertySingleValue"):
                        prop_name = prop.Name
                        prop_value = prop.NominalValue.wrappedValue if prop.NominalValue else None
                        properties[pset_name][prop_name] = prop_value
                        
            return properties
            
        except Exception as e:
            logger.error(f"Error getting properties: {e}")
            return {}
            
    def _get_related_elements(self, element: Any) -> List[Dict]:
        """
        Get elements related to the given element
        
        Args:
            element: IFC element
            
        Returns:
            List[Dict]: List of related elements
        """
        if not self.ifc_file or not element:
            return []
            
        try:
            related_elements = []
            
            # Get all relationships
            for rel in self.ifc_file.get_inverse(element):
                # Only look at specific relationship types
                if rel.is_a("IfcRelAggregates") or rel.is_a("IfcRelContainedInSpatialStructure"):
                    # Add the parent element (what contains this element)
                    if hasattr(rel, "RelatingObject") and rel.RelatingObject != element:
                        parent = rel.RelatingObject
                        related_elements.append({
                            "id": str(parent.id()),
                            "name": parent.Name if hasattr(parent, "Name") else None,
                            "type": parent.is_a(),
                            "relationship": "parent"
                        })
                    
                    # Add the child elements (what this element contains)
                    if hasattr(rel, "RelatedElements"):
                        for child in rel.RelatedElements:
                            if child != element:
                                related_elements.append({
                                    "id": str(child.id()),
                                    "name": child.Name if hasattr(child, "Name") else None,
                                    "type": child.is_a(),
                                    "relationship": "child"
                                })
                                
            return related_elements
            
        except Exception as e:
            logger.error(f"Error getting related elements: {e}")
            return []
    
    def to_domain_model(self) -> Optional[BIMModel]:
        """
        Convert the loaded IFC file to a domain model BIMModel
        
        Returns:
            Optional[BIMModel]: BIM model or None if conversion failed
        """
        if not self.ifc_file or not self.model:
            return None
            
        try:
            # We already have the basic model structure from load_file
            # Now load elements for all types we know about
            element_types = self.get_element_types()
            
            for element_type in element_types:
                elements_data = self.get_elements_by_type(element_type)
                
                for element_data in elements_data:
                    # Create a domain BIMElement
                    element = BIMElement(
                        id=element_data["id"],
                        global_id=element_data["global_id"],
                        type=ElementType(element_data["type"]),
                        ifc_class=element_data["ifc_class"],
                        name=element_data["name"],
                        properties=element_data["properties"]
                    )
                    
                    # Add to model
                    self.model.add_element(element)
                    
            return self.model
            
        except Exception as e:
            logger.error(f"Error converting to domain model: {e}")
            return None