"""
Mock IFC data provider for the BIM agent
This module provides sample building data for testing and development
"""

from typing import Dict, List, Optional


class MockIFCElement:
    """Represents a single IFC element with properties"""

    def __init__(self, id: str, type: str, name: str, properties: Dict):
        self.id = id
        self.type = type
        self.name = name
        self.properties = properties

    def to_dict(self) -> Dict:
        """Convert element to dictionary representation"""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "properties": self.properties,
        }


class MockIFCData:
    """Provides sample IFC building data"""

    def __init__(self):
        """Initialize with sample building data"""
        self.building_name = "Cosmic Tower Project"
        self.building_type = "Commercial High-Rise"
        self.location = "1234 Innovation Way, Future City"
        self.floors = 17
        self.gross_area = 25000  # in square meters
        self.height = 85  # in meters
        self.year_built = 2023
        self.construction_status = "Completed"

        # Generate sample building elements
        self.elements = self._generate_sample_elements()

    def _generate_sample_elements(self) -> List[MockIFCElement]:
        """Generate a list of sample building elements"""
        elements = [
            # Structural elements
            MockIFCElement(
                id="ST001",
                type="IfcColumn",
                name="Column-Type1",
                properties={
                    "material": "Reinforced Concrete",
                    "dimensions": "0.5m x 0.5m",
                    "load_bearing": True,
                    "fire_rating": "4 hours",
                },
            ),
            MockIFCElement(
                id="ST002",
                type="IfcBeam",
                name="Beam-Type1",
                properties={
                    "material": "Steel",
                    "dimensions": "0.3m x 0.6m",
                    "load_bearing": True,
                    "span": "8m",
                },
            ),
            # Architectural elements
            MockIFCElement(
                id="AR001",
                type="IfcWall",
                name="Wall-Exterior",
                properties={
                    "material": "Curtain Wall",
                    "thickness": "0.3m",
                    "thermal_resistance": "R-25",
                    "fire_rating": "2 hours",
                },
            ),
            MockIFCElement(
                id="AR002",
                type="IfcDoor",
                name="Door-Main-Entrance",
                properties={
                    "material": "Glass and Aluminum",
                    "dimensions": "2.4m x 2.1m",
                    "fire_exit": True,
                    "accessibility": "ADA Compliant",
                },
            ),
            # MEP elements
            MockIFCElement(
                id="ME001",
                type="IfcChiller",
                name="HVAC-Chiller-1",
                properties={
                    "capacity": "500 tons",
                    "energy_efficiency": "High",
                    "refrigerant": "R-134a",
                    "location": "Roof",
                },
            ),
            MockIFCElement(
                id="EL001",
                type="IfcDistributionBoard",
                name="Electrical-Main-Panel",
                properties={
                    "capacity": "2000A",
                    "voltage": "480V",
                    "location": "Basement Level 1",
                    "emergency_backup": True,
                },
            ),
            # Spaces
            MockIFCElement(
                id="SP001",
                type="IfcSpace",
                name="Office-Open-Plan-1",
                properties={
                    "floor_area": "500 sqm",
                    "ceiling_height": "3m",
                    "occupancy": "50 persons",
                    "ventilation_rate": "15 L/s per person",
                },
            ),
            MockIFCElement(
                id="SP002",
                type="IfcSpace",
                name="Conference-Room-1",
                properties={
                    "floor_area": "100 sqm",
                    "ceiling_height": "3m",
                    "occupancy": "20 persons",
                    "acoustic_rating": "STC 50",
                },
            ),
        ]

        return elements

    def get_building_summary(self) -> Dict:
        """Return a summary of the building data"""
        return {
            "name": self.building_name,
            "type": self.building_type,
            "location": self.location,
            "floors": self.floors,
            "area": self.gross_area,
            "height": self.height,
            "year_built": self.year_built,
            "status": self.construction_status,
            "element_count": len(self.elements),
        }

    def get_all_elements(self) -> List[Dict]:
        """Return all building elements as dictionaries"""
        return [element.to_dict() for element in self.elements]

    def get_elements_by_type(self, element_type: str) -> List[Dict]:
        """Return elements of a specific type"""
        return [
            element.to_dict()
            for element in self.elements
            if element.type.lower() == element_type.lower()
        ]

    def get_element_by_id(self, element_id: str) -> Optional[Dict]:
        """Return a specific element by ID"""
        for element in self.elements:
            if element.id == element_id:
                return element.to_dict()
        return None

    def get_spaces(self) -> List[Dict]:
        """Return all space elements"""
        return self.get_elements_by_type("IfcSpace")

    def to_dict(self) -> Dict:
        """Convert the entire dataset to a dictionary representation"""
        return {
            "building": {
                "name": self.building_name,
                "type": self.building_type,
                "location": self.location,
                "floors": self.floors,
                "gross_area": self.gross_area,
                "height": self.height,
                "year_built": self.year_built,
                "construction_status": self.construction_status,
            },
            "elements": self.get_all_elements(),
        }
