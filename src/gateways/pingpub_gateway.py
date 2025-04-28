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
import dotenv
import time
from urllib.parse import urljoin

# Set up logging
logger = logging.getLogger(__name__)

# SECURITY: Force loading of environment variables at module initialization
# This ensures environment variables are available when imported
dotenv.load_dotenv('.env')

class PingPubGateway:
    """Gateway for interacting with the Odiseo blockchain via ping.pub"""
    
    def __init__(self):
        """
        Initialize the PingPub Gateway with required environment variables
        
        Raises:
            ValueError: If required environment variables are missing or invalid
        """
        # SECURITY IMPROVEMENT: Enhanced environment variable validation
        
        # Force reload environment variables to ensure they're available
        dotenv.load_dotenv('.env')
        
        # Log environment variables for debugging
        logger.debug(f"PINGPUB_API_URL={os.environ.get('PINGPUB_API_URL', 'Not set')}")
        logger.debug(f"CHAIN_ID={os.environ.get('CHAIN_ID', 'Not set')}")
        
        # Get and validate required environment variables
        self.base_url = os.environ.get("PINGPUB_API_URL")
        if not self.base_url:
            logger.error("PINGPUB_API_URL environment variable is missing")
            raise ValueError("PINGPUB_API_URL environment variable is required")
            
        self.chain_id = os.environ.get("CHAIN_ID")
        if not self.chain_id:
            logger.error("CHAIN_ID environment variable is missing")
            raise ValueError("CHAIN_ID environment variable is required")
            
        # Security: Validate contract address
        self.contract_address = os.environ.get("CONTRACT_ADDRESS")
        if not self.contract_address:
            logger.error("CONTRACT_ADDRESS environment variable is missing")
            raise ValueError("CONTRACT_ADDRESS environment variable is required")
            
        # Security: Validate validator pool address
        self.validator_pool_address = os.environ.get("VALIDATOR_POOL_ADDRESS")
        if not self.validator_pool_address:
            logger.error("VALIDATOR_POOL_ADDRESS environment variable is missing")
            raise ValueError("VALIDATOR_POOL_ADDRESS environment variable is required")
            
        # Additional security: validate URLs
        if not self.base_url.startswith(('https://', 'http://localhost')):
            logger.warning(f"SECURITY WARNING: PINGPUB_API_URL should use HTTPS in production: {self.base_url}")
        
        # Ensure base_url ends with slash for proper URL joining
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        # Set API endpoints (don't include leading slashes)
        self.broadcast_endpoint = "broadcast"
        self.account_endpoint = "account"
        self.validators_endpoint = "validators"
        self.transaction_endpoint = "tx"
        
        # Get gas settings from environment with validation
        try:
            self.default_gas = str(int(os.environ.get("DEFAULT_GAS", "100000")))
            self.default_fee = str(int(os.environ.get("DEFAULT_FEE", "2500")))
        except ValueError:
            logger.error("Invalid gas or fee settings, must be numeric")
            raise ValueError("DEFAULT_GAS and DEFAULT_FEE must be numeric values")
            
        self.default_denom = os.environ.get("DEFAULT_DENOM", "uodis")
        if not self.default_denom:
            logger.warning("DEFAULT_DENOM is empty, using 'uodis' as fallback")
            self.default_denom = "uodis"
            
        # Get explorer URL for transaction links
        self.explorer_url = os.environ.get("EXPLORER_URL")
        if not self.explorer_url and not os.environ.get('FLASK_DEBUG'):
            logger.warning("EXPLORER_URL environment variable is missing")
        
        # Initialize session with proper timeouts
        self.session = requests.Session()
        # Set default timeout for all requests
        self.timeout = (5, 30)  # (connect_timeout, read_timeout)
        
        # Set default headers with security headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Daodiseo-RWA-Client/1.0",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        })
        
        # Test the connection to verify configuration
        try:
            self._test_connection()
            logger.info(f"PingPub Gateway successfully initialized for chain: {self.chain_id}")
            self.is_connected = True
        except Exception as e:
            logger.error(f"Failed to connect to PingPub gateway: {str(e)}")
            
            # Check if we're in development/debug mode
            if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
                # In development mode, use mock mode to allow the app to start
                logger.warning("Running in DEVELOPMENT MODE with MOCK PingPub gateway")
                self.is_connected = False
            else:
                # In production, we must have a working connection
                logger.error("Cannot start in production without PingPub connectivity")
                raise
            
    def _test_connection(self):
        """
        Test connection to PingPub gateway to verify configuration
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Try to get validator list as a simple connectivity test
            url = f"{self.base_url}{self.validators_endpoint}"
            response = self.session.get(url, timeout=(3, 10))  # Short timeout for quick feedback
            
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to PingPub gateway: {response.status_code}")
                
            logger.debug("PingPub gateway connection test successful")
            
        except Exception as e:
            logger.error(f"PingPub gateway connection test failed: {str(e)}")
            raise ConnectionError(f"Failed to connect to PingPub gateway: {str(e)}")
    
    def get_account_info(self, address):
        """
        Retrieve account information for the given address
        
        Args:
            address: The wallet address to lookup
            
        Returns:
            dict: Account information including number and sequence
        """
        # Check if running in mock mode due to connection issues
        if hasattr(self, 'is_connected') and not self.is_connected:
            logger.warning(f"Using MOCK account info for address: {address}")
            return {
                "address": address,
                "account_number": "12345",  # Mock account number for dev testing
                "sequence": "1"             # Mock sequence number for dev testing
            }
            
        try:
            endpoint = f"{self.base_url}{self.account_endpoint}/{address}"
            logger.debug(f"Requesting account info from: {endpoint}")
            
            response = self.session.get(endpoint, timeout=self.timeout)
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
            
            # If in development mode, return mock data
            if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
                logger.warning(f"Using MOCK account info for address: {address} due to error")
                return {
                    "address": address,
                    "account_number": "12345",  # Mock account number for dev testing
                    "sequence": "1"             # Mock sequence number for dev testing
                }
            else:
                raise ValueError(f"Failed to fetch account info: {str(e)}")
    
    def get_validators(self):
        """
        Retrieve list of active validators
        
        Returns:
            list: List of validator information
        """
        # Check if running in mock mode due to connection issues
        if hasattr(self, 'is_connected') and not self.is_connected:
            logger.warning("Using MOCK validators list")
            return [
                {
                    "operator_address": "odiseovaloper1gghjut3ccd8ay0zduzj64hwre2fxs9ldmqhffj",
                    "description": {"moniker": "Mock Validator 1"},
                    "status": "BOND_STATUS_BONDED",
                    "voting_power": "1000000",
                    "commission": {"commission_rates": {"rate": "0.05"}}
                },
                {
                    "operator_address": "odiseovaloper1fmprm0sjy6lz9llv7rltn0v2azzwcwzvk2lsyn",
                    "description": {"moniker": "Mock Validator 2"},
                    "status": "BOND_STATUS_BONDED",
                    "voting_power": "2000000",
                    "commission": {"commission_rates": {"rate": "0.07"}}
                }
            ]
            
        try:
            endpoint = f"{self.base_url}{self.validators_endpoint}"
            logger.debug(f"Requesting validators from: {endpoint}")
            
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Received {len(data)} validators")
            
            return data
        
        except requests.RequestException as e:
            logger.error(f"Failed to get validators: {str(e)}")
            
            # If in development mode, return mock data
            if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
                logger.warning("Using MOCK validators list due to error")
                return [
                    {
                        "operator_address": "odiseovaloper1gghjut3ccd8ay0zduzj64hwre2fxs9ldmqhffj",
                        "description": {"moniker": "Mock Validator 1"},
                        "status": "BOND_STATUS_BONDED",
                        "voting_power": "1000000",
                        "commission": {"commission_rates": {"rate": "0.05"}}
                    },
                    {
                        "operator_address": "odiseovaloper1fmprm0sjy6lz9llv7rltn0v2azzwcwzvk2lsyn",
                        "description": {"moniker": "Mock Validator 2"},
                        "status": "BOND_STATUS_BONDED",
                        "voting_power": "2000000",
                        "commission": {"commission_rates": {"rate": "0.07"}}
                    }
                ]
            else:
                raise ValueError(f"Failed to fetch validators: {str(e)}")
    
    def broadcast_transaction(self, signed_tx):
        """
        Broadcast a signed transaction to the blockchain through ping.pub
        
        Args:
            signed_tx: The signed transaction data
            
        Returns:
            dict: Transaction response data
        """
        # Check if running in mock mode due to connection issues
        if hasattr(self, 'is_connected') and not self.is_connected:
            logger.warning("Using MOCK transaction broadcast")
            # Generate random txhash for mock transactions
            mock_txhash = hashlib.sha256(str(time.time()).encode()).hexdigest()
            return {
                "height": "12345",
                "txhash": mock_txhash,
                "gas_used": "50000",
                "gas_wanted": "100000",
                "logs": [{"success": True, "log": ""}]
            }
        
        try:
            endpoint = f"{self.base_url}{self.broadcast_endpoint}"
            logger.debug(f"Broadcasting transaction to: {endpoint}")
            logger.debug(f"Transaction payload: {json.dumps(signed_tx, indent=2)}")
            
            response = self.session.post(endpoint, json=signed_tx, timeout=self.timeout)
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
                if hasattr(e, 'response') and e.response is not None:
                    error_detail = e.response.json().get("error", error_detail)
            except:
                pass
                
            # If in development mode, return mock data
            if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
                logger.warning("Using MOCK transaction broadcast due to error")
                # Generate random txhash for mock transactions
                mock_txhash = hashlib.sha256(str(time.time()).encode()).hexdigest()
                return {
                    "height": "12345",
                    "txhash": mock_txhash,
                    "gas_used": "50000",
                    "gas_wanted": "100000",
                    "logs": [{"success": True, "log": ""}]
                }
            else:
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
        # Check if running in mock mode due to connection issues
        if hasattr(self, 'is_connected') and not self.is_connected:
            logger.warning(f"Using MOCK transaction status for hash: {tx_hash}")
            return {
                "hash": tx_hash,
                "success": True,
                "height": "123456",
                "gas_used": "50000",
                "gas_wanted": "100000",
                "timestamp": "2025-04-28T12:34:56Z",
                "error": None
            }
            
        try:
            endpoint = f"{self.base_url}tx/{tx_hash}"
            logger.debug(f"Checking transaction status from: {endpoint}")
            
            response = self.session.get(endpoint, timeout=self.timeout)
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
            
            # If in development mode, return mock data
            if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
                logger.warning(f"Using MOCK transaction status for hash: {tx_hash} due to error")
                return {
                    "hash": tx_hash,
                    "success": True,
                    "height": "123456",
                    "gas_used": "50000",
                    "gas_wanted": "100000",
                    "timestamp": "2025-04-28T12:34:56Z",
                    "error": None
                }
            else:
                raise ValueError(f"Failed to check transaction status: {str(e)}")
    
    def get_explorer_url(self, tx_hash):
        """
        Get the explorer URL for a transaction
        
        Args:
            tx_hash: The transaction hash
            
        Returns:
            str: The URL to the transaction in the explorer
        """
        # Get explorer URL from environment or compute it based on chain ID
        explorer_base = os.environ.get("EXPLORER_URL")
        
        if explorer_base:
            # Use configured explorer URL
            return f"{explorer_base.rstrip('/')}/tx/{tx_hash}"
        else:
            # Derive explorer URL from chain ID as fallback (this is less secure)
            if self.chain_id and "testnet" in self.chain_id.lower():
                logger.warning("Using testnet explorer URL derived from chain ID")
                return f"https://testnet.explorer.nodeshub.online/odiseo/tx/{tx_hash}"
            else:
                # Mainnet URL should be configured explicitly
                logger.error("EXPLORER_URL environment variable is missing for mainnet")
                return f"https://explorer.nodeshub.online/odiseo/tx/{tx_hash}"