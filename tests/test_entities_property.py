"""
Test cases for Property entity classes
"""

import pytest
from datetime import datetime
from src.entities.property import (
    PropertyStatus, PropertyType, Location, PropertyDetails,
    FinancialData, BIMData, RealEstateProperty
)


class TestPropertyEnums:
    """Tests for Property-related enumeration classes"""
    
    def test_property_status_values(self):
        """Test property status enumeration values"""
        assert PropertyStatus.DRAFT == "draft"
        assert PropertyStatus.PENDING == "pending"
        assert PropertyStatus.TOKENIZED == "tokenized"
        assert PropertyStatus.LISTED == "listed"
        assert PropertyStatus.SOLD == "sold"
        assert PropertyStatus.ARCHIVED == "archived"
        
    def test_property_type_values(self):
        """Test property type enumeration values"""
        assert PropertyType.RESIDENTIAL == "residential"
        assert PropertyType.COMMERCIAL == "commercial"
        assert PropertyType.INDUSTRIAL == "industrial"
        assert PropertyType.LAND == "land"
        assert PropertyType.MIXED_USE == "mixed_use"


class TestLocation:
    """Tests for Location class"""
    
    @pytest.fixture
    def sample_location(self):
        """Create a sample location for testing"""
        return Location(
            address="123 Main St",
            city="Metropolis",
            state="NY",
            zip_code="10001",
            country="USA",
            coordinates={"latitude": 40.7128, "longitude": -74.0060}
        )
    
    def test_location_creation(self, sample_location):
        """Test Location object creation"""
        assert sample_location.address == "123 Main St"
        assert sample_location.city == "Metropolis"
        assert sample_location.state == "NY"
        assert sample_location.zip_code == "10001"
        assert sample_location.country == "USA"
        assert sample_location.coordinates["latitude"] == 40.7128
        assert sample_location.coordinates["longitude"] == -74.0060
        
    def test_to_dict(self, sample_location):
        """Test conversion to dictionary"""
        location_dict = sample_location.to_dict()
        assert location_dict["address"] == "123 Main St"
        assert location_dict["city"] == "Metropolis"
        assert location_dict["state"] == "NY"
        assert location_dict["zip_code"] == "10001"
        assert location_dict["country"] == "USA"
        assert location_dict["coordinates"]["latitude"] == 40.7128
        assert location_dict["coordinates"]["longitude"] == -74.0060


class TestPropertyDetails:
    """Tests for PropertyDetails class"""
    
    @pytest.fixture
    def sample_details(self):
        """Create sample property details for testing"""
        return PropertyDetails(
            size_sqft=2500.0,
            bedrooms=4,
            bathrooms=2.5,
            year_built=1998,
            lot_size_sqft=5000.0,
            features=["Hardwood floors", "Granite countertops"],
            amenities=["Pool", "Gym"]
        )
    
    def test_details_creation(self, sample_details):
        """Test PropertyDetails object creation"""
        assert sample_details.size_sqft == 2500.0
        assert sample_details.bedrooms == 4
        assert sample_details.bathrooms == 2.5
        assert sample_details.year_built == 1998
        assert sample_details.lot_size_sqft == 5000.0
        assert "Hardwood floors" in sample_details.features
        assert "Pool" in sample_details.amenities
        
    def test_to_dict(self, sample_details):
        """Test conversion to dictionary"""
        details_dict = sample_details.to_dict()
        assert details_dict["size_sqft"] == 2500.0
        assert details_dict["bedrooms"] == 4
        assert details_dict["bathrooms"] == 2.5
        assert details_dict["year_built"] == 1998
        assert details_dict["lot_size_sqft"] == 5000.0
        assert "Granite countertops" in details_dict["features"]
        assert "Gym" in details_dict["amenities"]


