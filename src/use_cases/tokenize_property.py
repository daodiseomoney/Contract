from src.entities.property import Property, TokenizedAsset
from src.gateways.blockchain_gateway import deploy_contract
from src.gateways.llm_gateway import validate_compliance


class TokenizePropertyUseCase:
    def __init__(self, blockchain_gateway, llm_gateway):
        self.blockchain_gateway = blockchain_gateway
        self.llm_gateway = llm_gateway

    async def execute(self, property: Property, budget_splits: dict) -> TokenizedAsset:
        # Validate compliance
        compliance_result = await self.llm_gateway.validate_property(property)
        if not compliance_result.is_valid:
            raise ValueError(f"Compliance check failed: {compliance_result.message}")

        # Deploy smart contract
        contract_address = await self.blockchain_gateway.deploy_contract(
            property.bim_file_hash, budget_splits
        )

        return TokenizedAsset(
            id=0,  # DB will assign
            property_id=property.id,
            token_id=f"TOKEN_{property.id}",
            smart_contract_address=contract_address,
            budget_splits=budget_splits,
            status="active",
        )
