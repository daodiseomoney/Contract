from typing import Optional, Dict, List, Any
import json
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

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

    def connect_wallet(self, address: str) -> str:
        """
        Record a connected wallet address
        
        Args:
            address: The wallet address to connect
            
        Returns:
            str: The connected wallet address
        """
        # Store the connected address
        self.connected_address = address
        logger.info(f"Wallet connected: {address}")
        
        # In a real implementation, verify wallet ownership with a signature
        # TODO(DDS_TEAM): Implement signature verification for wallet connection
        
        return address

    def sign_transaction(self, tx_data: Dict, role: KeplerSignatureRole = None) -> Dict:
        """
        Prepare a transaction for signing with Keplr wallet
        
        Args:
            tx_data: Transaction data including from_address, to_address, and amount
            role: The role of the signer (optional)
            
        Returns:
            Dict: The formatted transaction sign doc for Keplr
        """
        # Get transaction parameters with defaults
        from_address = tx_data.get("from_address", "")
        to_address = tx_data.get("to_address", "")
        amount = tx_data.get("amount", [{"denom": "uodis", "amount": "1000"}])
        transaction_id = tx_data.get("transaction_id", "")
        content_hash = tx_data.get("content_hash", "")
        
        # Determine role value
        role_value = role.value if role else tx_data.get("role", "owner")
        
        # Standard fee for transactions (2500 uodis)
        fee = {
            "amount": [{"denom": "uodis", "amount": "2500"}],
            "gas": "100000"
        }
        
        # Create memo with transaction metadata
        memo = f"{transaction_id}:{content_hash}:{role_value}"
        
        # Create message in Amino format for Keplr compatibility
        msg = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": from_address,
                "to_address": to_address,
                "amount": amount
            }
        }
        
        # Create complete sign doc for Keplr
        sign_doc = {
            "chain_id": self.chain_id,
            "account_number": tx_data.get("account_number", "0"),
            "sequence": tx_data.get("sequence", "0"),
            "fee": fee,
            "msgs": [msg],
            "memo": memo
        }
        
        logger.debug(f"Sign doc prepared: {json.dumps(sign_doc, indent=2)}")
        return sign_doc
    
    def convert_amino_to_proto(self, msg: Dict) -> Dict:
        """
        Convert an Amino message to Proto format
        
        Args:
            msg: The Amino format message
            
        Returns:
            Dict: The Proto format message
        """
        # Handle Amino message with type/value structure
        if msg.get("type") == "cosmos-sdk/MsgSend" and "value" in msg:
            # Convert to Proto format
            proto_msg = {
                "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                "value": {
                    "fromAddress": msg["value"]["from_address"],
                    "toAddress": msg["value"]["to_address"],
                    "amount": msg["value"]["amount"]
                }
            }
            logger.debug(f"Converted Amino to Proto: {json.dumps(proto_msg, indent=2)}")
            return proto_msg
        
        # If already in Proto format, return as is
        if "typeUrl" in msg:
            return msg
            
        # For unknown formats, log warning
        logger.warning(f"Unknown message format for conversion: {msg}")
        return msg

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
