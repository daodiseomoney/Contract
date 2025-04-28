"""
IFC Gateway for loading and accessing IFC building models.
This gateway wraps ifcopenshell functionality and provides clean interfaces for the application.
"""

from pathlib import Path
import logging
import ifcopenshell

# Configure logging
logger = logging.getLogger(__name__)

class IFCGateway:
    """
    Loads an IFC file and extracts high-level stats and elements.
    This class provides a clean interface to ifcopenshell functionality.
    """

    def __init__(self, file_path: str = None):
        """
        Initialize the IFC Gateway with an optional file path.
        
        Args:
            file_path: Path to the IFC file to load
        """
        self.model = None
        self.file_path = None
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path: str) -> bool:
        """
        Load an IFC file.
        
        Args:
            file_path: Path to the IFC file
            
        Returns:
            bool: True if file loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading IFC file: {file_path}")
            self.model = ifcopenshell.open(file_path)
            self.file_path = file_path
            return True
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            return False
    
    def summary(self) -> dict:
        """
        Get a summary of the IFC model.
        
        Returns:
            dict: Summary information about the model
        """
        if not self.model:
            logger.warning("Cannot get summary, no IFC file loaded")
            return {
                "elements": 0,
                "schema": None,
                "site_name": None,
                "success": False,
                "message": "No IFC file loaded"
            }
        
        try:
            elements = self.model.by_type("IfcBuildingElement")
            sites = self.model.by_type("IfcSite")
            site_name = sites[0].Name if sites else None
            
            return {
                "elements": len(elements),
                "schema": self.model.schema,
                "site_name": site_name,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting model summary: {e}")
            return {
                "elements": 0,
                "schema": None,
                "site_name": None,
                "success": False,
                "message": str(e)
            }
    
    def get_all_elements(self) -> list:
        """
        Get all building elements in the model.
        
        Returns:
            list: All building elements
        """
        if not self.model:
            return []
        
        try:
            return self.model.by_type("IfcBuildingElement")
        except Exception as e:
            logger.error(f"Error getting elements: {e}")
            return []
    
    def get_element_types(self) -> list:
        """
        Get all element types in the model.
        
        Returns:
            list: All element type names
        """
        if not self.model:
            return []
        
        try:
            # Get all entities that are instances of IfcBuildingElement
            elements = self.model.by_type("IfcBuildingElement")
            
            # Extract unique types
            types = set()
            for element in elements:
                types.add(element.is_a())
            
            return sorted(list(types))
        except Exception as e:
            logger.error(f"Error getting element types: {e}")
            return []
    
    def get_elements_by_type(self, element_type: str) -> list:
        """
        Get all elements of a specific type.
        
        Args:
            element_type: The type of element to get (e.g., "IfcWall")
            
        Returns:
            list: All elements of the specified type
        """
        if not self.model:
            return []
        
        try:
            return self.model.by_type(element_type)
        except Exception as e:
            logger.error(f"Error getting elements by type: {e}")
            return []
    
    def get_element_by_id(self, element_id: str) -> dict:
        """
        Get a specific element by ID.
        
        Args:
            element_id: The ID of the element to get
            
        Returns:
            dict: Element information
        """
        if not self.model:
            return None
        
        try:
            # Convert string ID to integer
            id_value = int(element_id)
            element = self.model.by_id(id_value)
            
            if not element:
                return None
            
            # Convert element to dictionary representation
            result = {
                "id": element.id(),
                "type": element.is_a(),
                "guid": getattr(element, "GlobalId", None),
                "name": getattr(element, "Name", None),
                "description": getattr(element, "Description", None),
                "properties": self._get_element_properties(element)
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting element by ID: {e}")
            return None
    
    def _get_element_properties(self, element) -> dict:
        """
        Get properties for an element.
        
        Args:
            element: The element to get properties for
            
        Returns:
            dict: Property sets and their properties
        """
        properties = {}
        
        try:
            # Get property sets
            property_sets = self.model.get_inverse(element, 'HasProperties')
            
            for pset in property_sets:
                pset_name = getattr(pset, "Name", "Unknown")
                properties[pset_name] = {}
                
                if hasattr(pset, "HasProperties"):
                    for prop in pset.HasProperties:
                        if hasattr(prop, "Name") and hasattr(prop, "NominalValue"):
                            prop_name = prop.Name
                            prop_value = prop.NominalValue.wrappedValue
                            properties[pset_name][prop_name] = prop_value
        except Exception as e:
            logger.warning(f"Error getting properties for element {element.id()}: {e}")
        
        return properties