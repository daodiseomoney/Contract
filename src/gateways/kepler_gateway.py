from typing import Optional, Dict
import json
from enum import Enum


class KeplerSignatureRole(Enum):
    OWNER = "owner"
    CONTRIBUTOR = "contributor"
    VALIDATOR = "validator"


class KeplerGateway:
    def __init__(self, network_config: Dict):
        self.chain_id = network_config["chain_id"]
        self.rpc_url = network_config["rpc_url"]
        self.api_url = network_config["api_url"]
        self.connected_address: Optional[str] = None

    def get_network_config(self) -> Dict:
        """Return network configuration for Kepler wallet"""
        return {
            "chainId": self.chain_id,
            "chainName": "Odiseo Testnet",
            "rpc": self.rpc_url,
            "rest": self.api_url,
            "bip44": {
                "coinType": 118,
            },
            "bech32Config": {
                "bech32PrefixAccAddr": "odiseo",
                "bech32PrefixAccPub": "odiseopub",
                "bech32PrefixValAddr": "odiseoval",
                "bech32PrefixValPub": "odiseovalpub",
                "bech32PrefixConsAddr": "odiseovalcons",
                "bech32PrefixConsPub": "odiseovalconspub",
            },
            "currencies": [
                {
                    "coinDenom": "ODIS",
                    "coinMinimalDenom": "uodis",
                    "coinDecimals": 6,
                }
            ],
            "feeCurrencies": [
                {
                    "coinDenom": "ODIS",
                    "coinMinimalDenom": "uodis",
                    "coinDecimals": 6,
                }
            ],
            "stakeCurrency": {
                "coinDenom": "ODIS",
                "coinMinimalDenom": "uodis",
                "coinDecimals": 6,
            },
            "gasPriceStep": {"low": 0.01, "average": 0.025, "high": 0.04},
        }

    async def connect_wallet(self) -> str:
        """This function will be called from JavaScript to connect Kepler wallet"""
        # ------------------------------------------------------------
        # TODO(DDS_TEAM): Implement backend validation of wallet connection
        # TODO(DDS_TEAM): Store wallet connection in user session
        # TODO(DDS_TEAM): Verify wallet ownership using signature
        # ------------------------------------------------------------
        # The actual connection happens in JavaScript
        # This is just a placeholder for the backend interface
        return self.connected_address or ""  # Return empty string if None

    async def sign_transaction(self, tx_data: Dict, role: KeplerSignatureRole) -> Dict:
        """This function will be called from JavaScript to sign a transaction"""
        # ------------------------------------------------------------
        # TODO(DDS_TEAM): Implement proper Amino message formatting
        # TODO(DDS_TEAM): Add backend verification of signature
        # TODO(DDS_TEAM): Implement proper fee calculation
        # TODO(DDS_TEAM): Add transaction validation before signing
        # ------------------------------------------------------------
        # The actual signing happens in JavaScript
        # This is just a placeholder for the backend interface

        # Use simplified memo format matching our frontend changes
        transaction_id = tx_data.get("transaction_id", "")
        content_hash = tx_data.get("content_hash", "")
        role_value = role.value if role else "unknown"

        return {
            "messages": tx_data.get("messages", []),
            "fee": tx_data.get("fee", {}),
            "memo": f"{transaction_id}:{content_hash}:{role_value}",  # Simple colon-separated format
        }

    def parse_memo_data(self, memo: str) -> Dict:
        """Parse transaction memo data with flexible format support"""
        try:
            data = {}

            # Handle our ultra-simplified format: "transactionId:contentHash:role"
            if memo.count(":") == 2 and "|" not in memo:
                parts = memo.split(":")
                if len(parts) == 3:
                    data["tx"] = parts[0]
                    data["hash"] = parts[1]
                    data["role"] = parts[2]
                    return data

            # Handle our original format with pipe separators: "tx:id|hash:123|role:owner"
            elif "|" in memo:
                parts = memo.split("|")
                for part in parts:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        data[key.strip()] = value.strip()

            # If we didn't parse anything but there's content, store as raw_memo
            if not data and memo:
                data["raw_memo"] = memo

            return data
        except Exception as e:
            # Return a minimal dict if parsing fails
            return {"raw_memo": memo, "error": str(e)}
