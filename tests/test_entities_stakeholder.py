"""
Test cases for Stakeholder entity classes
"""

import pytest
from src.entities.stakeholder import StakeholderGroup, StakeholderProfile


class TestStakeholderGroup:
    """Tests for StakeholderGroup enum"""
    
    def test_stakeholder_group_values(self):
        """Test stakeholder group enumeration values"""
        assert StakeholderGroup.TENANT_BUYER == "tenant_buyer"
        assert StakeholderGroup.BROKER == "broker"
        assert StakeholderGroup.LANDLORD == "landlord"
        assert StakeholderGroup.PROPERTY_MANAGER == "property_manager"
        assert StakeholderGroup.APPRAISER == "appraiser"
        assert StakeholderGroup.MORTGAGE_BROKER == "mortgage_broker"
        assert StakeholderGroup.INVESTOR == "investor"
        
    def test_to_string(self):
        """Test string conversion of enum values"""
        assert str(StakeholderGroup.TENANT_BUYER) == "tenant_buyer"
        assert str(StakeholderGroup.BROKER) == "broker"
        assert str(StakeholderGroup.LANDLORD) == "landlord"
        
    def test_from_string(self):
        """Test creation from string with case insensitivity"""
        assert StakeholderGroup.from_string("tenant_buyer") == StakeholderGroup.TENANT_BUYER
        assert StakeholderGroup.from_string("BROKER") == StakeholderGroup.BROKER
        assert StakeholderGroup.from_string("Landlord") == StakeholderGroup.LANDLORD
        assert StakeholderGroup.from_string("nonexistent") == StakeholderGroup.INVESTOR  # Default


class TestStakeholderProfile:
    """Tests for StakeholderProfile class"""
    
    @pytest.fixture
    def sample_profile(self):
        """Create a sample stakeholder profile for testing"""
        return StakeholderProfile(
            group=StakeholderGroup.BROKER,
            name="Jane Smith",
            email="jane@example.com",
            wallet_address="cosmos1abcdef123456789",
            verified=True
        )
    
    def test_profile_creation(self, sample_profile):
        """Test StakeholderProfile object creation"""
        assert sample_profile.group == StakeholderGroup.BROKER
        assert sample_profile.name == "Jane Smith"
        assert sample_profile.email == "jane@example.com"
        assert sample_profile.wallet_address == "cosmos1abcdef123456789"
        assert sample_profile.verified is True
        
    def test_to_dict(self, sample_profile):
        """Test conversion to dictionary"""
        profile_dict = sample_profile.to_dict()
        assert profile_dict["group"] == "broker"
        assert profile_dict["name"] == "Jane Smith"
        assert profile_dict["email"] == "jane@example.com"
        assert profile_dict["wallet_address"] == "cosmos1abcdef123456789"
        assert profile_dict["verified"] is True
        
    def test_from_dict(self):
        """Test creation from dictionary"""
        profile_dict = {
            "group": "landlord",
            "name": "John Doe",
            "email": "john@example.com",
            "wallet_address": "cosmos1xyz987654321",
            "verified": False
        }
        
        profile = StakeholderProfile.from_dict(profile_dict)
        assert profile.group == StakeholderGroup.LANDLORD
        assert profile.name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.wallet_address == "cosmos1xyz987654321"
        assert profile.verified is False
        
    def test_from_dict_defaults(self):
        """Test default values when creating from incomplete dictionary"""
        profile = StakeholderProfile.from_dict({"group": "investor"})
        assert profile.group == StakeholderGroup.INVESTOR
        assert profile.name == ""
        assert profile.email == ""
        assert profile.wallet_address == ""
        assert profile.verified is False
        
    def test_permission_level(self):
        """Test permission level calculation based on stakeholder group"""
        investor = StakeholderProfile(group=StakeholderGroup.INVESTOR)
        broker = StakeholderProfile(group=StakeholderGroup.BROKER)
        mortgage_broker = StakeholderProfile(group=StakeholderGroup.MORTGAGE_BROKER)
        tenant = StakeholderProfile(group=StakeholderGroup.TENANT_BUYER)
        
        assert investor.permission_level == 3  # Highest
        assert broker.permission_level == 2  # Intermediate
        assert mortgage_broker.permission_level == 2  # Intermediate
        assert tenant.permission_level == 1  # Basic