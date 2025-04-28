"""
Test cases for Role entity class
"""

import pytest
from src.entities.role import RoleType, Role


class TestRoleType:
    """Tests for RoleType enum"""
    
    def test_role_type_values(self):
        """Test role type enumeration values"""
        assert RoleType.LANDLORD.value == "landlord"
        assert RoleType.ARCHITECT.value == "architect"
        assert RoleType.CONTRACTOR.value == "contractor"
        assert RoleType.INVESTOR.value == "investor"
        assert RoleType.BROKER.value == "broker"


class TestRole:
    """Tests for Role class"""
    
    @pytest.fixture
    def landlord_role(self):
        """Create a landlord role for testing"""
        return Role(
            id=1,
            user_id=101,
            role_type=RoleType.LANDLORD,
            permissions=["create", "read", "update", "tokenize"]
        )
    
    @pytest.fixture
    def architect_role(self):
        """Create an architect role for testing"""
        return Role(
            id=2,
            user_id=102,
            role_type=RoleType.ARCHITECT,
            permissions=["read", "upload_bim", "comment"]
        )
    
    @pytest.fixture
    def broker_role(self):
        """Create a broker role for testing"""
        return Role(
            id=3,
            user_id=103,
            role_type=RoleType.BROKER,
            permissions=["read", "list", "sell"]
        )
    
    def test_role_creation(self, landlord_role):
        """Test Role object creation"""
        assert landlord_role.id == 1
        assert landlord_role.user_id == 101
        assert landlord_role.role_type == RoleType.LANDLORD
        assert "create" in landlord_role.permissions
        assert "tokenize" in landlord_role.permissions
        
    def test_can_tokenize(self, landlord_role, architect_role, broker_role):
        """Test can_tokenize permission check"""
        assert landlord_role.can_tokenize() is True  # Landlord can tokenize
        assert architect_role.can_tokenize() is False  # Architect cannot tokenize
        assert broker_role.can_tokenize() is False  # Broker cannot tokenize
        
    def test_can_upload_bim(self, landlord_role, architect_role, broker_role):
        """Test can_upload_bim permission check"""
        assert landlord_role.can_upload_bim() is False  # Landlord cannot upload BIM
        assert architect_role.can_upload_bim() is True  # Architect can upload BIM
        assert broker_role.can_upload_bim() is False  # Broker cannot upload BIM