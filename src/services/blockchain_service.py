"""
Blockchain Service for coordinating blockchain operations
Works with PingPub and MultiSig gateways
"""

import os
import json
import logging
import hashlib
import base64
import dotenv
from typing import Dict, Any, Optional, List

from src.gateways.pingpub_gateway import PingPubGateway

# Set up logging
logger = logging.getLogger(__name__)

# SECURITY: Force loading of environment variables at module initialization
# This ensures environment variables are available even if imported before app startup
dotenv.load_dotenv('.env')

class BlockchainService:
    """Service for blockchain operations including transaction coordination"""
    
    def __init__(self):
        # SECURITY: Double-check environment is loaded
        dotenv.load_dotenv('.env')
        
        logger.debug(f"PINGPUB_API_URL={os.environ.get('PINGPUB_API_URL', 'Not set')}")
        logger.debug(f"CHAIN_ID={os.environ.get('CHAIN_ID', 'Not set')}")
        
        # Initialize gateways
        try:
            self.pingpub_gateway = PingPubGateway()
        except Exception as e:
            logger.error(f"Failed to initialize PingPubGateway: {str(e)}")
            raise
        
        # Get contract address from environment (no hardcoded fallback)
        self.contract_address = os.environ.get("CONTRACT_ADDRESS")
        if not self.contract_address:
            logger.error("CONTRACT_ADDRESS environment variable is missing")
            raise ValueError("CONTRACT_ADDRESS environment variable is required")
        
        # Validator pool address for multi-sig transactions
        self.validator_pool_address = os.environ.get(
            "VALIDATOR_POOL_ADDRESS",
            "odiseo1k5vh4mzjncn4tnvan463whhrkkcsvjzgxm384q"
        )
        
        logger.info("Blockchain service initialized")
    
    def process_ifc_upload(self, file_data: bytes, user_address: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process an IFC file upload and create blockchain transaction
        
        Args:
            file_data: Binary content of the IFC file
            user_address: User's wallet address
            metadata: Additional metadata for the transaction
            
        Returns:
            dict: Transaction details including hash and prepared transaction
        """
        # Generate content hash
        content_hash = hashlib.sha256(file_data).hexdigest()
        logger.info(f"Generated content hash: {content_hash}")
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata["file_size"] = len(file_data)
        metadata["uploader"] = user_address
        metadata["content_type"] = "application/ifc"
        
        # Create transaction ID from hash
        transaction_id = f"ifc_{content_hash[:8]}"
        
        # Get account info to prepare transaction
        account_info = self.pingpub_gateway.get_account_info(user_address)
        logger.debug(f"Account info: {account_info}")
        
        # Create the transaction message
        msg, memo = self.pingpub_gateway.create_upload_message(
            from_address=user_address,
            to_address=self.contract_address,
            content_hash=content_hash,
            metadata=metadata
        )
        
        # Create complete transaction document
        transaction = {
            "transaction_id": transaction_id,
            "content_hash": content_hash,
            "user_address": user_address,
            "account_info": account_info,
            "chain_id": self.pingpub_gateway.chain_id,
            "tx_msg": msg,
            "memo": memo,
            "fee": {
                "amount": [{"denom": "uodis", "amount": "2500"}],
                "gas": "100000"
            }
        }
        
        # Prepare response with transaction data for frontend signing
        response = {
            "success": True,
            "transaction_id": transaction_id,
            "content_hash": content_hash,
            "metadata": metadata,
            "transaction": transaction,
            "sign_doc": {
                "chain_id": transaction["chain_id"],
                "account_number": account_info["account_number"],
                "sequence": account_info["sequence"],
                "fee": transaction["fee"],
                "msgs": [msg],
                "memo": memo
            }
        }
        
        logger.info(f"Prepared transaction: {transaction_id}")
        return response
    
    def broadcast_signed_transaction(self, signed_tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Broadcast a signed transaction
        
        Args:
            signed_tx: The signed transaction data from Keplr
            
        Returns:
            dict: Transaction result including hash and explorer URL
        """
        # Format the transaction for broadcasting
        broadcast_tx = self._format_for_broadcast(signed_tx)
        
        # Broadcast transaction
        broadcast_result = self.pingpub_gateway.broadcast_transaction(broadcast_tx)
        
        # Get transaction hash
        tx_hash = broadcast_result.get("txhash")
        
        # Prepare explorer URL
        explorer_url = self.pingpub_gateway.get_explorer_url(tx_hash)
        
        # Prepare response
        response = {
            "success": True,
            "transaction_hash": tx_hash,
            "height": broadcast_result.get("height"),
            "gas_used": broadcast_result.get("gas_used"),
            "explorer_url": explorer_url,
            "raw_result": broadcast_result
        }
        
        logger.info(f"Successfully broadcast transaction: {tx_hash}")
        return response
    
    def _format_for_broadcast(self, signed_tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the signed transaction for broadcasting
        
        Args:
            signed_tx: Signed transaction from Keplr
            
        Returns:
            dict: Formatted transaction for broadcasting
        """
        # Extract signature and public key
        signature = signed_tx.get("signature", {})
        pub_key = signature.get("pub_key", {})
        
        # For ProtoTx format required by ping.pub
        broadcast_tx = {
            "tx": {
                "msg": self._convert_msgs_to_proto(signed_tx.get("signed", {}).get("msgs", [])),
                "fee": signed_tx.get("signed", {}).get("fee", {}),
                "signatures": [
                    {
                        "pub_key": pub_key,
                        "signature": signature.get("signature", "")
                    }
                ],
                "memo": signed_tx.get("signed", {}).get("memo", "")
            },
            "mode": "block"  # Wait for block confirmation
        }
        
        return broadcast_tx
    
    def _convert_msgs_to_proto(self, msgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert Amino format messages to Proto format
        
        Args:
            msgs: List of Amino format messages
            
        Returns:
            list: List of Proto format messages
        """
        proto_msgs = []
        
        for msg in msgs:
            if msg.get("type") == "cosmos-sdk/MsgSend":
                # Convert to Proto format
                proto_msg = {
                    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                    "value": {
                        "fromAddress": msg.get("value", {}).get("from_address", ""),
                        "toAddress": msg.get("value", {}).get("to_address", ""),
                        "amount": msg.get("value", {}).get("amount", [])
                    }
                }
                proto_msgs.append(proto_msg)
            else:
                # Handle other message types if needed
                logger.warning(f"Unknown message type: {msg.get('type')}")
        
        return proto_msgs
    
    def verify_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Verify a transaction status
        
        Args:
            tx_hash: Transaction hash to verify
            
        Returns:
            dict: Transaction verification result
        """
        # Check transaction status
        status = self.pingpub_gateway.check_transaction_status(tx_hash)
        
        # Prepare response
        response = {
            "verified": status.get("success", False),
            "transaction_hash": tx_hash,
            "height": status.get("height"),
            "timestamp": status.get("timestamp"),
            "explorer_url": self.pingpub_gateway.get_explorer_url(tx_hash),
            "status": status
        }
        
        return response
    
    def get_validators(self) -> List[Dict[str, Any]]:
        """
        Get list of active validators
        
        Returns:
            list: List of validator information
        """
        validators = self.pingpub_gateway.get_validators()
        
        # Format validator information
        formatted_validators = []
        for validator in validators:
            formatted_validators.append({
                "address": validator.get("operator_address"),
                "name": validator.get("description", {}).get("moniker", "Unknown"),
                "status": validator.get("status", "UNKNOWN"),
                "voting_power": validator.get("voting_power", 0),
                "commission": validator.get("commission", {}).get("commission_rates", {}).get("rate", 0)
            })
        
        return formatted_validators