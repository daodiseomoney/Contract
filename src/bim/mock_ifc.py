"""
Mock IFC Module
Provides a simplified mock implementation of IFC (Industry Foundation Classes) objects
to simulate BIM data for testing and development purposes.
"""
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MockIFCObject:
    """
    A lightweight mock implementation of an IFC object with sample properties
    for testing BIM agent interactions before real IFC data integration.
    """
    
    def __init__(self):
        """Initialize the mock IFC object with sample building data"""
        # Sample building information
        self.project_info = {
            "name": "Grand Plaza Tower",
            "address": "123 Innovation Avenue, Smart City",
            "type": "Mixed-Use Development",
            "status": "Under Construction",
            "total_area": "25,000 m²",
            "stories": 32,
            "completion_date": "2026-06-30"
        }
        
        # Mock building components
        self.properties = {
            "walls": [
                {"id": "W1001", "name": "Exterior Wall Type 1", "material": "Reinforced Concrete", "thickness": "300mm", "thermal_rating": "R-19", "location": "Perimeter", "level": "Ground Floor"},
                {"id": "W1002", "name": "Interior Wall Type A", "material": "Gypsum Board", "thickness": "150mm", "fire_rating": "1 hour", "acoustic_rating": "STC-45", "location": "East Wing", "level": "Floor 3-12"},
                {"id": "W1003", "name": "Curtain Wall System", "material": "Aluminum and Glass", "glass_type": "Low-E Double Glazed", "u_value": "1.4 W/m²K", "location": "South Facade", "level": "All Floors"}
            ],
            "floors": [
                {"id": "F2001", "name": "Standard Floor Type", "material": "Reinforced Concrete", "thickness": "250mm", "live_load": "4.0 kN/m²", "dead_load": "1.5 kN/m²", "level": "Typical Floors"},
                {"id": "F2002", "name": "Lobby Floor", "material": "Granite Tiles on Concrete", "thickness": "300mm", "finish": "Polished Stone", "level": "Ground Floor"}
            ],
            "rooms": [
                {"id": "R3001", "name": "Office Space Type A", "area": "120 m²", "ceiling_height": "2.7m", "occupancy": "12 persons", "level": "Floors 3-20"},
                {"id": "R3002", "name": "Conference Room", "area": "45 m²", "ceiling_height": "2.7m", "occupancy": "15 persons", "acoustics": "Enhanced", "level": "Floors 3-20"},
                {"id": "R3003", "name": "Residential Unit Type B", "area": "85 m²", "bedrooms": 2, "bathrooms": 1, "level": "Floors 21-30"}
            ],
            "mep_systems": [
                {"id": "M4001", "name": "HVAC System", "type": "Variable Refrigerant Flow", "capacity": "2000 kW", "service_area": "Entire Building"},
                {"id": "M4002", "name": "Plumbing System", "water_supply": "Municipal Connection", "waste_management": "Gravity System"},
                {"id": "E4001", "name": "Electrical System", "main_supply": "5000 kVA", "emergency_power": "800 kVA Generator"}
            ],
            "sustainability": [
                {"id": "S5001", "name": "Solar Panel Array", "capacity": "200 kW", "location": "Rooftop"},
                {"id": "S5002", "name": "Rainwater Harvesting System", "capacity": "50,000 liters", "usage": "Landscape Irrigation"}
            ]
        }
        
        # Building performance metrics
        self.performance = {
            "energy_efficiency": "LEED Platinum",
            "estimated_annual_energy_consumption": "120 kWh/m²",
            "carbon_footprint": "15 kg CO₂/m²/year",
            "water_efficiency": "40% reduction from baseline"
        }
        
        logger.debug("MockIFCObject initialized with sample building data")
    
    def get_property(self, key: str) -> Union[List[Dict[str, Any]], str]:
        """
        Get a specific property from the mock IFC data
        
        Args:
            key: The property key to retrieve
            
        Returns:
            The property value or an error message if not found
        """
        return self.properties.get(key, "Property not found in mock IFC data")
    
    def get_project_info(self) -> Dict[str, str]:
        """
        Get basic project information
        
        Returns:
            Dictionary of project information
        """
        return self.project_info
    
    def get_performance_metrics(self) -> Dict[str, str]:
        """
        Get building performance metrics
        
        Returns:
            Dictionary of performance metrics
        """
        return self.performance
    
    def search_components(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for components matching a query string
        
        Args:
            query: Search term to match against component properties
            
        Returns:
            List of matching components
        """
        results = []
        query = query.lower()
        
        # Search through all properties
        for category, items in self.properties.items():
            for item in items:
                # Check if query matches any value in the item
                for key, value in item.items():
                    if isinstance(value, str) and query in value.lower():
                        # Add category to the item for context
                        item_with_category = item.copy()
                        item_with_category["category"] = category
                        results.append(item_with_category)
                        break
        
        return results