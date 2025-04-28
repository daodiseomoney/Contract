from dataclasses import dataclass
from typing import Dict, Optional
from src.entities.property import RealEstateProperty, PropertyStatus


@dataclass
class TokenizedAsset:
    """
    Represents a property that has been tokenized on the blockchain.
    """
    property_id: str
    token_id: str
    smart_contract_address: str
    budget_splits: Dict[str, float]
    status: str = "active"
    id: Optional[int] = None


class TokenizePropertyUseCase:
    """
    Use case for tokenizing a real estate property on the blockchain.
    """
    def __init__(self, blockchain_gateway, llm_gateway):
        self.blockchain_gateway = blockchain_gateway
        self.llm_gateway = llm_gateway

    async def execute(self, property_obj: RealEstateProperty, budget_splits: Dict[str, float]) -> TokenizedAsset:
        """
        Execute the tokenization process:
        1. Validate property compliance
        2. Deploy blockchain contract
        3. Return the tokenized asset
        
        Args:
            property_obj: The property to tokenize
            budget_splits: Dictionary mapping stakeholders to their percentage share
            
        Returns:
            TokenizedAsset: The newly created tokenized asset
            
        Raises:
            ValueError: If compliance validation fails
        """
        # Validate compliance
        compliance_result = await self.llm_gateway.validate_property(property_obj)
        if not compliance_result.is_valid:
            raise ValueError(f"Compliance check failed: {compliance_result.message}")

        # Get file hash from BIM data if available
        file_hash = None
        if property_obj.bim_data and property_obj.bim_data.model_id:
            file_hash = property_obj.bim_data.model_id
        
        if not file_hash:
            raise ValueError("Property must have associated BIM model to tokenize")

        # Deploy smart contract
        contract_address = await self.blockchain_gateway.deploy_contract(
            file_hash, budget_splits
        )
        
        # Update property status
        property_obj.status = PropertyStatus.TOKENIZED
        property_obj.contract_address = contract_address

        return TokenizedAsset(
            id=None,  # DB will assign
            property_id=property_obj.id,
            token_id=f"TOKEN_{property_obj.id}",
            smart_contract_address=contract_address,
            budget_splits=budget_splits,
            status="active",
        )
