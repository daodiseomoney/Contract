from typing import List, Dict
from enum import Enum
from datetime import datetime
import json
import logging

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
        self.blockchain_tx_hash = None
        self.explorer_url = None

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "signatures": {role.value: status.value for role, status in self.signatures.items()},
            "created_at": self.created_at.isoformat(),
            "blockchain_tx_hash": self.blockchain_tx_hash,
            "explorer_url": self.explorer_url,
            "status": self.get_status()
        }

    def get_status(self) -> str:
        signed_count = len([s for s in self.signatures.values() if s == SignatureStatus.SIGNED])
        total_count = len(self.signatures)
        if signed_count == total_count:
            return "completed"
        elif signed_count > 0:
            return "pending_signatures"
        return "active"

    def update_blockchain_details(self, tx_hash: str):
        """Update transaction with blockchain details"""
        self.blockchain_tx_hash = tx_hash
        self.explorer_url = f"https://testnet.explorer.nodeshub.online/odiseo/tx/{tx_hash}"

class MultiSigBlockchainGateway:
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        self.pending_transactions: Dict[str, MultiSigTransaction] = {}
        self.logger = logging.getLogger(__name__)

    def create_transaction(self, content_hash: str, metadata: Dict) -> str:
        """Create a new multi-signature transaction"""
        transaction_id = f"tx_{len(self.pending_transactions) + 1}"
        transaction = MultiSigTransaction(transaction_id, content_hash, metadata)
        self.pending_transactions[transaction_id] = transaction
        return transaction_id

    def sign_transaction(self, transaction_id: str, role: SignatureRole, signature: Dict) -> bool:
        """Sign a transaction with Keplr signature"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")

        transaction = self.pending_transactions[transaction_id]
        self.logger.info(f"Processing signature for transaction {transaction_id}, role: {role}")

        try:
            # Verify and process Keplr signature
            if not signature or not signature.get('pubKey') or not signature.get('signature'):
                raise ValueError("Invalid signature data")

            # Update signature status
            transaction.signatures[role] = SignatureStatus.SIGNED
            self.logger.info(f"Updated signature status for {role} to SIGNED")

            # Get transaction hash from Keplr response
            tx_hash = signature.get('tx_hash')
            if tx_hash:
                transaction.update_blockchain_details(tx_hash)
                self.logger.info(f"Updated blockchain details with hash: {tx_hash}")

            # Check if all signatures are collected
            all_signed = all(status == SignatureStatus.SIGNED for status in transaction.signatures.values())
            if all_signed:
                self.logger.info("All signatures collected, transaction complete")

            return True

        except Exception as e:
            self.logger.error(f"Failed to sign transaction: {str(e)}")
            raise Exception(f"Failed to sign transaction: {str(e)}")

    def get_transaction_status(self, transaction_id: str) -> Dict:
        """Get the current status of a transaction"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")

        transaction = self.pending_transactions[transaction_id]
        return transaction.to_dict()

    def get_active_contracts(self) -> List[Dict]:
        """Get all active contracts/transactions"""
        return [tx.to_dict() for tx in self.pending_transactions.values()]