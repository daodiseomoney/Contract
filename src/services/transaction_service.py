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
            "rest+https://testnet-api.daodiseo.chaintools.tech",  # REST API endpoint first
            "http+https://testnet-rpc.daodiseo.chaintools.tech",  # HTTP endpoint as fallback
            "grpc+https://testnet-rpc.daodiseo.chaintools.tech:443",  # gRPC as last resort
        ]

        # Add specific API and RPC URLs for direct HTTP calls
        self.api_url = "https://testnet-api.daodiseo.chaintools.tech"
        self.rpc_url = "https://testnet-rpc.daodiseo.chaintools.tech"

        self.network = NetworkConfig(
            chain_id="ithaca-1",
            url=self.endpoints[0],  # Start with REST endpoint
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis",
        )
        self.logger.debug(
            f"Initializing TransactionService with network config: {self.network}"
        )
        self.logger.debug(f"Using API URL: {self.api_url}")
        self.logger.debug(f"Using RPC URL: {self.rpc_url}")

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
                self.logger.warning(
                    f"Failed to connect to endpoint {endpoint}: {str(e)}"
                )
                continue

        if not self.client:
            error_msg = f"Failed to connect to any available endpoints. Last error: {str(last_error)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)

    def create_sign_doc(
        self, sender_address: str, msg: Dict, account_data: Optional[Dict] = None
    ) -> Dict:
        """Create a sign doc for Keplr to sign"""
        try:
            self.logger.debug(f"Creating sign doc for address: {sender_address}")
            self.logger.debug(f"Message data: {msg}")
            self.logger.debug(f"Account data: {account_data}")

            # If account_data is not provided, fetch it from the chain
            if not account_data:
                try:
                    from cosmpy.crypto.address import Address

                    addr = Address(sender_address)
                    self.logger.debug(
                        f"Fetching account data for address: {sender_address}"
                    )
                    account = self.client.query_account(addr)

                    # Extract account data
                    if hasattr(account, "sequence"):
                        account_data = {
                            "account_number": str(
                                getattr(account, "account_number", "0")
                            ),
                            "sequence": str(account.sequence),
                            "address": sender_address,
                        }
                    elif hasattr(account, "base_vesting_account"):
                        base_account = account.base_vesting_account.base_account
                        account_data = {
                            "account_number": str(
                                getattr(base_account, "account_number", "0")
                            ),
                            "sequence": str(getattr(base_account, "sequence", "0")),
                            "address": sender_address,
                        }
                    else:
                        # Default values if structure is unknown
                        account_data = {
                            "account_number": "0",
                            "sequence": "0",
                            "address": sender_address,
                        }
                    self.logger.debug(f"Fetched account data: {account_data}")
                except Exception as account_error:
                    self.logger.error(
                        f"Error fetching account data: {str(account_error)}"
                    )
                    # Fallback to provided data or defaults
                    account_data = account_data or {
                        "account_number": "0",
                        "sequence": "0",
                        "address": sender_address,
                    }

            # Create simple memo format using a string-based format instead of JSON
            tx_id = msg.get("transaction_id", "")
            role = msg.get("role", "")
            content_hash = msg.get("content_hash", "")
            # Use a simple string format instead of JSON object
            memo = f"tx:{tx_id}|hash:{content_hash}|role:{role}"
            self.logger.debug(f"Generated memo: {memo}")

            # Create sign doc for Keplr with explicit type conversions to strings
            sign_doc = {
                "chain_id": self.network.chain_id,
                "account_number": str(account_data.get("account_number", "0")),
                "sequence": str(account_data.get("sequence", "0")),
                "fee": {
                    "amount": [{"denom": "uodis", "amount": "2500"}],
                    "gas": "100000",
                },
                "msgs": [msg],
                "memo": memo,
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
            if not tx_data.get("tx"):
                raise ValueError("Missing transaction data")

            tx = tx_data["tx"]
            required_fields = ["msg", "fee", "signatures", "memo"]
            missing_fields = [field for field in required_fields if field not in tx]

            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # Validate signatures
            if not tx["signatures"] or not isinstance(tx["signatures"], list):
                raise ValueError("Missing or invalid signatures format")

            for signature in tx["signatures"]:
                if "pub_key" not in signature or "signature" not in signature:
                    raise ValueError("Missing public key or signature in signatures")

                # Ensure pub_key has the correct format
                pub_key = signature["pub_key"]
                if "type" not in pub_key or "value" not in pub_key:
                    # Try to fix common encoding issues
                    if isinstance(pub_key, dict) and "key" in pub_key:
                        # Format it according to the Amino spec
                        signature["pub_key"] = {
                            "type": "tendermint/PubKeySecp256k1",
                            "value": pub_key["key"],
                        }
                        self.logger.debug(
                            f"Fixed public key format: {signature['pub_key']}"
                        )

            # Check and adapt message format if needed
            msgs = tx["msg"]
            self.logger.debug(f"Processing messages: {msgs}")
            adapted_msgs = []

            for msg in msgs:
                # Log detailed message structure for debugging
                self.logger.debug(f"Processing message: {msg}")

                if not isinstance(msg, dict):
                    error_msg = (
                        f"Message must be a dictionary object, got {type(msg)}: {msg}"
                    )
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                # Handle Proto format (typeUrl)
                if "typeUrl" in msg:
                    self.logger.debug(
                        f"Found Proto format message with typeUrl: {msg['typeUrl']}"
                    )
                    # Map from Proto typeUrl back to Amino for blockchain
                    type_mapping = {
                        "/cosmos.bank.v1beta1.MsgSend": "cosmos-sdk/MsgSend",
                        # Add more mappings as needed
                    }

                    # Convert back to Amino if blockchain requires it
                    amino_type = type_mapping.get(msg["typeUrl"])
                    if amino_type:
                        adapted_msg = {"type": amino_type, "value": msg["value"]}
                        self.logger.debug(f"Converted Proto to Amino: {adapted_msg}")
                        adapted_msgs.append(adapted_msg)
                    else:
                        self.logger.warning(
                            f"Unknown Proto typeUrl: {msg['typeUrl']}, using as-is"
                        )
                        adapted_msgs.append(msg)

                # Handle Amino format (type, value)
                elif "type" in msg and "value" in msg:
                    self.logger.debug(
                        f"Found Amino format message with type: {msg['type']}"
                    )
                    adapted_msgs.append(msg)

                # Handle MsgSend format coming from Keplr wallet
                elif msg.get("type") == "cosmos-sdk/MsgSend":
                    # If it has a type but the value is missing or not a dictionary
                    # we need to reconstruct the message
                    self.logger.debug(
                        f"Found MsgSend message without proper value structure"
                    )

                    # Try to extract the necessary fields for a MsgSend message
                    value = {}
                    if "from_address" in msg:
                        value["from_address"] = msg["from_address"]
                    if "to_address" in msg:
                        value["to_address"] = msg["to_address"]
                    if "amount" in msg:
                        value["amount"] = msg["amount"]

                    if (
                        "from_address" in value
                        and "to_address" in value
                        and "amount" in value
                    ):
                        adapted_msg = {"type": "cosmos-sdk/MsgSend", "value": value}
                        self.logger.debug(f"Reconstructed message: {adapted_msg}")
                        adapted_msgs.append(adapted_msg)
                    else:
                        error_msg = (
                            f"Missing required fields for MsgSend message: {msg}"
                        )
                        self.logger.error(error_msg)
                        raise ValueError(error_msg)

                else:
                    # Try to infer the structure based on known fields
                    self.logger.debug(
                        f"Attempting to infer message structure from: {msg}"
                    )

                    # Check if it has fields common to a send transaction
                    if (
                        "from_address" in msg
                        and "to_address" in msg
                        and "amount" in msg
                    ):
                        # Looks like a MsgSend message
                        adapted_msg = {
                            "type": "cosmos-sdk/MsgSend",
                            "value": {
                                "from_address": msg["from_address"],
                                "to_address": msg["to_address"],
                                "amount": msg["amount"],
                            },
                        }
                        self.logger.debug(f"Inferred MsgSend message: {adapted_msg}")
                        adapted_msgs.append(adapted_msg)
                    else:
                        error_msg = f"Unsupported message format: {msg}"
                        self.logger.error(error_msg)
                        raise ValueError(error_msg)

            # Update messages in the transaction
            tx["msg"] = adapted_msgs
            self.logger.debug(f"Adapted messages for broadcast: {adapted_msgs}")

            # Use direct REST API approach for transaction broadcast
            self.logger.debug("Using direct REST API transaction broadcast approach")

            try:
                import requests
                import json

                # Ensure consistent data types for all fields
                # Convert all numeric values to strings
                for msg in tx["msg"]:
                    if "value" in msg and "amount" in msg["value"]:
                        for amount_item in msg["value"]["amount"]:
                            if "amount" in amount_item:
                                amount_item["amount"] = str(amount_item["amount"])

                # Ensure fee amount is string
                if "fee" in tx and "amount" in tx["fee"]:
                    for amount_item in tx["fee"]["amount"]:
                        if "amount" in amount_item:
                            amount_item["amount"] = str(amount_item["amount"])

                # Ensure gas is string
                if "fee" in tx and "gas" in tx["fee"]:
                    tx["fee"]["gas"] = str(tx["fee"]["gas"])

                # Prepare the transaction broadcast request in Amino JSON format
                broadcast_json = {
                    "tx": tx,
                    "mode": "block",  # Use "block" to wait for confirmation
                }

                self.logger.debug(
                    f"Broadcasting transaction: {json.dumps(broadcast_json, indent=2)}"
                )

                # Get the proper REST API endpoint
                rest_api = (
                    self.api_url
                    if hasattr(self, "api_url")
                    else "https://odiseo.test.api.nodeshub.online"
                )
                broadcast_url = f"{rest_api}/cosmos/tx/v1beta1/txs"

                self.logger.debug(f"Broadcasting to endpoint: {broadcast_url}")

                # Use requests to broadcast the transaction
                response = requests.post(
                    broadcast_url,
                    json=broadcast_json,
                    headers={"Content-Type": "application/json"},
                )

                # Log complete response for debugging
                self.logger.debug(f"Response status: {response.status_code}")
                self.logger.debug(f"Response headers: {response.headers}")

                try:
                    response_text = response.text
                    self.logger.debug(f"Response body: {response_text}")
                except Exception as e:
                    self.logger.error(f"Error reading response text: {str(e)}")

                if not response.ok:
                    error_msg = f"Transaction broadcast failed: {response.status_code}"
                    self.logger.error(error_msg)

                    # Try to parse the error response if possible
                    error_details = "Unknown error"
                    try:
                        error_json = response.json()
                        if isinstance(error_json, dict):
                            error_details = error_json
                            # Log the detailed error structure
                            self.logger.error(
                                f"Error details: {json.dumps(error_json, indent=2)}"
                            )
                    except Exception as parse_error:
                        self.logger.error(f"Error parsing response: {str(parse_error)}")
                        error_details = response.text

                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code,
                        "error_details": error_details,
                    }

                # Parse response
                result = response.json()
                self.logger.debug(f"Broadcast response: {json.dumps(result, indent=2)}")

                tx_response = result.get("tx_response", {})
                if tx_response.get("code", 0) != 0:
                    error_msg = f"Transaction broadcast failed: {tx_response.get('raw_log', 'Unknown error')}"
                    self.logger.error(error_msg)

                    # Log additional error details if available
                    self.logger.error(
                        f"Transaction response details: {json.dumps(tx_response, indent=2)}"
                    )

                    return {
                        "success": False,
                        "error": error_msg,
                        "tx_response": tx_response,
                        "error_code": tx_response.get("code"),
                        "raw_log": tx_response.get("raw_log"),
                    }

                success_result = {
                    "success": True,
                    "txhash": tx_response.get("txhash"),
                    "height": tx_response.get("height"),
                    "gas_used": tx_response.get("gas_used"),
                    "code": tx_response.get("code", 0),
                    "raw_log": tx_response.get("raw_log", ""),
                }
                self.logger.info(f"Transaction broadcast successful: {success_result}")
                return success_result

            except Exception as e:
                self.logger.error(
                    f"Error in transaction processing: {str(e)}", exc_info=True
                )
                raise ValueError(f"Transaction processing error: {str(e)}")

        except ValueError as e:
            error_msg = f"Invalid transaction data: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to broadcast transaction: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)
