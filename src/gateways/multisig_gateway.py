from typing import List, Dict
from enum import Enum
from datetime import datetime
import json
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.tx import Transaction
from cosmpy.crypto.address import Address

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

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "signatures": {role.value: status.value for role, status in self.signatures.items()},
            "created_at": self.created_at.isoformat(),
            "blockchain_tx_hash": self.blockchain_tx_hash
        }

class MultiSigBlockchainGateway:
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        self.pending_transactions: Dict[str, MultiSigTransaction] = {}

        # Initialize Odiseo testnet client
        self.network_config = NetworkConfig(
            chain_id="odiseo_1234-1",  # Update with actual chain ID
            url="grpc+https://odiseo.test.rpc.nodeshub.online",  # Added grpc+https prefix
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.client = LedgerClient(self.network_config)

    def create_transaction(self, content_hash: str, metadata: Dict) -> str:
        """Create a new multi-signature transaction and initialize on blockchain"""
        transaction_id = f"tx_{len(self.pending_transactions) + 1}"
        transaction = MultiSigTransaction(transaction_id, content_hash, metadata)

        if not self.test_mode:
            try:
                # Create transaction
                tx = Transaction()
                tx.add_message(
                    "/cosmos.bank.v1beta1.MsgSend",
                    {
                        "from_address": self.client.address(),
                        "to_address": Address("odiseo1..."),  # Contract address
                        "amount": [{"denom": "uodis", "amount": "1"}],
                        "memo": json.dumps({
                            "transaction_id": transaction_id,
                            "content_hash": content_hash,
                            "type": "property_token"
                        })
                    }
                )

                # Sign and broadcast
                tx_result = self.client.broadcast_tx(tx)
                transaction.blockchain_tx_hash = tx_result.tx_hash
            except Exception as e:
                raise Exception(f"Failed to deploy contract: {str(e)}")

        self.pending_transactions[transaction_id] = transaction
        return transaction_id

    def sign_transaction(self, transaction_id: str, role: SignatureRole, signature: str) -> bool:
        """Sign a transaction with Kepler signature"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")

        transaction = self.pending_transactions[transaction_id]

        if self.test_mode:
            transaction.signatures[role] = SignatureStatus.SIGNED
            return True

        try:
            # Create blockchain transaction for signature
            tx = Transaction()
            tx.add_message(
                "/cosmos.bank.v1beta1.MsgSend",
                {
                    "from_address": self.client.address(),
                    "to_address": Address("odiseo1..."),  # Contract address
                    "amount": [{"denom": "uodis", "amount": "1"}],
                    "memo": json.dumps({
                        "transaction_id": transaction_id,
                        "role": role.value,
                        "signature": signature,
                        "type": "multisig_sign"
                    })
                }
            )

            # Broadcast signature transaction
            tx_result = self.client.broadcast_tx(tx)
            if tx_result.tx_hash:
                transaction.signatures[role] = SignatureStatus.SIGNED
                return True
            return False

        except Exception as e:
            raise Exception(f"Failed to sign transaction: {str(e)}")

    def get_transaction_status(self, transaction_id: str) -> Dict:
        """Get the current status of a transaction from blockchain"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")

        transaction = self.pending_transactions[transaction_id]

        if not self.test_mode and transaction.blockchain_tx_hash:
            try:
                # Query blockchain for latest status
                tx_result = self.client.query_tx(transaction.blockchain_tx_hash)
                if tx_result:
                    # Update local state based on blockchain
                    pass
            except Exception as e:
                raise Exception(f"Failed to query transaction status: {str(e)}")

        return transaction.to_dict()

    def is_transaction_complete(self, transaction_id: str) -> bool:
        """Check if all required signatures are present"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")

        transaction = self.pending_transactions[transaction_id]
        return all(status == SignatureStatus.SIGNED for status in transaction.signatures.values())

    def get_active_contracts(self) -> List[Dict]:
        """Query active property contracts"""
        try:
            query = self.client.query_bank_balance(self.client.address())
            # In real implementation, we would query contract state
            # This is simplified for demo
            return [{
                "id": query.tx_hash,
                "status": "active",
                "balance": query.balance,
                "property": "Property Token",
                "created": "2025-03-17"
            }]
        except Exception as e:
            raise Exception(f"Failed to fetch contracts: {str(e)}")