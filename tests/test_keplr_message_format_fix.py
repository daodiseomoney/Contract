"""
Test cases for the Keplr message format fix to ensure proper message format handling.
These tests focus on validating the fixes made to address the 'Expected a message object' error.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

# Simulate the message formats we're dealing with
AMINO_FORMAT = {
    "type": "cosmos-sdk/MsgSend",
    "value": {
        "from_address": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
        "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
        "amount": [{ "denom": "uodis", "amount": "1000" }]
    }
}

KEPLR_EXPECTED_FORMAT = {
    "@type": "/cosmos.bank.v1beta1.MsgSend",
    "from_address": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
    "amount": [{ "denom": "uodis", "amount": "1000" }]
}

PROTO_FORMAT = {
    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
    "value": {
        "fromAddress": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
        "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
        "amount": [{ "denom": "uodis", "amount": "1000" }]
    }
}

# Mock the Keplr wallet interface
class MockKeplrWallet:
    def __init__(self):
        self.sign_calls = []
    
    async def signAmino(self, chainId, signer, signDoc, options=None):
        """Mock implementation that validates message format like the real Keplr wallet."""
        self.sign_calls.append({
            "chainId": chainId,
            "signer": signer,
            "signDoc": signDoc,
            "options": options
        })
        
        # Validate the message format strictly as Keplr would
        if not signDoc or not signDoc.get("msgs"):
            raise ValueError("signDoc or msgs is missing")
            
        for msg in signDoc["msgs"]:
            # Check if message has the expected format
            if isinstance(msg, dict) and msg.get("type") and msg.get("value"):
                # This is the old Amino format with type/value nesting - should fail
                raise ValueError(f"Expected a message object, but got {msg}.")
            
            # If using @type field, it should have the right format
            if not msg.get("@type") and not msg.get("typeUrl"):
                raise ValueError(f"Message missing @type or typeUrl: {msg}")
                
        # If validation passes, return a mock signature
        return {
            "signed": signDoc,
            "signature": {
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "A1234567890abcdef" 
                },
                "signature": "BASE64_SIGNATURE_STRING"
            }
        }


class TestKeplrMessageFormatFix:
    """Test suite for fixing the Keplr message format issue."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_keplr = MockKeplrWallet()
        
    @patch("window.keplr", None)
    def test_old_amino_format_fails(self):
        """Test that the old Amino format with type/value nesting fails."""
        # Simulate what happens in JavaScript
        sign_doc = {
            "chain_id": "odiseotestnet_1234-1",
            "account_number": "0",
            "sequence": "0",
            "fee": {
                "amount": [{ "denom": "uodis", "amount": "2500" }],
                "gas": "100000"
            },
            "msgs": [AMINO_FORMAT],
            "memo": "tx:tx_1|hash:abc123|role:contributor"
        }
        
        with pytest.raises(ValueError) as exc_info:
            self.mock_keplr.signAmino("odiseotestnet_1234-1", "odiseo1abc", sign_doc)
            
        assert "Expected a message object" in str(exc_info.value)
    
    @patch("window.keplr", None)
    def test_keplr_expects_direct_object_properties(self):
        """Test that Keplr expects direct object properties not nested under value."""
        # Simulate the fixed format we're now using
        sign_doc = {
            "chain_id": "odiseotestnet_1234-1",
            "account_number": "0",
            "sequence": "0",
            "fee": {
                "amount": [{ "denom": "uodis", "amount": "2500" }],
                "gas": "100000"
            },
            "msgs": [KEPLR_EXPECTED_FORMAT],
            "memo": "tx:tx_1|hash:abc123|role:contributor"
        }
        
        # This should NOT raise an exception
        result = self.mock_keplr.signAmino("odiseotestnet_1234-1", "odiseo1abc", sign_doc)
        assert result["signed"] == sign_doc
    
    def test_conversion_from_amino_to_keplr_format(self):
        """Test our function that converts from Amino to Keplr format."""
        def convert_amino_to_keplr(amino_msg):
            """Simplified version of our JavaScript converter."""
            if amino_msg.get("type") and amino_msg.get("value"):
                msg_type = amino_msg["type"].split("/")[-1]
                return {
                    "@type": f"/cosmos.bank.v1beta1.{msg_type}",
                    **amino_msg["value"]
                }
            return amino_msg
            
        converted = convert_amino_to_keplr(AMINO_FORMAT)
        
        # Check if conversion is correct
        assert converted["@type"] == "/cosmos.bank.v1beta1.MsgSend"
        assert converted["from_address"] == "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        assert converted["to_address"] == "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"
        assert converted["amount"][0]["amount"] == "1000"
        
        # Ensure it doesn't have type/value nesting anymore
        assert "type" not in converted
        assert "value" not in converted
    
    def test_memo_format(self):
        """Test that the memo format is correct."""
        # The original memo format
        memo = "tx:tx_1|hash:abc123|role:contributor"
        
        # Parse the memo string
        parts = {}
        for part in memo.split("|"):
            if ":" in part:
                key, value = part.split(":", 1)
                parts[key] = value
                
        # Check that the memo format is correctly parsed
        assert parts["tx"] == "tx_1"
        assert parts["hash"] == "abc123"
        assert parts["role"] == "contributor"