from dataclasses import dataclass
from typing import List, Dict, Any, Protocol
from src.entities.property import RealEstateProperty


class LLMGateway(Protocol):
    """
    Protocol defining the interface for LLM Gateway implementations
    """
    async def analyze_bim_file(self, model_id: str) -> Dict[str, Any]:
        """
        Analyze a BIM file using an LLM
        
        Args:
            model_id: ID of the BIM model to analyze
            
        Returns:
            Dict with analysis results
        """
        ...
    
    async def validate_property(self, property_obj: RealEstateProperty) -> 'ComplianceResult':
        """
        Validate a property for compliance
        
        Args:
            property_obj: Property to validate
            
        Returns:
            ComplianceResult with validation status and recommendations
        """
        ...


@dataclass
class ComplianceResult:
    """
    Result of a property compliance validation check
    """
    is_valid: bool
    message: str
    recommendations: List[str]


class ValidateComplianceUseCase:
    """
    Use case for validating property compliance using AI analysis
    """
    def __init__(self, llm_gateway: LLMGateway):
        self.llm_gateway = llm_gateway

    async def execute(self, property_obj: RealEstateProperty) -> ComplianceResult:
        """
        Execute the compliance validation process
        
        Args:
            property_obj: Property to validate
            
        Returns:
            ComplianceResult with validation status and recommendations
            
        Raises:
            ValueError: If property has no BIM data
        """
        # Check if property has BIM data
        if not property_obj.bim_data or not property_obj.bim_data.model_id:
            raise ValueError("Property must have associated BIM model to validate compliance")
            
        # Get compliance analysis from LLM
        analysis = await self.llm_gateway.analyze_bim_file(property_obj.bim_data.model_id)

        # Process safety checks
        safety_issues = analysis.get("safety_issues", [])
        if safety_issues:
            return ComplianceResult(
                is_valid=False,
                message="Safety requirements not met",
                recommendations=safety_issues,
            )

        return ComplianceResult(
            is_valid=True,
            message="All compliance checks passed",
            recommendations=analysis.get("recommendations", []),
        )
