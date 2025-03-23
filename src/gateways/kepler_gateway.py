from typing import Optional, Dict
import json
from enum import Enum

class KeplerSignatureRole(Enum):
    OWNER = "owner"
    CONTRIBUTOR = "contributor"
    VALIDATOR = "validator"

class KeplerGateway:
    def __init__(self, network_config: Dict):
        self.chain_id = network_config['chain_id']
        self.rpc_url = network_config['rpc_url']
        self.api_url = network_config['api_url']
        self.connected_address: Optional[str] = None
        
    def get_network_config(self) -> Dict:
        """Return network configuration for Kepler wallet"""
        return {
            'chainId': self.chain_id,
            'chainName': 'Odiseo Testnet',
            'rpc': self.rpc_url,
            'rest': self.api_url,
            'bip44': {
                'coinType': 118,
            },
            'bech32Config': {
                'bech32PrefixAccAddr': 'odiseo',
                'bech32PrefixAccPub': 'odiseopub',
                'bech32PrefixValAddr': 'odiseoval',
                'bech32PrefixValPub': 'odiseovalpub',
                'bech32PrefixConsAddr': 'odiseovalcons',
                'bech32PrefixConsPub': 'odiseovalconspub'
            },
            'currencies': [{
                'coinDenom': 'ODIS',
                'coinMinimalDenom': 'uodis',
                'coinDecimals': 6,
            }],
            'feeCurrencies': [{
                'coinDenom': 'ODIS',
                'coinMinimalDenom': 'uodis',
                'coinDecimals': 6,
            }],
            'stakeCurrency': {
                'coinDenom': 'ODIS',
                'coinMinimalDenom': 'uodis',
                'coinDecimals': 6,
            },
            'gasPriceStep': {
                'low': 0.01,
                'average': 0.025,
                'high': 0.04
            }
        }

    async def connect_wallet(self) -> str:
        """This function will be called from JavaScript to connect Kepler wallet"""
        # The actual connection happens in JavaScript
        # This is just a placeholder for the backend interface
        pass

    async def sign_transaction(self, tx_data: Dict, role: KeplerSignatureRole) -> Dict:
        """This function will be called from JavaScript to sign a transaction"""
        # The actual signing happens in JavaScript
        # This is just a placeholder for the backend interface
        pass
