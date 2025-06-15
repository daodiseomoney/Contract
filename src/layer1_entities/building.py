"""
Building Entity - Layer 1 Domain Entity
Core business entity representing a building with IFC elements and geometric data
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .bim_element import BIMElement


@dataclass
class Building:
    """
    Core building entity containing authentic IFC structure and geometry
    """
    id: str
    name: str
    elements: List[BIMElement]
    bounds: Dict[str, float]
    coordinate_system: str = "metric"
    
    @property
    def floor_count(self) -> int:
        """Calculate number of floors from slab elements"""
        floors = set()
        for element in self.elements:
            if element.type == "IfcSlab" and "floor" in element.name.lower():
                floors.add(element.level)
        return len(floors) if floors else 1
    
    @property
    def total_area(self) -> float:
        """Calculate total floor area from slab elements"""
        total = 0.0
        for element in self.elements:
            if element.type == "IfcSlab" and hasattr(element, 'area') and element.area is not None:
                total += element.area
        return total
    
    @property
    def complexity_level(self) -> str:
        """Determine building complexity based on element count"""
        element_count = len(self.elements)
        if element_count > 100000:
            return "High"
        elif element_count > 10000:
            return "Medium-High"
        elif element_count > 1000:
            return "Medium"
        else:
            return "Low"
    
    @property
    def architectural_style(self) -> str:
        """Infer architectural style from element types"""
        wall_count = len([e for e in self.elements if e.type == "IfcWall"])
        window_count = len([e for e in self.elements if e.type == "IfcWindow"])
        
        if window_count / max(wall_count, 1) > 0.3:
            return "Modern Commercial"
        else:
            return "Traditional"
    
    @property
    def construction_type(self) -> str:
        """Determine construction type from structural elements"""
        steel_elements = len([e for e in self.elements if "steel" in e.material_properties.get("type", "").lower()])
        concrete_elements = len([e for e in self.elements if "concrete" in e.material_properties.get("type", "").lower()])
        
        if steel_elements > concrete_elements:
            return "Steel Frame"
        elif concrete_elements > 0:
            return "Concrete"
        else:
            return "Mixed Construction"
    
    @property
    def complexity_score(self) -> float:
        """Calculate complexity score based on element diversity"""
        element_types = set(e.type for e in self.elements)
        return min(len(element_types) / 20.0, 1.0)
    
    @property
    def bim_maturity(self) -> str:
        """Assess BIM maturity level based on data completeness"""
        elements_with_geometry = len([e for e in self.elements if e.geometry_data])
        elements_with_materials = len([e for e in self.elements if e.material_properties])
        
        geometry_ratio = elements_with_geometry / max(len(self.elements), 1)
        material_ratio = elements_with_materials / max(len(self.elements), 1)
        
        avg_completeness = (geometry_ratio + material_ratio) / 2
        
        if avg_completeness > 0.8:
            return "LOD 400+"
        elif avg_completeness > 0.6:
            return "LOD 300"
        elif avg_completeness > 0.4:
            return "LOD 200"
        else:
            return "LOD 100"