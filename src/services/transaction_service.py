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
        
        # Add specific API and RPC URLs for direct HTTP calls
        self.api_url = "https://odiseo.test.api.nodeshub.online"
        self.rpc_url = "https://odiseo.test.rpc.nodeshub.online"

        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url=self.endpoints[0],  # Start with REST endpoint
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.logger.debug(f"Initializing TransactionService with network config: {self.network}")
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
            memo = f"tx:{tx_id}|hash:{content_hash}|role:{role}"
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
            
            # Use cosmpy's transaction class but handle it manually
            self.logger.debug("Using manual transaction broadcast approach")
            
            try:
                # Import required cosmpy components
                from cosmpy.aerial.tx import Transaction
                from cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 import TxBody, AuthInfo, SignDoc, TxRaw
                from cosmpy.protos.cosmos.tx.signing.v1beta1.signing_pb2 import SignMode
                from cosmpy.protos.cosmos.crypto.secp256k1.keys_pb2 import PubKey
                import importlib
                import google.protobuf.json_format as json_format
                
                # Create new transaction objects from scratch for better control
                tx_body = TxBody()
                auth_info = AuthInfo()
                
                # Set the memo field
                tx_body.memo = tx['memo']
                
                # Handle fee
                fee = tx['fee']
                for amount in fee.get('amount', []):
                    from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
                    coin = Coin()
                    coin.denom = amount['denom']
                    coin.amount = amount['amount']
                    auth_info.fee.amount.append(coin)
                
                auth_info.fee.gas_limit = int(fee.get('gas', '100000'))
                
                # We need to use a simpler approach - rely on the REST API directly with the original Amino format
                # rather than trying to convert to protobuf
                import requests
                import json
                
                # Prepare the transaction broadcast request in Amino JSON format
                broadcast_json = {
                    "tx": {
                        "msg": tx['msg'],
                        "fee": tx['fee'],
                        "signatures": tx['signatures'],
                        "memo": tx['memo']
                    },
                    "mode": "block"
                }
                
                self.logger.debug(f"Broadcasting Amino transaction format: {broadcast_json}")
                
                # Extract REST API endpoint from our RPC URL or use a default
                rest_api = self.api_url if hasattr(self, 'api_url') else "https://odiseo.test.api.nodeshub.online"
                broadcast_url = f"{rest_api}/cosmos/tx/v1beta1/txs"
                
                self.logger.debug(f"Broadcasting to endpoint: {broadcast_url}")
                
                # Use requests to broadcast the transaction
                response = requests.post(
                    broadcast_url,
                    json=broadcast_json,
                    headers={"Content-Type": "application/json"}
                )
                
                if not response.ok:
                    error_msg = f"Transaction broadcast failed: {response.status_code}, {response.text}"
                    self.logger.error(error_msg)
                    
                    # Try to parse the error response if possible
                    error_details = "Unknown error"
                    try:
                        error_json = response.json()
                        if isinstance(error_json, dict):
                            error_details = error_json
                    except Exception as parse_error:
                        self.logger.error(f"Error parsing response: {str(parse_error)}")
                        error_details = response.text
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": response.status_code,
                        "error_details": error_details
                    }
                
                # Parse response
                result = response.json()
                self.logger.debug(f"Broadcast response: {result}")
                
                tx_response = result.get('tx_response', {})
                if tx_response.get('code', 0) != 0:
                    error_msg = f"Transaction broadcast failed: {tx_response.get('raw_log', 'Unknown error')}"
                    self.logger.error(error_msg)
                    
                    # Log additional error details if available
                    self.logger.error(f"Transaction response details: {json.dumps(tx_response, indent=2)}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "tx_response": tx_response,
                        "error_code": tx_response.get('code'),
                        "raw_log": tx_response.get('raw_log')
                    }
                
                success_result = {
                    "success": True,
                    "txhash": tx_response.get('txhash'),
                    "height": tx_response.get('height'),
                    "gas_used": tx_response.get('gas_used'),
                    "code": tx_response.get('code', 0),
                    "raw_log": tx_response.get('raw_log', '')
                }
                self.logger.info(f"Transaction broadcast successful: {success_result}")
                return success_result
                
            except ImportError as e:
                self.logger.error(f"Import error: {str(e)}. Using fallback method...")
                # Continue with fallback approach...
            
            except Exception as e:
                self.logger.error(f"Error in transaction processing: {str(e)}", exc_info=True)
                raise ValueError(f"Transaction processing error: {str(e)}")
            
            # If we got here, use a more basic approach - simple JSON structure
            return {
                "success": False,
                "error": "Failed to broadcast transaction using the available methods"
            }

        except ValueError as e:
            error_msg = f"Invalid transaction data: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to broadcast transaction: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)