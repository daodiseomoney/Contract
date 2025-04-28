"""
PingPub Gateway for Odiseo blockchain integration
Handles the connection to ping.pub validators and blockchain
"""

import os
import json
import base64
import hashlib
import logging
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class PingPubGateway:
    """Gateway for interacting with the Odiseo blockchain via ping.pub"""
    
    def __init__(self):
        # PingPub API endpoint for Odiseo testnet
        self.base_url = os.environ.get("PINGPUB_API_URL", "https://pingpub-testnet.daodiseo.com/api/")
        self.chain_id = os.environ.get("CHAIN_ID", "odiseotestnet_1234-1")
        self.broadcast_endpoint = "broadcast"
        self.account_endpoint = "account"
        self.validators_endpoint = "validators"
        
        # Default gas settings
        self.default_gas = "100000"
        self.default_fee = "2500"
        self.default_denom = "uodis"
        
        # Initialize session
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Daodiseo-RWA-Client/1.0"
        })
        
        logger.info(f"PingPub Gateway initialized for chain: {self.chain_id}")
    
    def get_account_info(self, address):
        """
        Retrieve account information for the given address
        
        Args:
            address: The wallet address to lookup
            
        Returns:
            dict: Account information including number and sequence
        """
        try:
            endpoint = urljoin(self.base_url, f"{self.account_endpoint}/{address}")
            logger.debug(f"Requesting account info from: {endpoint}")
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Account data received: {json.dumps(data, indent=2)}")
            
            # Extract account_number and sequence, defaulting to 0 if not found
            account_number = str(data.get("account_number", "0"))
            sequence = str(data.get("sequence", "0"))
            
            return {
                "address": address,
                "account_number": account_number,
                "sequence": sequence
            }
        
        except requests.RequestException as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise ValueError(f"Failed to fetch account info: {str(e)}")
    
    def get_validators(self):
        """
        Retrieve list of active validators
        
        Returns:
            list: List of validator information
        """
        try:
            endpoint = urljoin(self.base_url, self.validators_endpoint)
            logger.debug(f"Requesting validators from: {endpoint}")
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Received {len(data)} validators")
            
            return data
        
        except requests.RequestException as e:
            logger.error(f"Failed to get validators: {str(e)}")
            raise ValueError(f"Failed to fetch validators: {str(e)}")
    
    def broadcast_transaction(self, signed_tx):
        """
        Broadcast a signed transaction to the blockchain through ping.pub
        
        Args:
            signed_tx: The signed transaction data
            
        Returns:
            dict: Transaction response data
        """
        try:
            endpoint = urljoin(self.base_url, self.broadcast_endpoint)
            logger.debug(f"Broadcasting transaction to: {endpoint}")
            logger.debug(f"Transaction payload: {json.dumps(signed_tx, indent=2)}")
            
            response = self.session.post(endpoint, json=signed_tx)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Transaction broadcast successful. Hash: {data.get('txhash')}")
            logger.debug(f"Full response: {json.dumps(data, indent=2)}")
            
            return data
        
        except requests.RequestException as e:
            logger.error(f"Failed to broadcast transaction: {str(e)}")
            
            # Try to get error details from response
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("error", error_detail)
            except:
                pass
                
            raise ValueError(f"Failed to broadcast transaction: {error_detail}")
    
    def create_upload_message(self, from_address, to_address, content_hash, metadata=None):
        """
        Create a blockchain message for uploading an IFC file hash
        
        Args:
            from_address: The sender's wallet address
            to_address: The recipient's wallet address (usually the contract)
            content_hash: The hash of the IFC file content
            metadata: Additional metadata for the transaction
            
        Returns:
            dict: The formatted message
        """
        # Create transaction metadata
        memo_data = {
            "hash": content_hash,
            "type": "ifc-upload",
            "metadata": metadata or {}
        }
        
        # Convert to JSON string for memo
        memo = json.dumps(memo_data)
        
        # Create the message
        msg = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": from_address,
                "to_address": to_address,
                "amount": [{"denom": self.default_denom, "amount": "1000"}]  # Minimal transfer
            }
        }
        
        return msg, memo
    
    def verify_content_hash(self, file_content, claimed_hash):
        """
        Verify that the hash of the content matches the claimed hash
        
        Args:
            file_content: The raw file content (bytes)
            claimed_hash: The hash value to verify against
            
        Returns:
            bool: True if the hash matches, False otherwise
        """
        if not file_content:
            return False
            
        # Calculate SHA256 hash of the content
        calculated_hash = hashlib.sha256(file_content).hexdigest()
        
        # Compare with claimed hash
        return calculated_hash == claimed_hash
    
    def check_transaction_status(self, tx_hash):
        """
        Check the status of a transaction
        
        Args:
            tx_hash: The transaction hash to check
            
        Returns:
            dict: Transaction status information
        """
        try:
            endpoint = urljoin(self.base_url, f"tx/{tx_hash}")
            logger.debug(f"Checking transaction status from: {endpoint}")
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Transaction status: {json.dumps(data, indent=2)}")
            
            # Check if the transaction was successful
            code = data.get("code", 0)
            if code != 0:
                logger.warning(f"Transaction failed with code {code}: {data.get('raw_log')}")
                
            return {
                "hash": tx_hash,
                "success": code == 0,
                "height": data.get("height"),
                "gas_used": data.get("gas_used"),
                "gas_wanted": data.get("gas_wanted"),
                "timestamp": data.get("timestamp"),
                "error": data.get("raw_log") if code != 0 else None
            }
        
        except requests.RequestException as e:
            logger.error(f"Failed to check transaction status: {str(e)}")
            raise ValueError(f"Failed to check transaction status: {str(e)}")
    
    def get_explorer_url(self, tx_hash):
        """
        Get the explorer URL for a transaction
        
        Args:
            tx_hash: The transaction hash
            
        Returns:
            str: The URL to the transaction in the explorer
        """
        # Use the testnet explorer URL
        return f"https://testnet.explorer.nodeshub.online/odiseo/tx/{tx_hash}"