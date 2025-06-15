"""
BIM Element Entity - Layer 1 Domain Entity
Represents individual building elements from IFC files
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class BIMElement:
    """Individual building element with IFC properties"""
    id: str
    type: str
    name: str
    level: str
    geometry_data: Optional[Dict[str, Any]] = None
    material_properties: Optional[Dict[str, Any]] = None
    position: Optional[List[float]] = None
    rotation: Optional[List[float]] = None
    area: Optional[float] = None
    volume: Optional[float] = None
    is_structural: bool = False
    
    def __post_init__(self):
        """Set default values after initialization"""
        if self.position is None:
            self.position = [0.0, 0.0, 0.0]
        if self.rotation is None:
            self.rotation = [0.0, 0.0, 0.0]
        if self.geometry_data is None:
            self.geometry_data = {}
        if self.material_properties is None:
            self.material_properties = {}
            
        # Determine if element is structural
        structural_types = ["IfcBeam", "IfcColumn", "IfcWall", "IfcSlab", "IfcFoundation"]
        self.is_structural = self.type in structural_types