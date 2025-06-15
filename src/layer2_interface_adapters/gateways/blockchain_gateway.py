"""
Blockchain Gateway - Clean Architecture Layer 2
Gateway interface and implementation for blockchain services (Cosmos/Odiseo)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
import json


class BlockchainGatewayInterface(ABC):
    """Abstract interface for blockchain gateway"""
    
    @abstractmethod
    def get_network_health(self) -> Dict[str, Any]:
        """Get network health status"""
        pass
    
    @abstractmethod
    def get_token_price(self) -> Dict[str, Any]:
        """Get ODIS token price data"""
        pass
    
    @abstractmethod
    def get_validators(self) -> Dict[str, Any]:
        """Get validator information"""
        pass


class BlockchainGateway(BlockchainGatewayInterface):
    """Implementation of blockchain gateway for Odiseo network"""
    
    def __init__(self):
        # Odiseo testnet endpoints
        self.rpc_endpoint = "https://testnet-rpc.odiseo.chain.tools"
        self.api_endpoint = "https://testnet-api.odiseo.chain.tools"
        self.timeout = 10
    
    def get_network_health(self) -> Dict[str, Any]:
        """
        Get network health status from Odiseo RPC
        
        Returns:
            Network health data including block height, validator count, etc.
        """
        try:
            # Get status from RPC endpoint
            response = requests.get(
                f"{self.rpc_endpoint}/status",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            status_data = response.json()
            
            # Extract relevant data
            result = status_data.get('result', {})
            sync_info = result.get('sync_info', {})
            validator_info = result.get('validator_info', {})
            
            latest_block_height = int(sync_info.get('latest_block_height', 0))
            catching_up = sync_info.get('catching_up', True)
            
            return {
                "success": True,
                "network_healthy": not catching_up and latest_block_height > 0,
                "latest_block_height": latest_block_height,
                "catching_up": catching_up,
                "validator_address": validator_info.get('address', ''),
                "network": result.get('node_info', {}).get('network', 'unknown'),
                "timestamp": sync_info.get('latest_block_time', '')
            }
            
        except requests.RequestException as e:
            return self._fallback_network_health(f"Network error: {str(e)}")
        except (json.JSONDecodeError, KeyError) as e:
            return self._fallback_network_health(f"Data parsing error: {str(e)}")
        except Exception as e:
            return self._fallback_network_health(f"Unexpected error: {str(e)}")
    
    def get_token_price(self) -> Dict[str, Any]:
        """
        Get ODIS token price data
        
        Note: Since ODIS is a testnet token, this returns mock data
        In production, this would integrate with actual price APIs
        """
        try:
            # For testnet, we provide simulated price data
            # In production, this would query actual price APIs like CoinGecko
            return {
                "success": True,
                "current_price": 4.85,
                "price_change_24h": 1.2,
                "price_change_percentage_24h": 0.25,
                "market_cap": 50000000,
                "volume_24h": 2500000,
                "last_updated": "2025-06-13T00:00:00Z",
                "note": "Testnet token - simulated data"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "current_price": 4.85,
                "price_change_24h": 0.0
            }
    
    def get_validators(self) -> Dict[str, Any]:
        """
        Get validator information from the network
        
        Returns:
            List of validators with their status and voting power
        """
        try:
            # Get validators from API endpoint
            response = requests.get(
                f"{self.api_endpoint}/cosmos/staking/v1beta1/validators",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            validators = data.get('validators', [])
            
            # Process validator data
            processed_validators = []
            for validator in validators[:10]:  # Limit to top 10
                processed_validators.append({
                    "operator_address": validator.get('operator_address', ''),
                    "moniker": validator.get('description', {}).get('moniker', 'Unknown'),
                    "status": validator.get('status', 'UNKNOWN'),
                    "tokens": validator.get('tokens', '0'),
                    "delegator_shares": validator.get('delegator_shares', '0'),
                    "commission_rate": validator.get('commission', {}).get('commission_rates', {}).get('rate', '0'),
                    "jailed": validator.get('jailed', False)
                })
            
            return {
                "success": True,
                "validators": processed_validators,
                "total_validators": len(validators)
            }
            
        except requests.RequestException as e:
            return self._fallback_validators(f"Network error: {str(e)}")
        except (json.JSONDecodeError, KeyError) as e:
            return self._fallback_validators(f"Data parsing error: {str(e)}")
        except Exception as e:
            return self._fallback_validators(f"Unexpected error: {str(e)}")
    
    def _fallback_network_health(self, error_msg: str) -> Dict[str, Any]:
        """Provide fallback network health data"""
        return {
            "success": False,
            "error": error_msg,
            "network_healthy": False,
            "latest_block_height": 0,
            "catching_up": True,
            "fallback": True
        }
    
    def _fallback_validators(self, error_msg: str) -> Dict[str, Any]:
        """Provide fallback validator data"""
        return {
            "success": False,
            "error": error_msg,
            "validators": [],
            "total_validators": 0,
            "fallback": True
        }
    
    def deploy_smart_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a smart contract to the blockchain
        
        Args:
            contract_data: Contract deployment parameters
            
        Returns:
            Deployment result with transaction hash
        """
        # This would implement actual contract deployment
        # For now, returning mock response
        return {
            "success": True,
            "transaction_hash": "mock_tx_hash_12345",
            "contract_address": "odiseo1mock_contract_address",
            "block_height": 3483092,
            "gas_used": 250000
        }
    
    def query_contract(self, contract_address: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query a smart contract
        
        Args:
            contract_address: Address of the contract to query
            query_data: Query parameters
            
        Returns:
            Query results
        """
        # This would implement actual contract querying
        return {
            "success": True,
            "data": {"mock": "query_result"}
        }