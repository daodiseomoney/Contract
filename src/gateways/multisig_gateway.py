"""MultiSig Gateway for handling blockchain transactions"""
from typing import List, Dict
from enum import Enum
from datetime import datetime
import json
import logging
import base64
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.tx import Transaction, SigningCfg
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PublicKey
from cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 import TxBody, AuthInfo, SignDoc

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
            SignatureRole.OWNER.value: SignatureStatus.PENDING.value,
            SignatureRole.CONTRIBUTOR.value: SignatureStatus.PENDING.value,
            SignatureRole.VALIDATOR.value: SignatureStatus.PENDING.value
        }
        self.created_at = datetime.utcnow()
        self.blockchain_tx_hash = None
        self.explorer_url = None

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "signatures": self.signatures,
            "created_at": self.created_at.isoformat(),
            "blockchain_tx_hash": self.blockchain_tx_hash,
            "explorer_url": self.explorer_url,
            "status": self.get_status()
        }

    def get_status(self) -> str:
        signed_count = len([s for s in self.signatures.values() if s == SignatureStatus.SIGNED.value])
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

        # Initialize Odiseo testnet client with basic configuration
        self.network_config = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url="grpc+https://odiseo.test.rpc.nodeshub.online",
            fee_minimum_gas_price=0.01,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.client = LedgerClient(self.network_config)

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
            # Validate Keplr amino signature
            if not signature or not isinstance(signature, dict):
                self.logger.error("Invalid signature data format")
                raise ValueError("Invalid signature data format")

            signed = signature.get('signed')
            if not signed or not isinstance(signed, dict):
                self.logger.error("Invalid signed data in signature")
                raise ValueError("Invalid signed data")

            # Verify chain ID
            if signed.get('chain_id') != 'odiseotestnet_1234-1':
                self.logger.error(f"Chain ID mismatch: {signed.get('chain_id')}")
                raise ValueError("Invalid chain ID in signature")

            # Parse and verify pipe-delimited memo
            try:
                memo = signed.get('memo', '')
                # Check for JSON format (not allowed anymore)
                if memo.startswith('{') or memo.startswith('['):
                    self.logger.error("Invalid memo format: JSON object not allowed")
                    raise ValueError("Memo must be a simple pipe-delimited string")
                
                # Parse the memo into a dictionary
                memo_data = {}
                if '|' in memo:
                    parts = memo.split('|')
                    for part in parts:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            memo_data[key.strip()] = value.strip()
                
                # Check for required fields
                if not all(k in memo_data for k in ['tx', 'hash', 'role']):
                    self.logger.error(f"Missing required fields in memo: {memo}")
                    raise ValueError("Invalid memo format. Expected tx:ID|hash:HASH|role:ROLE")
                
                # Verify the values match
                if (memo_data['tx'] != transaction_id or
                    memo_data['hash'] != transaction.content_hash or
                    memo_data['role'] != role.value):  # Compare with role.value, not the Enum itself
                    self.logger.error(f"Memo data mismatch: Expected tx={transaction_id}, hash={transaction.content_hash}, role={role.value}, got {memo_data}")
                    raise ValueError("Invalid memo data")
            except Exception as e:
                self.logger.error(f"Failed to parse memo: {str(e)}")
                raise ValueError(f"Invalid memo format: {str(e)}")

            # Create transaction body
            tx_body = TxBody()
            tx_body.memo = signed.get('memo', '')

            # Process messages from signed data
            msgs = signed.get('msgs', [])
            if not msgs:
                self.logger.error("No messages found in signed data")
                raise ValueError("No messages found in signed data")

            for msg in msgs:
                if msg.get('type') != 'cosmos-sdk/MsgSend':
                    continue

                msg_value = msg.get('value', {})
                if not all(k in msg_value for k in ['from_address', 'to_address', 'amount']):
                    self.logger.error("Invalid message format")
                    raise ValueError("Invalid message format")

                tx_body.messages.extend([msg])

            # Create auth info with fee
            auth_info = AuthInfo()
            if 'fee' in signed:
                fee = signed['fee']
                for amt in fee.get('amount', []):
                    auth_info.fee.amount.append(amt)
                auth_info.fee.gas_limit = int(fee.get('gas', '100000'))

            # Create signing configuration
            signing_cfg = SigningCfg.direct(
                public_key=PublicKey(
                    key_type=signature['pub_key']['type'],
                    key=base64.b64decode(signature['pub_key']['value'])
                ),
                sequence=int(signed.get('sequence', '0')),
                account_number=int(signed.get('account_number', '0'))
            )

            # Create transaction
            tx = Transaction()
            tx.body = tx_body
            tx.auth_info = auth_info
            tx.signing_cfg = signing_cfg

            # Broadcast transaction
            self.logger.info("Broadcasting transaction to network")
            result = self.client.broadcast_tx(tx)

            if result.code != 0:
                self.logger.error(f"Broadcast failed: {result.raw_log}")
                raise ValueError(f"Transaction broadcast failed: {result.raw_log}")

            # Update transaction status
            transaction.signatures[role.value] = SignatureStatus.SIGNED.value
            transaction.update_blockchain_details(result.tx_hash)
            self.logger.info(f"Transaction broadcast successful. Hash: {result.tx_hash}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to process transaction: {str(e)}")
            raise

    def get_transaction_status(self, transaction_id: str) -> Dict:
        """Get the current status of a transaction"""
        if transaction_id not in self.pending_transactions:
            raise ValueError("Transaction not found")

        transaction = self.pending_transactions[transaction_id]
        return transaction.to_dict()

    def get_active_contracts(self) -> List[Dict]:
        """Get all active contracts/transactions"""
        return [tx.to_dict() for tx in self.pending_transactions.values()]