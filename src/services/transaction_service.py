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
        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url="grpc+https://odiseo.test.rpc.nodeshub.online:443",
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.client = LedgerClient(self.network)
        self.logger = logging.getLogger(__name__)

    def create_sign_doc(self, sender_address: str, msg: Dict, account_data: Optional[Dict] = None) -> Dict:
        """Create a sign doc for Keplr to sign"""
        try:
            # Get account data if not provided
            if account_data is None:
                account = self.client.query_account(Address(sender_address))
                account_number = str(account.account_number)
                sequence = str(account.sequence)
            else:
                account_number = account_data.get("account_number", "0")
                sequence = account_data.get("sequence", "0")

            # Create simple memo format
            tx_id = msg.get("transaction_id", "")
            role = msg.get("role", "")
            memo = f"tx:{tx_id}|role:{role}"

            # Create sign doc for Keplr
            sign_doc = {
                "chain_id": self.network.chain_id,
                "account_number": account_number,
                "sequence": sequence,
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
            self.logger.error(f"Failed to create sign doc: {str(e)}")
            raise ValueError(f"Failed to create sign doc: {str(e)}")

    def broadcast_signed_tx(self, signed_tx_data: Dict) -> Dict:
        """Broadcast a signed transaction to the network"""
        try:
            self.logger.info("Broadcasting signed transaction")
            self.logger.debug(f"Signed transaction data: {signed_tx_data}")

            # Validate signed transaction data
            if not signed_tx_data.get("signed"):
                raise ValueError("Missing 'signed' field in transaction data")
            if not signed_tx_data.get("signature"):
                raise ValueError("Missing 'signature' field in transaction data")

            # Create transaction with signed data
            tx = Transaction()

            try:
                # Set transaction body
                tx.body.messages.extend(signed_tx_data["signed"]["msgs"])
                tx.body.memo = signed_tx_data["signed"].get("memo", "")

                # Set auth info with fee and signer info
                fee_amount = signed_tx_data["signed"]["fee"]["amount"]
                gas_limit = signed_tx_data["signed"]["fee"]["gas"]

                self.logger.debug(f"Setting fee amount: {fee_amount}, gas limit: {gas_limit}")
                tx.auth_info.fee.amount.extend(fee_amount)
                tx.auth_info.fee.gas_limit = int(gas_limit)

                # Add signature
                signature = base64.b64decode(signed_tx_data["signature"]["signature"])
                self.logger.debug(f"Adding signature (length: {len(signature)})")
                tx.signatures.append(signature)

            except KeyError as ke:
                self.logger.error(f"Missing required field in transaction data: {str(ke)}")
                raise ValueError(f"Invalid transaction format: missing {str(ke)}")
            except ValueError as ve:
                self.logger.error(f"Invalid value in transaction data: {str(ve)}")
                raise ValueError(f"Invalid transaction format: {str(ve)}")

            # Broadcast transaction
            self.logger.info("Broadcasting transaction to network")
            result = self.client.broadcast_tx(tx)

            if result.code != 0:
                self.logger.error(f"Transaction broadcast failed: {result.raw_log}")
                return {
                    "success": False,
                    "error": f"Transaction broadcast failed: {result.raw_log}"
                }

            success_result = {
                "success": True,
                "tx_hash": result.tx_hash,
                "height": result.height,
                "gas_used": result.gas_used
            }
            self.logger.info(f"Transaction broadcast successful: {success_result}")
            return success_result

        except Exception as e:
            self.logger.error(f"Failed to broadcast transaction: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to broadcast transaction: {str(e)}"
            }