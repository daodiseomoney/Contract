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
        "amount": [{"denom": "uodis", "amount": "1000"}],
    },
}

INCORRECT_FORMAT = {
    "@type": "/cosmos.bank.v1beta1.MsgSend",
    "from_address": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
    "amount": [{"denom": "uodis", "amount": "1000"}],
}

PROTO_FORMAT = {
    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
    "value": {
        "fromAddress": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
        "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
        "amount": [{"denom": "uodis", "amount": "1000"}],
    },
}


# Mock the Keplr wallet interface
class MockKeplrWallet:
    def __init__(self):
        self.sign_calls = []

    def signAmino(self, chainId, signer, signDoc, options=None):
        """Mock implementation that validates message format like the real Keplr wallet."""
        self.sign_calls.append(
            {
                "chainId": chainId,
                "signer": signer,
                "signDoc": signDoc,
                "options": options,
            }
        )

        # Validate the message format strictly as Keplr would
        if not signDoc or not signDoc.get("msgs"):
            raise ValueError("signDoc or msgs is missing")

        for msg in signDoc["msgs"]:
            # We no longer validate against @type field since we now use direct format
            # Instead, validate that the message has required Keplr fields
            if "@type" in msg:
                # This format is now supported
                if not msg.get("from_address") or not msg.get("to_address"):
                    raise ValueError(f"Missing required fields in message: {msg}")

            # Check for proper Amino format
            if not (msg.get("type") and msg.get("value")):
                raise ValueError(f"Message missing type/value structure: {msg}")

        # If validation passes, return a mock signature
        return {
            "signed": signDoc,
            "signature": {
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "A1234567890abcdef",
                },
                "signature": "BASE64_SIGNATURE_STRING",
            },
        }


class TestKeplrMessageFormatFix:
    """Test suite for fixing the Keplr message format issue."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_keplr = MockKeplrWallet()

    def test_incorrect_format_fails(self):
        """Test that the incorrect format with @type field fails."""
        # Simulate what happens in JavaScript with incorrect format
        sign_doc = {
            "chain_id": "odiseotestnet_1234-1",
            "account_number": "0",
            "sequence": "0",
            "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
            "msgs": [INCORRECT_FORMAT],
            "memo": "tx:tx_1|hash:abc123|role:contributor",
        }

        with pytest.raises(ValueError) as exc_info:
            self.mock_keplr.signAmino("odiseotestnet_1234-1", "odiseo1abc", sign_doc)

        assert "Message missing type/value structure" in str(exc_info.value)

    def test_amino_format_succeeds(self):
        """Test that the proper Amino format with type/value structure succeeds."""
        # Simulate the correct format we're now using
        sign_doc = {
            "chain_id": "odiseotestnet_1234-1",
            "account_number": "0",
            "sequence": "0",
            "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
            "msgs": [AMINO_FORMAT],
            "memo": "tx:tx_1|hash:abc123|role:contributor",
        }

        # This should NOT raise an exception
        result = self.mock_keplr.signAmino(
            "odiseotestnet_1234-1", "odiseo1abc", sign_doc
        )
        assert result["signed"] == sign_doc

    def test_conversion_from_incorrect_to_amino_format(self):
        """Test our function that converts from incorrect to Amino format."""

        def convert_to_amino(incorrect_msg):
            """Simplified version of our JavaScript converter."""
            if "@type" in incorrect_msg:
                msg_type = "cosmos-sdk/MsgSend"
                return {
                    "type": msg_type,
                    "value": {
                        "from_address": incorrect_msg["from_address"],
                        "to_address": incorrect_msg["to_address"],
                        "amount": incorrect_msg["amount"],
                    },
                }
            return incorrect_msg

        converted = convert_to_amino(INCORRECT_FORMAT)

        # Check if conversion is correct
        assert converted["type"] == "cosmos-sdk/MsgSend"
        assert "value" in converted
        assert (
            converted["value"]["from_address"]
            == "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        )
        assert (
            converted["value"]["to_address"]
            == "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"
        )
        assert converted["value"]["amount"][0]["amount"] == "1000"

        # Ensure it doesn't have @type field anymore
        assert "@type" not in converted

    def test_amino_to_proto_conversion(self):
        """Test converting from Amino to Proto format."""

        def convert_amino_to_proto(amino_msg):
            """Convert from Amino format to Proto format."""
            if amino_msg.get("type") == "cosmos-sdk/MsgSend" and "value" in amino_msg:
                return {
                    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                    "value": {
                        "fromAddress": amino_msg["value"]["from_address"],
                        "toAddress": amino_msg["value"]["to_address"],
                        "amount": amino_msg["value"]["amount"],
                    },
                }
            return amino_msg

        proto_msg = convert_amino_to_proto(AMINO_FORMAT)

        # Check if conversion is correct
        assert proto_msg["typeUrl"] == "/cosmos.bank.v1beta1.MsgSend"
        assert (
            proto_msg["value"]["fromAddress"]
            == "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        )
        assert (
            proto_msg["value"]["toAddress"]
            == "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"
        )
        assert proto_msg["value"]["amount"][0]["amount"] == "1000"

    def test_memo_format(self):
        """Test that the memo format is correct."""
        # The proper memo format
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
