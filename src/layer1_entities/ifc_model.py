"""
IFC Model Entity - Layer 1 Domain Entity
Container for IFC file data and building entities
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .building import Building


@dataclass
class IfcModel:
    """
    Container for parsed IFC file data containing buildings and metadata
    """
    file_path: str
    schema: str
    buildings: List[Building]
    project_info: Dict[str, Any]
    global_bounds: Dict[str, float]
    total_elements: int
    file_size_bytes: int
    
    @property
    def primary_building(self) -> Optional[Building]:
        """Get the primary building (first one)"""
        return self.buildings[0] if self.buildings else None
    
    @property
    def complexity_level(self) -> str:
        """Overall model complexity"""
        if self.total_elements > 100000:
            return "High"
        elif self.total_elements > 10000:
            return "Medium-High"
        else:
            return "Medium"