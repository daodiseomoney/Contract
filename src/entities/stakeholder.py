"""
Stakeholder entity for the Real Estate Tokenization platform.
Defines stakeholder types and their properties within the system.
"""

from enum import Enum, auto


class StakeholderGroup(str, Enum):
    """Enumeration of stakeholder groups in real estate transactions"""
    TENANT_BUYER = "tenant_buyer"
    BROKER = "broker"
    LANDLORD = "landlord"
    PROPERTY_MANAGER = "property_manager"
    APPRAISER = "appraiser"
    MORTGAGE_BROKER = "mortgage_broker"
    INVESTOR = "investor"
    
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to enum value with case insensitivity"""
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return cls.INVESTOR  # Default to investor if not found
    
    @classmethod
    def get_name(cls, stakeholder_type):
        """Get display name for stakeholder type"""
        name_mapping = {
            cls.TENANT_BUYER: "Tenant/Buyer",
            cls.BROKER: "Broker",
            cls.LANDLORD: "Landlord",
            cls.PROPERTY_MANAGER: "Property Manager",
            cls.APPRAISER: "Appraiser",
            cls.MORTGAGE_BROKER: "Mortgage Broker",
            cls.INVESTOR: "Investor"
        }
        return name_mapping.get(stakeholder_type, "Unknown")


class StakeholderProfile:
    """
    Profile for a stakeholder in the real estate ecosystem.
    Contains information about the stakeholder's preferences and permissions.
    """
    
    def __init__(
        self,
        group: StakeholderGroup,
        name: str = "",
        email: str = "",
        wallet_address: str = "",
        verified: bool = False
    ):
        self.group = group
        self.name = name
        self.email = email
        self.wallet_address = wallet_address
        self.verified = verified
        
    def to_dict(self):
        """Convert profile to dictionary for API responses"""
        return {
            "group": str(self.group),
            "name": self.name,
            "email": self.email,
            "wallet_address": self.wallet_address,
            "verified": self.verified
        }
    
    @property
    def permission_level(self):
        """Get permission level based on stakeholder group"""
        if self.group == StakeholderGroup.INVESTOR:
            return 3  # Highest permissions
        elif self.group in [StakeholderGroup.BROKER, StakeholderGroup.MORTGAGE_BROKER]:
            return 2  # Intermediate permissions
        else:
            return 1  # Basic permissions
            
    @classmethod
    def from_dict(cls, data):
        """Create a StakeholderProfile from a dictionary"""
        group = StakeholderGroup.from_string(data.get("group", "investor"))
        return cls(
            group=group,
            name=data.get("name", ""),
            email=data.get("email", ""),
            wallet_address=data.get("wallet_address", ""),
            verified=data.get("verified", False)
        )