"""
Test cases for BIM Model entity classes
"""

import pytest
from datetime import datetime
from src.entities.bim_model import ElementType, BIMElement, AIAnalysis, BIMModel


class TestElementType:
    """Tests for ElementType enum"""
    
    def test_element_type_values(self):
        """Test element type enumeration values"""
        assert ElementType.WALL == "wall"
        assert ElementType.DOOR == "door"
        assert ElementType.WINDOW == "window"
        assert ElementType.SLAB == "slab"
        assert ElementType.COLUMN == "column"
        
    def test_from_ifc_class(self):
        """Test mapping from IFC class to ElementType"""
        assert ElementType.from_ifc_class("IfcWall") == ElementType.WALL
        assert ElementType.from_ifc_class("IfcDoor") == ElementType.DOOR
        assert ElementType.from_ifc_class("IfcStair") == ElementType.STAIR
        assert ElementType.from_ifc_class("NonExistentClass") == ElementType.OTHER


class TestBIMElement:
    """Tests for BIMElement class"""
    
    @pytest.fixture
    def sample_element(self):
        """Create a sample BIM element for testing"""
        return BIMElement(
            id="elem-001",
            global_id="2Hv$n5tL9F8RKopxqmwS4r",
            type=ElementType.WALL,
            ifc_class="IfcWall",
            name="Interior Wall",
            level="Level 1",
            material="Concrete",
            properties={"thickness": 200, "fire_rating": "2HR"}
        )
    
    def test_element_creation(self, sample_element):
        """Test BIMElement object creation"""
        assert sample_element.id == "elem-001"
        assert sample_element.global_id == "2Hv$n5tL9F8RKopxqmwS4r"
        assert sample_element.type == ElementType.WALL
        assert sample_element.ifc_class == "IfcWall"
        assert sample_element.name == "Interior Wall"
        assert sample_element.level == "Level 1"
        assert sample_element.material == "Concrete"
        assert sample_element.properties["thickness"] == 200
        assert sample_element.properties["fire_rating"] == "2HR"
    
    def test_to_dict(self, sample_element):
        """Test conversion to dictionary"""
        element_dict = sample_element.to_dict()
        assert element_dict["id"] == "elem-001"
        assert element_dict["global_id"] == "2Hv$n5tL9F8RKopxqmwS4r"
        assert element_dict["type"] == "wall"
        assert element_dict["ifc_class"] == "IfcWall"
        assert element_dict["name"] == "Interior Wall"
        assert element_dict["level"] == "Level 1"
        assert element_dict["material"] == "Concrete"
        assert element_dict["properties"]["thickness"] == 200
        assert element_dict["properties"]["fire_rating"] == "2HR"
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        element_dict = {
            "id": "elem-002",
            "global_id": "3Kp$m7uN2G9TLqsapnvR5t",
            "type": "door",
            "ifc_class": "IfcDoor",
            "name": "Entry Door",
            "level": "Ground Floor",
            "material": "Wood",
            "properties": {"width": 900, "height": 2100}
        }
        
        element = BIMElement.from_dict(element_dict)
        assert element.id == "elem-002"
        assert element.global_id == "3Kp$m7uN2G9TLqsapnvR5t"
        assert element.type == ElementType.DOOR
        assert element.ifc_class == "IfcDoor"
        assert element.name == "Entry Door"
        assert element.level == "Ground Floor"
        assert element.material == "Wood"
        assert element.properties["width"] == 900
        assert element.properties["height"] == 2100


