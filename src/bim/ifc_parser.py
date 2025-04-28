"""
IFC Parser module using IfcOpenShell.
This module processes IFC files using the IfcOpenShell library and provides structured data.
"""

import logging
import os
import ifcopenshell
from typing import Dict, List, Optional, Any, Set

# Configure logging
logging.basicConfig(level=logging.DEBUG)
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
