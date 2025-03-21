from typing import List, Dict
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.tx import Transaction
from cosmpy.crypto.address import Address
import json

class CosmosBlockchainGateway:
    def __init__(self, mnemonic: str = None):
        # Configure for Odiseo testnet
        network_config = NetworkConfig(
            chain_id="odiseo_1234-1",  # Update with actual chain ID
            url="https://odiseo.test.rpc.nodeshub.online",
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )

        self.client = LedgerClient(network_config)
        if mnemonic:
            self.wallet = LocalWallet.from_mnemonic(mnemonic)
        else:
            self.wallet = LocalWallet.generate()

    async def deploy_contract(self, bim_hash: str, budget_splits: Dict) -> str:
        """Deploy smart contract for property tokenization"""
        try:
            # Create transaction
            tx = Transaction()
            tx.add_message(
                "/cosmos.bank.v1beta1.MsgSend",
                {
                    "from_address": self.wallet.address(),
                    "to_address": Address("odiseo1..."),  # Contract address
                    "amount": [{"denom": "uodis", "amount": "1"}],
                    "memo": json.dumps({
                        "bim_hash": bim_hash,
                        "budget_splits": budget_splits,
                        "type": "property_token"
                    })
                }
            )

            # Sign and broadcast
            tx_result = self.client.broadcast_tx(tx.sign(self.wallet))
            return tx_result.tx_hash
        except Exception as e:
            raise Exception(f"Failed to deploy contract: {str(e)}")

    def get_active_contracts(self) -> List[Dict]:
        """Query active property contracts"""
        try:
            query = self.client.query_bank_balance(self.wallet.address())
            # In real implementation, we would query contract state
            # This is simplified for demo
            return [{
                "id": query.tx_hash,
                "status": "active",
                "balance": query.balance,
                "property": "Property Token",
                "created": "2025-03-17"
            }]
        except Exception as e:
            raise Exception(f"Failed to fetch contracts: {str(e)}")