class TestAIAnalysis:
    """Tests for AIAnalysis class"""
    
    @pytest.fixture
    def sample_analysis(self):
        """Create a sample AI analysis for testing"""
        return AIAnalysis(
            timestamp=datetime(2025, 4, 1, 12, 0, 0),
            analysis_text="This building has a good layout but some potential issues.",
            complexity_score=0.75,
            quality_score=0.82,
            sustainability_score=0.64,
            cost_efficiency_score=0.71,
            detected_issues=["Inadequate fire exits", "Potential thermal bridging"],
            recommendations=["Add emergency exit to north wing", "Improve insulation details"]
        )
    
    def test_analysis_creation(self, sample_analysis):
        """Test AIAnalysis object creation"""
        assert sample_analysis.timestamp == datetime(2025, 4, 1, 12, 0, 0)
        assert sample_analysis.analysis_text == "This building has a good layout but some potential issues."
        assert sample_analysis.complexity_score == 0.75
        assert sample_analysis.quality_score == 0.82
        assert sample_analysis.sustainability_score == 0.64
        assert sample_analysis.cost_efficiency_score == 0.71
        assert "Inadequate fire exits" in sample_analysis.detected_issues
        assert "Add emergency exit to north wing" in sample_analysis.recommendations
    
    def test_to_dict(self, sample_analysis):
        """Test conversion to dictionary"""
        analysis_dict = sample_analysis.to_dict()
        assert analysis_dict["timestamp"] == "2025-04-01T12:00:00"
        assert analysis_dict["analysis_text"] == "This building has a good layout but some potential issues."
        assert analysis_dict["complexity_score"] == 0.75
        assert analysis_dict["quality_score"] == 0.82
        assert analysis_dict["sustainability_score"] == 0.64
        assert analysis_dict["cost_efficiency_score"] == 0.71
        assert "Inadequate fire exits" in analysis_dict["detected_issues"]
        assert "Add emergency exit to north wing" in analysis_dict["recommendations"]
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        analysis_dict = {
            "timestamp": "2025-04-02T14:30:00",
            "analysis_text": "Modern office building with efficient layout.",
            "complexity_score": 0.65,
            "quality_score": 0.88,
            "sustainability_score": 0.79,
            "cost_efficiency_score": 0.68,
            "detected_issues": ["Limited natural light in core areas"],
            "recommendations": ["Add skylights to improve daylighting"]
        }
        
        analysis = AIAnalysis.from_dict(analysis_dict)
        assert analysis.timestamp == datetime(2025, 4, 2, 14, 30, 0)
        assert analysis.analysis_text == "Modern office building with efficient layout."
        assert analysis.complexity_score == 0.65
        assert analysis.quality_score == 0.88
        assert analysis.sustainability_score == 0.79
        assert analysis.cost_efficiency_score == 0.68
        assert "Limited natural light in core areas" in analysis.detected_issues
        assert "Add skylights to improve daylighting" in analysis.recommendations


