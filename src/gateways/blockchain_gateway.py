from typing import List, Dict
import json
import os
from datetime import datetime


class MockBlockchainGateway:
    def __init__(self):
        self.contracts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "contracts.json")
        self._load_contracts()

    def _load_contracts(self):
        if os.path.exists(self.contracts_file):
            with open(self.contracts_file, "r") as f:
                self.contracts = json.load(f)
        else:
            self.contracts = []
            self._save_contracts()

    def _save_contracts(self):
        with open(self.contracts_file, "w") as f:
            json.dump(self.contracts, f)

    async def deploy_contract(self, bim_hash: str, budget_splits: Dict) -> str:
        """Mock contract deployment by storing data locally"""
        contract = {
            "id": len(self.contracts) + 1,
            "bim_hash": bim_hash,
            "budget_splits": budget_splits,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        self.contracts.append(contract)
        self._save_contracts()
        return f"mock_contract_{contract['id']}"

    def get_active_contracts(self) -> List[Dict]:
        """Return all stored contracts"""
        return [c for c in self.contracts if c["status"] == "active"]