class TestFinancialData:
    """Tests for FinancialData class"""
    
    @pytest.fixture
    def sample_financials(self):
        """Create sample financial data for testing"""
        return FinancialData(
            purchase_price=500000.0,
            current_valuation=550000.0,
            token_price=550.0,
            total_tokens=1000,
            available_tokens=750,
            annual_return=7.5,
            rental_income=36000.0,
            expenses=12000.0
        )
    
    def test_financials_creation(self, sample_financials):
        """Test FinancialData object creation"""
        assert sample_financials.purchase_price == 500000.0
        assert sample_financials.current_valuation == 550000.0
        assert sample_financials.token_price == 550.0
        assert sample_financials.total_tokens == 1000
        assert sample_financials.available_tokens == 750
        assert sample_financials.annual_return == 7.5
        assert sample_financials.rental_income == 36000.0
        assert sample_financials.expenses == 12000.0
        
    def test_to_dict(self, sample_financials):
        """Test conversion to dictionary"""
        financials_dict = sample_financials.to_dict()
        assert financials_dict["purchase_price"] == 500000.0
        assert financials_dict["current_valuation"] == 550000.0
        assert financials_dict["token_price"] == 550.0
        assert financials_dict["total_tokens"] == 1000
        assert financials_dict["available_tokens"] == 750
        assert financials_dict["annual_return"] == 7.5
        assert financials_dict["rental_income"] == 36000.0
        assert financials_dict["expenses"] == 12000.0


class TestBIMData:
    """Tests for BIMData class"""
    
    @pytest.fixture
    def sample_bim_data(self):
        """Create sample BIM data for testing"""
        return BIMData(
            model_id="bim-001",
            file_name="office_building.ifc",
            upload_date=datetime(2025, 3, 15, 10, 30, 0),
            element_count=1250,
            schema_version="IFC2X3",
            has_ai_analysis=True
        )
    
    def test_bim_data_creation(self, sample_bim_data):
        """Test BIMData object creation"""
        assert sample_bim_data.model_id == "bim-001"
        assert sample_bim_data.file_name == "office_building.ifc"
        assert sample_bim_data.upload_date == datetime(2025, 3, 15, 10, 30, 0)
        assert sample_bim_data.element_count == 1250
        assert sample_bim_data.schema_version == "IFC2X3"
        assert sample_bim_data.has_ai_analysis is True
        
    def test_to_dict(self, sample_bim_data):
        """Test conversion to dictionary"""
        bim_dict = sample_bim_data.to_dict()
        assert bim_dict["model_id"] == "bim-001"
        assert bim_dict["file_name"] == "office_building.ifc"
        assert bim_dict["upload_date"] == "2025-03-15T10:30:00"
        assert bim_dict["element_count"] == 1250
        assert bim_dict["schema_version"] == "IFC2X3"
        assert bim_dict["has_ai_analysis"] is True


