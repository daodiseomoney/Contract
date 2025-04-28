"""
BIM Model entity for the Real Estate Tokenization platform.
Defines core domain objects related to Building Information Modeling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from uuid import uuid4


class ElementType(str, Enum):
    """Types of elements in a BIM model"""
    WALL = "wall"
    DOOR = "door"
    WINDOW = "window"
    SLAB = "slab"
    COLUMN = "column"
    BEAM = "beam"
    ROOF = "roof"
    STAIR = "stair"
    RAILING = "railing"
    FURNITURE = "furniture"
    SPACE = "space"
    BUILDING = "building"
    SITE = "site"
    OTHER = "other"
    
    @classmethod
    def from_ifc_class(cls, ifc_class: str) -> 'ElementType':
        """Map an IFC class to an ElementType"""
        mapping = {
            "IfcWall": cls.WALL,
            "IfcWallStandardCase": cls.WALL,
            "IfcDoor": cls.DOOR,
            "IfcWindow": cls.WINDOW,
            "IfcSlab": cls.SLAB,
            "IfcColumn": cls.COLUMN,
            "IfcBeam": cls.BEAM,
            "IfcRoof": cls.ROOF,
            "IfcStair": cls.STAIR,
            "IfcRailing": cls.RAILING,
            "IfcFurnishingElement": cls.FURNITURE,
            "IfcSpace": cls.SPACE,
            "IfcBuilding": cls.BUILDING,
            "IfcSite": cls.SITE
        }
        
        return mapping.get(ifc_class, cls.OTHER)


@dataclass
class BIMElement:
    """A single element in a BIM model"""
    id: str
    global_id: str
    type: ElementType
    ifc_class: str
    name: Optional[str] = None
    level: Optional[str] = None
    material: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "global_id": self.global_id,
            "type": self.type.value,
            "ifc_class": self.ifc_class,
            "name": self.name,
            "level": self.level,
            "material": self.material,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BIMElement':
        """Create a BIMElement from a dictionary"""
        element_type = ElementType(data.get("type", "other"))
        return cls(
            id=data["id"],
            global_id=data["global_id"],
            type=element_type,
            ifc_class=data["ifc_class"],
            name=data.get("name"),
            level=data.get("level"),
            material=data.get("material"),
            properties=data.get("properties", {})
        )


@dataclass
class AIAnalysis:
    """AI-generated analysis of a BIM model"""
    timestamp: datetime
    analysis_text: str
    complexity_score: float = 0.0
    quality_score: float = 0.0
    sustainability_score: float = 0.0
    cost_efficiency_score: float = 0.0
    detected_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "analysis_text": self.analysis_text,
            "complexity_score": self.complexity_score,
            "quality_score": self.quality_score,
            "sustainability_score": self.sustainability_score,
            "cost_efficiency_score": self.cost_efficiency_score,
            "detected_issues": self.detected_issues,
            "recommendations": self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AIAnalysis':
        """Create an AIAnalysis from a dictionary"""
        timestamp = datetime.fromisoformat(data["timestamp"])
        return cls(
            timestamp=timestamp,
            analysis_text=data["analysis_text"],
            complexity_score=data.get("complexity_score", 0.0),
            quality_score=data.get("quality_score", 0.0),
            sustainability_score=data.get("sustainability_score", 0.0),
            cost_efficiency_score=data.get("cost_efficiency_score", 0.0),
            detected_issues=data.get("detected_issues", []),
            recommendations=data.get("recommendations", [])
        )


class BIMModel:
    """
    Building Information Model entity representing a BIM file
    and its associated elements and metadata.
    """
    
    def __init__(
        self,
        file_name: str,
        schema_version: str,
        site_name: Optional[str] = None,
        building_name: Optional[str] = None
    ):
        self.id = str(uuid4())
        self.file_name = file_name
        self.schema_version = schema_version
        self.site_name = site_name or "Unknown Site"
        self.building_name = building_name or "Unknown Building"
        self.upload_date = datetime.now()
        self.elements: List[BIMElement] = []
        self.elements_by_type: Dict[ElementType, List[BIMElement]] = {}
        self.elements_by_id: Dict[str, BIMElement] = {}
        self.element_types: Set[ElementType] = set()
        self.ai_analysis: Optional[AIAnalysis] = None
        self.property_id: Optional[str] = None
        
    def add_element(self, element: BIMElement) -> None:
        """Add an element to the model"""
        self.elements.append(element)
        self.elements_by_id[element.id] = element
        self.element_types.add(element.type)
        
        # Add to elements_by_type dictionary
        if element.type not in self.elements_by_type:
            self.elements_by_type[element.type] = []
        self.elements_by_type[element.type].append(element)
        
    def get_element_by_id(self, element_id: str) -> Optional[BIMElement]:
        """Get element by ID"""
        return self.elements_by_id.get(element_id)
    
    def get_elements_by_type(self, element_type: ElementType) -> List[BIMElement]:
        """Get all elements of a specific type"""
        return self.elements_by_type.get(element_type, [])
    
    def set_ai_analysis(self, analysis: AIAnalysis) -> None:
        """Set the AI analysis for this model"""
        self.ai_analysis = analysis
        
    def get_element_count(self) -> Dict[ElementType, int]:
        """Get count of elements by type"""
        return {
            element_type: len(elements)
            for element_type, elements in self.elements_by_type.items()
        }
        
    def get_total_element_count(self) -> int:
        """Get total number of elements"""
        return len(self.elements)
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary for API responses"""
        result = {
            "id": self.id,
            "file_name": self.file_name,
            "schema_version": self.schema_version,
            "site_name": self.site_name,
            "building_name": self.building_name,
            "upload_date": self.upload_date.isoformat(),
            "total_elements": self.get_total_element_count(),
            "element_types": [t.value for t in self.element_types],
            "element_counts": {k.value: v for k, v in self.get_element_count().items()},
            "property_id": self.property_id
        }
        
        if self.ai_analysis:
            result["ai_analysis"] = self.ai_analysis.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> Tuple['BIMModel', List[Dict]]:
        """
        Create a BIMModel from a dictionary and return element data separately
        
        Returns:
            Tuple of (BIMModel, List[Dict]) where the second element is the
            element data that can be loaded later
        """
        model = cls(
            file_name=data["file_name"],
            schema_version=data["schema_version"],
            site_name=data.get("site_name"),
            building_name=data.get("building_name")
        )
        
        # Set basic properties
        if "id" in data:
            model.id = data["id"]
        if "upload_date" in data:
            model.upload_date = datetime.fromisoformat(data["upload_date"])
        if "property_id" in data:
            model.property_id = data["property_id"]
            
        # Set AI analysis if present
        if "ai_analysis" in data:
            model.ai_analysis = AIAnalysis.from_dict(data["ai_analysis"])
            
        # Return element data separately to allow for lazy loading
        element_data = data.get("elements", [])
        
        return model, element_data
    
    def load_elements(self, element_data: List[Dict]) -> None:
        """Load elements from element data"""
        for element_dict in element_data:
            element = BIMElement.from_dict(element_dict)
            self.add_element(element)