"""
Test cases for the TokenizePropertyUseCase
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.entities.property import RealEstateProperty, PropertyType, PropertyStatus, Location, PropertyDetails, FinancialData, BIMData
from src.use_cases.tokenize_property import TokenizePropertyUseCase, TokenizedAsset
from src.use_cases.validate_compliance import ComplianceResult


class TestTokenizePropertyUseCase:
    """Tests for TokenizePropertyUseCase"""
    
    @pytest.fixture
    def mock_blockchain_gateway(self):
        """Create a mock blockchain gateway for testing"""
        mock = Mock()
        mock.deploy_contract = AsyncMock(return_value="cosmos1contract123")
        return mock
    
    @pytest.fixture
    def mock_llm_gateway(self):
        """Create a mock LLM gateway for testing"""
        mock = Mock()
        mock.validate_property = AsyncMock(
            return_value=ComplianceResult(
                is_valid=True,
                message="All compliance checks passed",
                recommendations=[]
            )
        )
        return mock
    
    @pytest.fixture
    def sample_property_with_bim(self):
        """Create a sample property with BIM data for testing"""
        location = Location(
            address="123 Main St",
            city="Metropolis",
            state="NY",
            zip_code="10001",
            country="USA"
        )
        
        details = PropertyDetails(
            size_sqft=2500.0,
            bedrooms=4,
            bathrooms=2.5
        )
        
        financials = FinancialData(
            purchase_price=500000.0,
            current_valuation=550000.0,
            token_price=550.0,
            total_tokens=1000
        )
        
        bim_data = BIMData(
            model_id="bim-001",
            file_name="office_building.ifc",
            upload_date=datetime(2025, 3, 15, 10, 30, 0)
        )
        
        return RealEstateProperty(
            name="Downtown Office",
            property_type=PropertyType.COMMERCIAL,
            location=location,
            details=details,
            financials=financials,
            bim_data=bim_data
        )
    
    @pytest.fixture
    def sample_property_without_bim(self):
        """Create a sample property without BIM data for testing"""
        location = Location(
            address="123 Main St",
            city="Metropolis",
            state="NY",
            zip_code="10001",
            country="USA"
        )
        
        details = PropertyDetails(
            size_sqft=2500.0,
            bedrooms=4,
            bathrooms=2.5
        )
        
        financials = FinancialData(
            purchase_price=500000.0,
            current_valuation=550000.0,
            token_price=550.0,
            total_tokens=1000
        )
        
        return RealEstateProperty(
            name="Downtown Office",
            property_type=PropertyType.COMMERCIAL,
            location=location,
            details=details,
            financials=financials
        )
    
    @pytest.fixture
    def sample_budget_splits(self):
        """Create a sample budget splits dictionary for testing"""
        return {
            "owner": 0.7,
            "developer": 0.2,
            "maintenance": 0.1
        }
    
    @pytest.mark.asyncio
    async def test_execute_successful_tokenization(
        self, 
        mock_blockchain_gateway, 
        mock_llm_gateway, 
        sample_property_with_bim, 
        sample_budget_splits
    ):
        """Test successful property tokenization"""
        # Create use case and execute
        use_case = TokenizePropertyUseCase(mock_blockchain_gateway, mock_llm_gateway)
        tokenized_asset = await use_case.execute(sample_property_with_bim, sample_budget_splits)
        
        # Verify gateway methods were called correctly
        mock_llm_gateway.validate_property.assert_called_once_with(sample_property_with_bim)
        mock_blockchain_gateway.deploy_contract.assert_called_once_with("bim-001", sample_budget_splits)
        
        # Verify tokenized asset was created correctly
        assert isinstance(tokenized_asset, TokenizedAsset)
        assert tokenized_asset.property_id == sample_property_with_bim.id
        assert tokenized_asset.token_id == f"TOKEN_{sample_property_with_bim.id}"
        assert tokenized_asset.smart_contract_address == "cosmos1contract123"
        assert tokenized_asset.budget_splits == sample_budget_splits
        assert tokenized_asset.status == "active"
        
        # Verify property was updated correctly
        assert sample_property_with_bim.status == PropertyStatus.TOKENIZED
        assert sample_property_with_bim.contract_address == "cosmos1contract123"
    
    @pytest.mark.asyncio
    async def test_execute_with_compliance_failure(
        self, 
        mock_blockchain_gateway, 
        mock_llm_gateway, 
        sample_property_with_bim, 
        sample_budget_splits
    ):
        """Test tokenization with compliance failure"""
        # Configure mock to return compliance failure
        mock_llm_gateway.validate_property.return_value = ComplianceResult(
            is_valid=False,
            message="Safety requirements not met",
            recommendations=["Fix fire exits"]
        )
        
        # Create use case
        use_case = TokenizePropertyUseCase(mock_blockchain_gateway, mock_llm_gateway)
        
        # Execute should raise ValueError
        with pytest.raises(ValueError, match="Compliance check failed"):
            await use_case.execute(sample_property_with_bim, sample_budget_splits)
        
        # Verify gateway methods were called correctly
        mock_llm_gateway.validate_property.assert_called_once_with(sample_property_with_bim)
        mock_blockchain_gateway.deploy_contract.assert_not_called()
        
        # Verify property was not updated
        assert sample_property_with_bim.status != PropertyStatus.TOKENIZED
        assert sample_property_with_bim.contract_address is None
    
    @pytest.mark.asyncio
    async def test_execute_without_bim_data(
        self, 
        mock_blockchain_gateway, 
        mock_llm_gateway, 
        sample_property_without_bim, 
        sample_budget_splits
    ):
        """Test tokenization with a property that has no BIM data"""
        # Create use case
        use_case = TokenizePropertyUseCase(mock_blockchain_gateway, mock_llm_gateway)
        
        # Execute should raise ValueError
        with pytest.raises(ValueError, match="Property must have associated BIM model"):
            await use_case.execute(sample_property_without_bim, sample_budget_splits)
        
        # Verify gateway methods were not called
        mock_llm_gateway.validate_property.assert_called_once_with(sample_property_without_bim)
        mock_blockchain_gateway.deploy_contract.assert_not_called()