class TestRealEstateProperty:
    """Tests for RealEstateProperty class"""
    
    @pytest.fixture
    def sample_location(self):
        return Location(
            address="123 Main St",
            city="Metropolis",
            state="NY",
            zip_code="10001",
            country="USA"
        )
    
    @pytest.fixture
    def sample_details(self):
        return PropertyDetails(
            size_sqft=2500.0,
            bedrooms=4,
            bathrooms=2.5
        )
    
    @pytest.fixture
    def sample_financials(self):
        return FinancialData(
            purchase_price=500000.0,
            current_valuation=550000.0,
            token_price=550.0,
            total_tokens=1000
        )
    
    @pytest.fixture
    def sample_bim_data(self):
        return BIMData(
            model_id="bim-001",
            file_name="office_building.ifc",
            upload_date=datetime(2025, 3, 15, 10, 30, 0)
        )
    
    @pytest.fixture
    def sample_property(self, sample_location, sample_details, sample_financials):
        """Create a sample property for testing"""
        return RealEstateProperty(
            name="Downtown Office",
            property_type=PropertyType.COMMERCIAL,
            location=sample_location,
            details=sample_details,
            financials=sample_financials,
            status=PropertyStatus.PENDING
        )
    
    def test_property_creation(self, sample_property, sample_location, sample_details, sample_financials):
        """Test RealEstateProperty object creation"""
        assert sample_property.name == "Downtown Office"
        assert sample_property.property_type == PropertyType.COMMERCIAL
        assert sample_property.location == sample_location
        assert sample_property.details == sample_details
        assert sample_property.financials == sample_financials
        assert sample_property.status == PropertyStatus.PENDING
        assert isinstance(sample_property.id, str)
        assert isinstance(sample_property.created_at, datetime)
        assert isinstance(sample_property.updated_at, datetime)
        assert sample_property.owner_wallet_address is None
        assert sample_property.contract_address is None
        assert sample_property.images == []
        assert sample_property.bim_data is None
        
    def test_property_with_bim_data(self, sample_location, sample_details, sample_financials, sample_bim_data):
        """Test property creation with BIM data"""
        property_with_bim = RealEstateProperty(
            name="Downtown Office",
            property_type=PropertyType.COMMERCIAL,
            location=sample_location,
            details=sample_details,
            financials=sample_financials,
            bim_data=sample_bim_data
        )
        
        assert property_with_bim.bim_data == sample_bim_data
        
    def test_to_dict(self, sample_property):
        """Test conversion to dictionary"""
        property_dict = sample_property.to_dict()
        assert property_dict["name"] == "Downtown Office"
        assert property_dict["property_type"] == "commercial"
        assert property_dict["status"] == "pending"
        assert "location" in property_dict
        assert property_dict["location"]["address"] == "123 Main St"
        assert "details" in property_dict
        assert property_dict["details"]["size_sqft"] == 2500.0
        assert "financials" in property_dict
        assert property_dict["financials"]["purchase_price"] == 500000.0
        assert "bim_data" not in property_dict
        
    def test_from_dict(self):
        """Test creation from dictionary"""
        property_dict = {
            "id": "prop-001",
            "name": "Lakeside Condo",
            "property_type": "residential",
            "status": "tokenized",
            "location": {
                "address": "456 Lake Dr",
                "city": "Laketown",
                "state": "CA",
                "zip_code": "90210",
                "country": "USA"
            },
            "details": {
                "size_sqft": 1800.0,
                "bedrooms": 3,
                "bathrooms": 2.0,
                "year_built": 2010
            },
            "financials": {
                "purchase_price": 450000.0,
                "current_valuation": 500000.0,
                "token_price": 500.0,
                "total_tokens": 1000,
                "available_tokens": 500
            },
            "bim_data": {
                "model_id": "bim-002",
                "file_name": "lakeside_condo.ifc",
                "upload_date": "2025-02-10T09:15:00",
                "element_count": 850,
                "schema_version": "IFC4",
                "has_ai_analysis": False
            },
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-02-15T12:30:00",
            "owner_wallet_address": "cosmos1xyzabc123456",
            "contract_address": "cosmos1contractabc123",
            "images": ["image1.jpg", "image2.jpg"]
        }
        
        property_obj = RealEstateProperty.from_dict(property_dict)
        assert property_obj.id == "prop-001"
        assert property_obj.name == "Lakeside Condo"
        assert property_obj.property_type == PropertyType.RESIDENTIAL
        assert property_obj.status == PropertyStatus.TOKENIZED
        assert property_obj.location.city == "Laketown"
        assert property_obj.details.size_sqft == 1800.0
        assert property_obj.details.bedrooms == 3
        assert property_obj.financials.purchase_price == 450000.0
        assert property_obj.bim_data is not None
        assert property_obj.bim_data.model_id == "bim-002"
        assert property_obj.bim_data.schema_version == "IFC4"
        assert property_obj.created_at == datetime(2025, 1, 1, 0, 0, 0)
        assert property_obj.updated_at == datetime(2025, 2, 15, 12, 30, 0)
        assert property_obj.owner_wallet_address == "cosmos1xyzabc123456"
        assert property_obj.contract_address == "cosmos1contractabc123"
        assert len(property_obj.images) == 2
        assert "image1.jpg" in property_obj.images
        
    def test_update(self, sample_property):
        """Test updating property with new data"""
        update_data = {
            "name": "Updated Office Name",
            "status": "tokenized",
            "owner_wallet_address": "cosmos1newowner123",
            "contract_address": "cosmos1newcontract456",
            "location": {
                "city": "New City",
                "state": "CA"
            },
            "details": {
                "size_sqft": 3000.0,
                "year_built": 2005
            },
            "financials": {
                "current_valuation": 600000.0,
                "available_tokens": 800
            },
            "images": ["new_image.jpg"]
        }
        
        old_updated_at = sample_property.updated_at
        sample_property.update(update_data)
        
        # Check that fields were updated
        assert sample_property.name == "Updated Office Name"
        assert sample_property.status == PropertyStatus.TOKENIZED
        assert sample_property.owner_wallet_address == "cosmos1newowner123"
        assert sample_property.contract_address == "cosmos1newcontract456"
        assert sample_property.location.city == "New City"
        assert sample_property.location.state == "CA"
        assert sample_property.details.size_sqft == 3000.0
        assert sample_property.details.year_built == 2005
        assert sample_property.financials.current_valuation == 600000.0
        assert sample_property.financials.available_tokens == 800
        assert sample_property.images == ["new_image.jpg"]
        
        # Check that updated_at was changed
        assert sample_property.updated_at > old_updated_at