from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Property:
    id: int
    name: str
    address: str
    owner_id: int
    bim_file_hash: Optional[str] = None
    created_at: datetime = datetime.utcnow()

@dataclass
class TokenizedAsset:
    id: int
    property_id: int
    token_id: str
    smart_contract_address: str
    budget_splits: dict
    status: str
    created_at: datetime = datetime.utcnow()

@dataclass
class BudgetAllocation:
    id: int
    asset_id: int
    role: str
    percentage: float
    wallet_address: str
