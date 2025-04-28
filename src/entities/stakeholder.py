"""
Stakeholder entities for the Real Estate Tokenization Platform.
Defines stakeholder groups and related domain objects.
"""

from typing import List


class StakeholderGroup:
    """
    Defines stakeholder groups in the real estate domain.
    These are used to categorize users and customize their experience.
    """
    TENANT_BUYER = "tenant_buyer"
    BROKER = "broker"
    LANDLORD = "landlord"
    PROPERTY_MANAGER = "property_manager"
    APPRAISER = "appraiser"
    MORTGAGE_BROKER = "mortgage_broker"
    INVESTOR = "investor"

    @staticmethod
    def get_all() -> List[str]:
        """Get all stakeholder group identifiers."""
        return [
            StakeholderGroup.TENANT_BUYER,
            StakeholderGroup.BROKER,
            StakeholderGroup.LANDLORD,
            StakeholderGroup.PROPERTY_MANAGER,
            StakeholderGroup.APPRAISER,
            StakeholderGroup.MORTGAGE_BROKER,
            StakeholderGroup.INVESTOR,
        ]

    @staticmethod
    def get_name(stakeholder_group: str) -> str:
        """Get human-readable name for a stakeholder group."""
        mapping = {
            StakeholderGroup.TENANT_BUYER: "Tenant/Buyer",
            StakeholderGroup.BROKER: "Broker",
            StakeholderGroup.LANDLORD: "Landlord",
            StakeholderGroup.PROPERTY_MANAGER: "Property Manager",
            StakeholderGroup.APPRAISER: "Appraiser",
            StakeholderGroup.MORTGAGE_BROKER: "Mortgage Broker",
            StakeholderGroup.INVESTOR: "Investor",
        }
        return mapping.get(stakeholder_group, "Unknown")