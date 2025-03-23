from typing import Dict, Optional
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.tx import Transaction, SigningCfg
from cosmpy.aerial.tx_helpers import SubmittedTx
from cosmpy.crypto.address import Address
import json
import logging
import base64

class TransactionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Define multiple endpoints with proper protocols for fallback
        self.endpoints = [
            "rest+https://odiseo.test.api.nodeshub.online",      # REST API endpoint first
            "http+https://odiseo.test.rpc.nodeshub.online",      # HTTP endpoint as fallback
            "grpc+https://odiseo.test.rpc.nodeshub.online:443"   # gRPC as last resort
        ]

        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url=self.endpoints[0],  # Start with REST endpoint
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.logger.debug(f"Initializing TransactionService with network config: {self.network}")

        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """Initialize client with fallback support"""
        last_error = None
        for endpoint in self.endpoints:
            try:
                self.network.url = endpoint
                self.logger.info(f"Attempting to connect to endpoint: {endpoint}")

                self.client = LedgerClient(self.network)
                self.logger.info(f"Successfully connected to endpoint: {endpoint}")
                return

            except Exception as e:
                last_error = e
                self.logger.warning(f"Failed to connect to endpoint {endpoint}: {str(e)}")
                continue

        if not self.client:
            error_msg = f"Failed to connect to any available endpoints. Last error: {str(last_error)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)

    def create_sign_doc(self, sender_address: str, msg: Dict, account_data: Optional[Dict] = None) -> Dict:
        """Create a sign doc for Keplr to sign"""
        try:
            self.logger.debug(f"Creating sign doc for address: {sender_address}")
            self.logger.debug(f"Message data: {msg}")
            self.logger.debug(f"Account data: {account_data}")

            # Create simple memo format - use a string-based format instead of JSON
            tx_id = msg.get("transaction_id", "")
            role = msg.get("role", "")
            content_hash = msg.get("content_hash", "")
            # Use a simple string format instead of JSON object
            memo = f"tx:{tx_id}|role:{role}|hash:{content_hash}"
            self.logger.debug(f"Generated memo: {memo}")

            # Create sign doc for Keplr
            sign_doc = {
                "chain_id": self.network.chain_id,
                "account_number": account_data.get("account_number", "0"),
                "sequence": account_data.get("sequence", "0"),
                "fee": {
                    "amount": [{"denom": "uodis", "amount": "2500"}],
                    "gas": "100000"
                },
                "msgs": [msg],
                "memo": memo
            }

            self.logger.debug(f"Created sign doc: {sign_doc}")
            return sign_doc

        except Exception as e:
            self.logger.error(f"Failed to create sign doc: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to create sign doc: {str(e)}")

    def broadcast_transaction(self, tx_data: Dict) -> Dict:
        """Broadcast a signed transaction to the blockchain"""
        try:
            self.logger.info("Starting transaction broadcast")
            self.logger.debug(f"Transaction data: {tx_data}")

            # Validate transaction data
            if not tx_data.get('tx'):
                raise ValueError("Missing transaction data")

            tx = tx_data['tx']
            required_fields = ['msg', 'fee', 'signatures', 'memo']
            missing_fields = [field for field in required_fields if field not in tx]

            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # Create Transaction object
            transaction = Transaction()
            self.logger.debug("Creating transaction object")

            # Set messages
            self.logger.debug(f"Setting transaction messages: {tx['msg']}")
            transaction.body.messages.extend(tx['msg'])
            transaction.body.memo = tx['memo']

            # Set fee
            self.logger.debug(f"Setting transaction fee: {tx['fee']}")
            transaction.auth_info.fee.amount.extend(tx['fee']['amount'])
            transaction.auth_info.fee.gas_limit = int(tx['fee'].get('gas', '100000'))

            # Add signatures
            self.logger.debug("Adding signatures")
            for sig in tx['signatures']:
                if not sig.get('signature') or not sig.get('pub_key'):
                    raise ValueError("Invalid signature format")

                signature = base64.b64decode(sig['signature'])
                self.logger.debug(f"Adding signature (length: {len(signature)})")
                transaction.signatures.append(signature)

            # Broadcast transaction
            self.logger.info("Broadcasting transaction to network")
            result = self.client.broadcast_tx(transaction)

            if result.code != 0:
                error_msg = f"Transaction broadcast failed: {result.raw_log}"
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }

            success_result = {
                "success": True,
                "txhash": result.tx_hash,
                "height": result.height,
                "gas_used": result.gas_used,
                "code": result.code,
                "raw_log": result.raw_log
            }
            self.logger.info(f"Transaction broadcast successful: {success_result}")
            return success_result

        except ValueError as e:
            error_msg = f"Invalid transaction data: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to broadcast transaction: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)