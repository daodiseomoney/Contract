"""
Property entity for the Real Estate Tokenization platform.
Defines core domain objects related to real estate property management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import uuid4


class PropertyStatus(str, Enum):
    """Status of a property in the tokenization platform"""
    DRAFT = "draft"
    PENDING = "pending"
    TOKENIZED = "tokenized"
    LISTED = "listed"
    SOLD = "sold"
    ARCHIVED = "archived"


class PropertyType(str, Enum):
    """Types of real estate properties supported by the platform"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    LAND = "land"
    MIXED_USE = "mixed_use"


@dataclass
class Location:
    """Geographic location information"""
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    coordinates: Optional[Dict[str, float]] = None  # Longitude, latitude
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "coordinates": self.coordinates
        }


@dataclass
class PropertyDetails:
    """Detailed property information"""
    size_sqft: float = 0.0
    bedrooms: int = 0
    bathrooms: float = 0.0
    year_built: Optional[int] = None
    lot_size_sqft: Optional[float] = None
    features: List[str] = field(default_factory=list)
    amenities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "size_sqft": self.size_sqft,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "year_built": self.year_built,
            "lot_size_sqft": self.lot_size_sqft,
            "features": self.features,
            "amenities": self.amenities
        }


@dataclass
class FinancialData:
    """Financial information related to the property"""
    purchase_price: float = 0.0
    current_valuation: float = 0.0
    token_price: float = 0.0
    total_tokens: int = 0
    available_tokens: int = 0
    annual_return: Optional[float] = None
    rental_income: Optional[float] = None
    expenses: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "purchase_price": self.purchase_price,
            "current_valuation": self.current_valuation,
            "token_price": self.token_price,
            "total_tokens": self.total_tokens,
            "available_tokens": self.available_tokens,
            "annual_return": self.annual_return,
            "rental_income": self.rental_income,
            "expenses": self.expenses
        }


@dataclass
class BIMData:
    """Building Information Model data"""
    model_id: str
    file_name: str
    upload_date: datetime
    element_count: int = 0
    schema_version: str = ""
    has_ai_analysis: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "model_id": self.model_id,
            "file_name": self.file_name,
            "upload_date": self.upload_date.isoformat(),
            "element_count": self.element_count,
            "schema_version": self.schema_version,
            "has_ai_analysis": self.has_ai_analysis
        }


class RealEstateProperty:
    """
    Real Estate Property entity representing a physical property
    that can be tokenized on the blockchain.
    """
    
    def __init__(
        self,
        name: str,
        property_type: PropertyType,
        location: Location,
        details: PropertyDetails,
        financials: FinancialData,
        bim_data: Optional[BIMData] = None,
        status: PropertyStatus = PropertyStatus.DRAFT
    ):
        self.id = str(uuid4())
        self.name = name
        self.property_type = property_type
        self.location = location
        self.details = details
        self.financials = financials
        self.bim_data = bim_data
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.owner_wallet_address: Optional[str] = None
        self.contract_address: Optional[str] = None
        self.images: List[str] = []
        
    def to_dict(self) -> Dict:
        """Convert property to dictionary for API responses"""
        result = {
            "id": self.id,
            "name": self.name,
            "property_type": self.property_type.value,
            "status": self.status.value,
            "location": self.location.to_dict(),
            "details": self.details.to_dict(),
            "financials": self.financials.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner_wallet_address": self.owner_wallet_address,
            "contract_address": self.contract_address,
            "images": self.images
        }
        
        if self.bim_data:
            result["bim_data"] = self.bim_data.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RealEstateProperty':
        """Create a RealEstateProperty from a dictionary"""
        # Parse nested objects
        location = Location(**data.get("location", {}))
        details = PropertyDetails(**data.get("details", {}))
        financials = FinancialData(**data.get("financials", {}))
        
        # Parse BIM data if present
        bim_data = None
        if "bim_data" in data:
            bim_data_dict = data["bim_data"]
            # Convert string date to datetime
            upload_date = datetime.fromisoformat(bim_data_dict.get("upload_date"))
            bim_data_dict["upload_date"] = upload_date
            bim_data = BIMData(**bim_data_dict)
        
        # Create property object
        property_type = PropertyType(data.get("property_type", "residential"))
        status = PropertyStatus(data.get("status", "draft"))
        
        property_obj = cls(
            name=data.get("name", "Unnamed Property"),
            property_type=property_type,
            location=location,
            details=details,
            financials=financials,
            bim_data=bim_data,
            status=status
        )
        
        # Set additional fields
        if "id" in data:
            property_obj.id = data["id"]
        if "created_at" in data:
            property_obj.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            property_obj.updated_at = datetime.fromisoformat(data["updated_at"])
        if "owner_wallet_address" in data:
            property_obj.owner_wallet_address = data["owner_wallet_address"]
        if "contract_address" in data:
            property_obj.contract_address = data["contract_address"]
        if "images" in data:
            property_obj.images = data["images"]
            
        return property_obj
    
    def update(self, data: Dict) -> None:
        """Update property with new data"""
        self.updated_at = datetime.now()
        
        # Update simple fields
        if "name" in data:
            self.name = data["name"]
        if "property_type" in data:
            self.property_type = PropertyType(data["property_type"])
        if "status" in data:
            self.status = PropertyStatus(data["status"])
        if "owner_wallet_address" in data:
            self.owner_wallet_address = data["owner_wallet_address"]
        if "contract_address" in data:
            self.contract_address = data["contract_address"]
        if "images" in data:
            self.images = data["images"]
            
        # Update nested objects
        if "location" in data:
            for key, value in data["location"].items():
                setattr(self.location, key, value)
                
        if "details" in data:
            for key, value in data["details"].items():
                setattr(self.details, key, value)
                
        if "financials" in data:
            for key, value in data["financials"].items():
                setattr(self.financials, key, value)