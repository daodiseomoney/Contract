"""
Test cases for the ValidateComplianceUseCase
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.entities.property import RealEstateProperty, PropertyType, Location, PropertyDetails, FinancialData, BIMData
from src.use_cases.validate_compliance import ValidateComplianceUseCase, ComplianceResult


class TestValidateComplianceUseCase:
    """Tests for ValidateComplianceUseCase"""
    
    @pytest.fixture
    def mock_llm_gateway(self):
        """Create a mock LLM gateway for testing"""
        mock = Mock()
        mock.analyze_bim_file = AsyncMock()
        mock.validate_property = AsyncMock()
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
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_property(self, mock_llm_gateway, sample_property_with_bim):
        """Test executing use case with a valid property (no safety issues)"""
        # Configure mock to return analysis with no safety issues
        mock_llm_gateway.analyze_bim_file.return_value = {
            "safety_issues": [],
            "recommendations": ["Improve insulation", "Add solar panels"]
        }
        
        # Create use case and execute
        use_case = ValidateComplianceUseCase(mock_llm_gateway)
        result = await use_case.execute(sample_property_with_bim)
        
        # Verify LLM gateway was called with correct model ID
        mock_llm_gateway.analyze_bim_file.assert_called_once_with("bim-001")
        
        # Verify result is as expected
        assert isinstance(result, ComplianceResult)
        assert result.is_valid is True
        assert result.message == "All compliance checks passed"
        assert len(result.recommendations) == 2
        assert "Improve insulation" in result.recommendations
        assert "Add solar panels" in result.recommendations
    
    @pytest.mark.asyncio
    async def test_execute_with_safety_issues(self, mock_llm_gateway, sample_property_with_bim):
        """Test executing use case with a property that has safety issues"""
        # Configure mock to return analysis with safety issues
        mock_llm_gateway.analyze_bim_file.return_value = {
            "safety_issues": ["Inadequate fire exits", "Missing smoke detectors"],
            "recommendations": ["Add emergency exit", "Install smoke detectors"]
        }
        
        # Create use case and execute
        use_case = ValidateComplianceUseCase(mock_llm_gateway)
        result = await use_case.execute(sample_property_with_bim)
        
        # Verify LLM gateway was called with correct model ID
        mock_llm_gateway.analyze_bim_file.assert_called_once_with("bim-001")
        
        # Verify result is as expected
        assert isinstance(result, ComplianceResult)
        assert result.is_valid is False
        assert result.message == "Safety requirements not met"
        assert len(result.recommendations) == 2
        assert "Inadequate fire exits" in result.recommendations
        assert "Missing smoke detectors" in result.recommendations
    
    @pytest.mark.asyncio
    async def test_execute_without_bim_data(self, mock_llm_gateway, sample_property_without_bim):
        """Test executing use case with a property that has no BIM data (should raise error)"""
        use_case = ValidateComplianceUseCase(mock_llm_gateway)
        
        # Executing with property without BIM data should raise ValueError
        with pytest.raises(ValueError, match="Property must have associated BIM model"):
            await use_case.execute(sample_property_without_bim)
        
        # Verify LLM gateway was not called
        mock_llm_gateway.analyze_bim_file.assert_not_called()