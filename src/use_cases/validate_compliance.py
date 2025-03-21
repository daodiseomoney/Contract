from dataclasses import dataclass
from src.gateways.llm_gateway import LLMGateway
from src.entities.property import Property

@dataclass
class ComplianceResult:
    is_valid: bool
    message: str
    recommendations: list[str]

class ValidateComplianceUseCase:
    def __init__(self, llm_gateway: LLMGateway):
        self.llm_gateway = llm_gateway

    async def execute(self, property: Property) -> ComplianceResult:
        # Get compliance analysis from LLM
        analysis = await self.llm_gateway.analyze_bim_file(property.bim_file_hash)
        
        # Process safety checks
        safety_issues = analysis.get("safety_issues", [])
        if safety_issues:
            return ComplianceResult(
                is_valid=False,
                message="Safety requirements not met",
                recommendations=safety_issues
            )

        return ComplianceResult(
            is_valid=True,
            message="All compliance checks passed",
            recommendations=analysis.get("recommendations", [])
        )
