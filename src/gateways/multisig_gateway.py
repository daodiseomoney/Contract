from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import json

class SignatureRole(Enum):
    OWNER = "owner"
    CONTRIBUTOR = "contributor"
    VALIDATOR = "validator"

class SignatureStatus(Enum):
    PENDING = "pending"
    SIGNED = "signed"
    REJECTED = "rejected"

class MultiSigTransaction:
    def __init__(self, transaction_id: str, content_hash: str, metadata: Dict):
        self.transaction_id = transaction_id
        self.content_hash = content_hash
        self.metadata = metadata
        self.signatures = {
            SignatureRole.OWNER: SignatureStatus.PENDING,
            SignatureRole.CONTRIBUTOR: SignatureStatus.PENDING,
            SignatureRole.VALIDATOR: SignatureStatus.PENDING
        }
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "signatures": {role.value: status.value for role, status in self.signatures.items()},
            "created_at": self.created_at.isoformat()
        }

class MultiSigBlockchainGateway:
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        self.pending_transactions: Dict[str, MultiSigTransaction] = {}
        
    async def create_transaction(self, content_hash: str, metadata: Dict) -> str:
        """Create a new multi-signature transaction"""
        transaction_id = f"tx_{len(self.pending_transactions) + 1}"
        transaction = MultiSigTransaction(transaction_id, content_hash, metadata)
        self.pending_transactions[transaction_id] = transaction
        return transaction_id

    async def sign_transaction(self, transaction_id: str, role: SignatureRole, signature: str) -> bool:
        """Sign a transaction with a specific role"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")
            
        transaction = self.pending_transactions[transaction_id]
        
        # In test mode, accept any signature
        if self.test_mode:
            transaction.signatures[role] = SignatureStatus.SIGNED
            return True
            
        # In production mode, verify Kepler signature
        # TODO: Implement Kepler signature verification
        return False

    def get_transaction_status(self, transaction_id: str) -> Dict:
        """Get the current status of a transaction"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")
            
        transaction = self.pending_transactions[transaction_id]
        return transaction.to_dict()

    def is_transaction_complete(self, transaction_id: str) -> bool:
        """Check if all required signatures are present"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")
            
        transaction = self.pending_transactions[transaction_id]
        return all(status == SignatureStatus.SIGNED for status in transaction.signatures.values())

    def get_pending_transactions(self) -> List[Dict]:
        """Get all pending transactions"""
        return [tx.to_dict() for tx in self.pending_transactions.values()]
