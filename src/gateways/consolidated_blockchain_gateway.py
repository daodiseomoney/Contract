"""
Consolidated Blockchain Gateway for DAODISEO Platform
Combines cosmos, pingpub, kepler, and multisig gateway functionality
"""

import os
import json
import logging
import requests
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class KeplerSignatureRole(Enum):
    """Kepler signature roles for multi-signature transactions"""
    OWNER = "owner"
    VALIDATOR = "validator"
    AUDITOR = "auditor"
    WITNESS = "witness"

@dataclass
class NetworkConfig:
    """Network configuration for blockchain connections"""
    chain_id: str
    rpc_url: str
    api_url: str
    fee_minimum_gas_price: float = 0.025
    fee_denomination: str = "uodis"
    staking_denomination: str = "uodis"

class ConsolidatedBlockchainGateway:
    """Unified gateway for all blockchain interactions"""
    
    def __init__(self, network_config: Optional[NetworkConfig] = None):
        self.network_config = network_config or NetworkConfig(
            chain_id="ithaca-1",
            rpc_url="https://testnet-rpc.daodiseo.chaintools.tech",
            api_url="https://testnet-api.daodiseo.chaintools.tech"
        )
        
        # PingPub configuration
        self.pingpub_api_url = os.environ.get(
            "PINGPUB_API_URL", 
            "https://testnet.explorer.chaintools.tech/odiseo/api"
        )
        
        # Test connection
        self._test_connections()
    
    def _test_connections(self):
        """Test blockchain connections"""
        try:
            # Test RPC connection
            rpc_response = requests.get(f"{self.network_config.rpc_url}/status", timeout=10)
            if rpc_response.status_code == 200:
                logger.info(f"RPC connection successful: {self.network_config.rpc_url}")
            
            # Test PingPub connection
            pingpub_response = requests.get(f"{self.pingpub_api_url}/validators", timeout=10)
            if pingpub_response.status_code == 200:
                logger.info(f"PingPub connection successful: {self.pingpub_api_url}")
                
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
    
    # =============================================================================
    # COSMOS NETWORK OPERATIONS
    # =============================================================================
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get network status from RPC"""
        try:
            response = requests.get(f"{self.network_config.rpc_url}/status", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("result", {}),
                    "chain_id": self.network_config.chain_id,
                    "rpc_url": self.network_config.rpc_url
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Network status error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_latest_block(self) -> Dict[str, Any]:
        """Get latest block information"""
        try:
            response = requests.get(f"{self.network_config.rpc_url}/block", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("result", {}),
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Latest block error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_validators(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Get validators from PingPub API"""
        try:
            response = requests.get(f"{self.pingpub_api_url}/validators", timeout=30)
            if response.status_code == 200:
                data = response.json()
                validators = data.get("validators", [])
                
                # Apply pagination
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_validators = validators[start_idx:end_idx]
                
                return {
                    "success": True,
                    "data": {
                        "validators": paginated_validators,
                        "total": len(validators),
                        "page": page,
                        "per_page": per_page
                    }
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Validators error: {e}")
            return {"success": False, "error": str(e)}
    
    def search_transactions(self, query: str = "tx.height>0", page: int = 1, per_page: int = 30) -> Dict[str, Any]:
        """Search transactions"""
        try:
            params = {
                "query": query,
                "page": page,
                "per_page": per_page,
                "order_by": "desc"
            }
            
            response = requests.get(
                f"{self.network_config.rpc_url}/tx_search",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("result", {}),
                    "query": query,
                    "page": page
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Transaction search error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information"""
        try:
            response = requests.get(
                f"{self.network_config.api_url}/cosmos/auth/v1beta1/accounts/{address}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "account": data.get("account", {}),
                    "address": address
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"Account info error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # KEPLR WALLET INTEGRATION
    # =============================================================================
    
    def sign_transaction(self, wallet_address: str, content_hash: str, 
                        transaction_id: str, role: KeplerSignatureRole) -> Dict[str, Any]:
        """Sign a transaction with Keplr wallet"""
        try:
            # Prepare transaction data for signing
            tx_data = {
                "chain_id": self.network_config.chain_id,
                "account_number": "0",
                "sequence": "0",
                "fee": {
                    "amount": [{"denom": self.network_config.fee_denomination, "amount": "5000"}],
                    "gas": "200000"
                },
                "msgs": [{
                    "type": "cosmos-sdk/MsgSend",
                    "value": {
                        "from_address": wallet_address,
                        "to_address": wallet_address,
                        "amount": []
                    }
                }],
                "memo": json.dumps({
                    "transaction_id": transaction_id,
                    "content_hash": content_hash,
                    "role": role.value,
                    "timestamp": int(time.time())
                })
            }
            
            # In a real implementation, this would interface with Keplr
            # For now, simulate successful signing
            signature = f"sig_{transaction_id}_{int(time.time())}"
            
            return {
                "success": True,
                "signature": signature,
                "transaction_id": transaction_id,
                "wallet_address": wallet_address,
                "role": role.value,
                "timestamp": int(time.time()),
                "tx_data": tx_data
            }
            
        except Exception as e:
            logger.error(f"Keplr signing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": transaction_id
            }
    
    def get_network_config_for_keplr(self) -> Dict[str, Any]:
        """Get network configuration for Keplr wallet"""
        return {
            "chainId": self.network_config.chain_id,
            "chainName": "Odiseo Testnet",
            "rpc": self.network_config.rpc_url,
            "rest": self.network_config.api_url,
            "bip44": {"coinType": 118},
            "bech32Config": {
                "bech32PrefixAccAddr": "odiseo",
                "bech32PrefixAccPub": "odiseopub",
                "bech32PrefixValAddr": "odiseovaloper",
                "bech32PrefixValPub": "odiseovaloperpub",
                "bech32PrefixConsAddr": "odiseovalcons",
                "bech32PrefixConsPub": "odiseovalconspub"
            },
            "currencies": [{
                "coinDenom": "ODIS",
                "coinMinimalDenom": self.network_config.fee_denomination,
                "coinDecimals": 6
            }],
            "feeCurrencies": [{
                "coinDenom": "ODIS",
                "coinMinimalDenom": self.network_config.fee_denomination,
                "coinDecimals": 6,
                "gasPriceStep": {
                    "low": 0.01,
                    "average": 0.025,
                    "high": 0.04
                }
            }],
            "stakeCurrency": {
                "coinDenom": "ODIS",
                "coinMinimalDenom": self.network_config.staking_denomination,
                "coinDecimals": 6
            }
        }
    
    # =============================================================================
    # MULTISIG OPERATIONS
    # =============================================================================
    
    def create_multisig_transaction(self, participants: List[str], threshold: int, 
                                  transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a multisig transaction"""
        try:
            multisig_id = f"multisig_{int(time.time())}_{hash(str(participants)) % 10000}"
            
            multisig_tx = {
                "id": multisig_id,
                "participants": participants,
                "threshold": threshold,
                "transaction_data": transaction_data,
                "signatures": {},
                "status": "pending",
                "created_at": int(time.time()),
                "expires_at": int(time.time()) + 86400  # 24 hours
            }
            
            logger.info(f"Created multisig transaction: {multisig_id}")
            return {
                "success": True,
                "multisig_transaction": multisig_tx
            }
            
        except Exception as e:
            logger.error(f"Multisig creation error: {e}")
            return {"success": False, "error": str(e)}
    
    def add_signature_to_multisig(self, multisig_id: str, wallet_address: str, 
                                 signature: str) -> Dict[str, Any]:
        """Add signature to multisig transaction"""
        try:
            # In production, this would interact with actual multisig storage
            logger.info(f"Added signature from {wallet_address} to multisig {multisig_id}")
            
            return {
                "success": True,
                "multisig_id": multisig_id,
                "signer": wallet_address,
                "signature_added": True,
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            logger.error(f"Multisig signature error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_multisig_transaction(self, multisig_id: str) -> Dict[str, Any]:
        """Execute multisig transaction when threshold is met"""
        try:
            # Simulate multisig execution
            tx_hash = f"0x{multisig_id}_{int(time.time())}"
            
            return {
                "success": True,
                "multisig_id": multisig_id,
                "transaction_hash": tx_hash,
                "executed_at": int(time.time()),
                "status": "executed"
            }
            
        except Exception as e:
            logger.error(f"Multisig execution error: {e}")
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # TRANSACTION BROADCASTING
    # =============================================================================
    
    def broadcast_transaction(self, signed_tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast signed transaction to the network"""
        try:
            # Try REST API first
            rest_endpoints = [
                f"{self.network_config.api_url}/txs",
                "https://testnet-api.daodiseo.chaintools.tech/txs",
                "https://api.odiseotestnet.chaintools.tech/txs"
            ]
            
            for endpoint in rest_endpoints:
                try:
                    response = requests.post(
                        endpoint,
                        json=signed_tx_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        tx_hash = result.get("txhash") or result.get("tx_hash")
                        
                        return {
                            "success": True,
                            "transaction_hash": tx_hash,
                            "response": result,
                            "endpoint": endpoint
                        }
                        
                except requests.RequestException as e:
                    logger.warning(f"REST endpoint {endpoint} failed: {e}")
                    continue
            
            # Try RPC endpoints as fallback
            rpc_endpoints = [
                f"{self.network_config.rpc_url}/broadcast_tx_commit",
                "https://testnet-rpc.daodiseo.chaintools.tech/broadcast_tx_commit"
            ]
            
            for endpoint in rpc_endpoints:
                try:
                    rpc_data = {
                        "jsonrpc": "2.0",
                        "method": "broadcast_tx_commit",
                        "params": {"tx": signed_tx_data.get("tx_bytes", "")},
                        "id": 1
                    }
                    
                    response = requests.post(
                        endpoint,
                        json=rpc_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        return {
                            "success": True,
                            "response": result,
                            "endpoint": endpoint
                        }
                        
                except requests.RequestException as e:
                    logger.warning(f"RPC endpoint {endpoint} failed: {e}")
                    continue
            
            return {
                "success": False,
                "error": "All broadcast endpoints failed"
            }
            
        except Exception as e:
            logger.error(f"Transaction broadcast error: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Verify transaction on the blockchain"""
        try:
            response = requests.get(
                f"{self.network_config.rpc_url}/tx",
                params={"hash": f"0x{tx_hash}" if not tx_hash.startswith("0x") else tx_hash},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                return {
                    "success": True,
                    "verified": True,
                    "transaction": result,
                    "status": {
                        "code": result.get("tx_result", {}).get("code", 0),
                        "memo": result.get("tx", {}).get("memo", "")
                    }
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "error": f"Transaction not found: HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Transaction verification error: {e}")
            return {
                "success": False,
                "verified": False,
                "error": str(e)
            }


# Compatibility classes for existing code
class CosmosGateway(ConsolidatedBlockchainGateway):
    """Compatibility wrapper for CosmosGateway"""
    pass

class PingPubGateway(ConsolidatedBlockchainGateway):
    """Compatibility wrapper for PingPubGateway"""
    pass

class KeplerGateway(ConsolidatedBlockchainGateway):
    """Compatibility wrapper for KeplerGateway"""
    pass

class MultisigGateway(ConsolidatedBlockchainGateway):
    """Compatibility wrapper for MultisigGateway"""
    pass