class TestBIMModel:
    """Tests for BIMModel class"""
    
    @pytest.fixture
    def sample_model(self):
        """Create a sample BIM model for testing"""
        model = BIMModel(
            file_name="office_building.ifc",
            schema_version="IFC2X3",
            site_name="Downtown Office Park",
            building_name="Building A"
        )
        return model
    
    @pytest.fixture
    def sample_element(self):
        """Create a sample BIM element for testing"""
        return BIMElement(
            id="elem-001",
            global_id="2Hv$n5tL9F8RKopxqmwS4r",
            type=ElementType.WALL,
            ifc_class="IfcWall",
            name="Interior Wall",
            level="Level 1",
            material="Concrete",
            properties={"thickness": 200, "fire_rating": "2HR"}
        )
    
    def test_model_creation(self, sample_model):
        """Test BIMModel object creation"""
        assert sample_model.file_name == "office_building.ifc"
        assert sample_model.schema_version == "IFC2X3"
        assert sample_model.site_name == "Downtown Office Park"
        assert sample_model.building_name == "Building A"
        assert isinstance(sample_model.id, str)
        assert len(sample_model.elements) == 0
        assert len(sample_model.element_types) == 0
    
    def test_add_element(self, sample_model, sample_element):
        """Test adding elements to model"""
        sample_model.add_element(sample_element)
        
        # Check that element was added
        assert len(sample_model.elements) == 1
        assert sample_model.elements[0].id == "elem-001"
        
        # Check that element type was added
        assert ElementType.WALL in sample_model.element_types
        
        # Check that element is retrievable by ID
        retrieved = sample_model.get_element_by_id("elem-001")
        assert retrieved == sample_element
        
        # Check that element is retrievable by type
        by_type = sample_model.get_elements_by_type(ElementType.WALL)
        assert len(by_type) == 1
        assert by_type[0] == sample_element
    
    def test_add_multiple_elements(self, sample_model):
        """Test adding multiple elements of different types"""
        wall = BIMElement(id="wall-1", global_id="W1", type=ElementType.WALL, ifc_class="IfcWall")
        door = BIMElement(id="door-1", global_id="D1", type=ElementType.DOOR, ifc_class="IfcDoor")
        window = BIMElement(id="window-1", global_id="WIN1", type=ElementType.WINDOW, ifc_class="IfcWindow")
        
        sample_model.add_element(wall)
        sample_model.add_element(door)
        sample_model.add_element(window)
        
        assert len(sample_model.elements) == 3
        assert len(sample_model.element_types) == 3
        assert ElementType.WALL in sample_model.element_types
        assert ElementType.DOOR in sample_model.element_types
        assert ElementType.WINDOW in sample_model.element_types
        
        assert len(sample_model.get_elements_by_type(ElementType.WALL)) == 1
        assert len(sample_model.get_elements_by_type(ElementType.DOOR)) == 1
        assert len(sample_model.get_elements_by_type(ElementType.WINDOW)) == 1
        
        element_count = sample_model.get_element_count()
        assert element_count[ElementType.WALL] == 1
        assert element_count[ElementType.DOOR] == 1
        assert element_count[ElementType.WINDOW] == 1
        
        assert sample_model.get_total_element_count() == 3
    
    def test_set_ai_analysis(self, sample_model):
        """Test setting AI analysis for a model"""
        analysis = AIAnalysis(
            timestamp=datetime(2025, 4, 1, 12, 0, 0),
            analysis_text="This is a sample analysis.",
            complexity_score=0.75
        )
        
        sample_model.set_ai_analysis(analysis)
        assert sample_model.ai_analysis == analysis
    
    def test_to_dict(self, sample_model, sample_element):
        """Test conversion to dictionary"""
        sample_model.add_element(sample_element)
        
        analysis = AIAnalysis(
            timestamp=datetime(2025, 4, 1, 12, 0, 0),
            analysis_text="This is a sample analysis.",
            complexity_score=0.75
        )
        sample_model.set_ai_analysis(analysis)
        
        model_dict = sample_model.to_dict()
        assert model_dict["file_name"] == "office_building.ifc"
        assert model_dict["schema_version"] == "IFC2X3"
        assert model_dict["site_name"] == "Downtown Office Park"
        assert model_dict["building_name"] == "Building A"
        assert model_dict["total_elements"] == 1
        assert "wall" in model_dict["element_types"]
        assert model_dict["element_counts"]["wall"] == 1
        assert "ai_analysis" in model_dict
        assert model_dict["ai_analysis"]["complexity_score"] == 0.75
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        model_dict = {
            "id": "bim-001",
            "file_name": "residential.ifc",
            "schema_version": "IFC4",
            "site_name": "Hillside Estate",
            "building_name": "Residence 123",
            "upload_date": "2025-03-15T10:30:00",
            "property_id": "prop-456",
            "ai_analysis": {
                "timestamp": "2025-03-16T14:00:00",
                "analysis_text": "Residential building analysis",
                "quality_score": 0.85
            }
        }
        
        element_data = [
            {
                "id": "wall-1",
                "global_id": "W1",
                "type": "wall",
                "ifc_class": "IfcWall"
            },
            {
                "id": "door-1",
                "global_id": "D1",
                "type": "door",
                "ifc_class": "IfcDoor"
            }
        ]
        
        model, elements = BIMModel.from_dict(model_dict)
        assert model.id == "bim-001"
        assert model.file_name == "residential.ifc"
        assert model.schema_version == "IFC4"
        assert model.site_name == "Hillside Estate"
        assert model.building_name == "Residence 123"
        assert model.upload_date == datetime(2025, 3, 15, 10, 30, 0)
        assert model.property_id == "prop-456"
        assert model.ai_analysis is not None
        assert model.ai_analysis.analysis_text == "Residential building analysis"
        assert model.ai_analysis.quality_score == 0.85
        
        # Test loading elements
        assert elements == []  # Element data should be empty in the original test
        
        # Load elements manually
        model.load_elements(element_data)
        assert len(model.elements) == 2
        assert model.elements[0].id == "wall-1"
        assert model.elements[1].id == "door-1"
        assert len(model.element_types) == 2
        assert model.get_element_by_id("wall-1").ifc_class == "IfcWall"