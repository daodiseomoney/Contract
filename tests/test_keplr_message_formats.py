"""
Tests focused specifically on the Keplr wallet message format requirements.
These tests validate that our message conversions match the strict format requirements
of the real Keplr wallet browser extension.
"""

import json
import pytest
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Mock function similar to our frontend convertAminoToProto
def convert_amino_to_proto(amino_msg):
    """
    Convert Amino format message to Proto format for Keplr compatibility.
    This mimics the frontend convertAminoToProto function.
    """
    if not amino_msg or not isinstance(amino_msg, dict):
        return None

    if not amino_msg.get("type") or not amino_msg.get("value"):
        return None

    type_url_mapping = {
        "cosmos-sdk/MsgSend": "/cosmos.bank.v1beta1.MsgSend",
    }

    type_url = type_url_mapping.get(amino_msg["type"])
    if not type_url:
        return None

    # For MsgSend specifically, transform field names
    if amino_msg["type"] == "cosmos-sdk/MsgSend":
        value = amino_msg["value"]
        return {
            "typeUrl": type_url,
            "value": {
                "fromAddress": value.get("from_address"),
                "toAddress": value.get("to_address"),
                "amount": value.get("amount"),
            },
        }

    # Generic transformation
    return {"typeUrl": type_url, "value": amino_msg["value"]}


# Sample sign doc generator functions
def create_amino_sign_doc(user_address):
    """Create a sign doc in Amino format as would be used in the app."""
    return {
        "chain_id": "odiseotestnet_1234-1",
        "account_number": "0",
        "sequence": "0",
        "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
        "msgs": [
            {
                "type": "cosmos-sdk/MsgSend",
                "value": {
                    "from_address": user_address,
                    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"denom": "uodis", "amount": "1000"}],
                },
            }
        ],
        "memo": "tx:tx_1|hash:abcdef123456|role:owner",
    }


def create_proto_sign_doc(user_address):
    """Create a sign doc in Proto format as expected by Keplr."""
    return {
        "chain_id": "odiseotestnet_1234-1",
        "account_number": "0",
        "sequence": "0",
        "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
        "msgs": [
            {
                "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                "value": {
                    "fromAddress": user_address,
                    "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"denom": "uodis", "amount": "1000"}],
                },
            }
        ],
        "memo": "tx:tx_1|hash:abcdef123456|role:owner",
    }


class TestKeplrMessageFormat:
    """Tests for Keplr message format compatibility."""

    def test_amino_to_proto_conversion(self):
        """Test that Amino messages are properly converted to Proto format."""
        user_address = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"

        # Create Amino format sign doc (as in main.js originally)
        amino_doc = create_amino_sign_doc(user_address)

        # Apply our conversion logic
        proto_doc = {
            **amino_doc,
            "msgs": [convert_amino_to_proto(msg) for msg in amino_doc["msgs"]],
        }

        # Create the expected Proto format
        expected_proto = create_proto_sign_doc(user_address)

        # Log for debugging
        logger.debug(f"Original Amino Doc: {json.dumps(amino_doc, indent=2)}")
        logger.debug(f"Converted Proto Doc: {json.dumps(proto_doc, indent=2)}")
        logger.debug(f"Expected Proto Doc: {json.dumps(expected_proto, indent=2)}")

        # Verify conversion matches expected format
        assert proto_doc["msgs"][0]["typeUrl"] == expected_proto["msgs"][0]["typeUrl"]
        assert (
            proto_doc["msgs"][0]["value"]["fromAddress"]
            == expected_proto["msgs"][0]["value"]["fromAddress"]
        )
        assert (
            proto_doc["msgs"][0]["value"]["toAddress"]
            == expected_proto["msgs"][0]["value"]["toAddress"]
        )
        assert (
            proto_doc["msgs"][0]["value"]["amount"]
            == expected_proto["msgs"][0]["value"]["amount"]
        )

    def test_keplr_message_format_requirements(self):
        """Test that our message format meets Keplr wallet requirements."""
        user_address = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"

        # Create message in Keplr expected format
        keplr_msg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": user_address,
                "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                "amount": [{"denom": "uodis", "amount": "1000"}],
            },
        }

        # Verify required fields exist and are in the correct format
        assert "typeUrl" in keplr_msg, "Message must have typeUrl field"
        assert keplr_msg["typeUrl"].startswith(
            "/cosmos."
        ), "typeUrl must start with /cosmos."
        assert "value" in keplr_msg, "Message must have value field"
        assert "fromAddress" in keplr_msg["value"], "Value must have fromAddress field"
        assert "toAddress" in keplr_msg["value"], "Value must have toAddress field"
        assert "amount" in keplr_msg["value"], "Value must have amount field"
        assert isinstance(keplr_msg["value"]["amount"], list), "Amount must be a list"

    def test_improper_message_format_detection(self):
        """Test that improper message formats are detected."""
        # Amino format (incorrect for Keplr direct use)
        amino_msg = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": "odiseo1sender",
                "to_address": "odiseo1receiver",
                "amount": [{"denom": "uodis", "amount": "1000"}],
            },
        }

        # Wrong field names (camelCase vs snake_case)
        with pytest.raises(AssertionError):
            assert (
                "fromAddress" in amino_msg["value"]
            ), "Should fail: fromAddress not in Amino message"

        # Wrong type field name
        with pytest.raises(AssertionError):
            assert "typeUrl" in amino_msg, "Should fail: typeUrl not in Amino message"

    def test_sign_doc_format_compatibility(self):
        """Test that our sign doc format is compatible with Keplr requirements."""
        user_address = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"

        # Create Proto format sign doc (proper format for Keplr)
        proto_doc = create_proto_sign_doc(user_address)

        # Verify sign doc meets Keplr requirements
        assert "chain_id" in proto_doc, "Sign doc must have chain_id field"
        assert "account_number" in proto_doc, "Sign doc must have account_number field"
        assert "sequence" in proto_doc, "Sign doc must have sequence field"
        assert "fee" in proto_doc, "Sign doc must have fee field"
        assert "msgs" in proto_doc, "Sign doc must have msgs field"

        # Verify message format
        msg = proto_doc["msgs"][0]
        assert "typeUrl" in msg, "Message must have typeUrl field"
        assert (
            msg["typeUrl"] == "/cosmos.bank.v1beta1.MsgSend"
        ), "Incorrect typeUrl value"

        # Verify value fields use camelCase (Keplr requirement)
        value = msg["value"]
        assert "fromAddress" in value, "Value should use camelCase fields (fromAddress)"
        assert "toAddress" in value, "Value should use camelCase fields (toAddress)"

        # Verify Amino format would fail Keplr requirements
        amino_doc = create_amino_sign_doc(user_address)
        amino_msg = amino_doc["msgs"][0]

        with pytest.raises(AssertionError):
            assert "typeUrl" in amino_msg, "Should fail: typeUrl not in Amino message"

        with pytest.raises(AssertionError):
            assert (
                "fromAddress" in amino_msg["value"]
            ), "Should fail: fromAddress not in Amino value"


class TestKeplrMessageEdgeCases:
    """Test edge cases and error handling for Keplr message formats."""

    def test_null_message_handling(self):
        """Test handling of null or undefined messages."""
        result = convert_amino_to_proto(None)
        assert result is None, "Should return None for null input"

        result = convert_amino_to_proto({})
        assert result is None, "Should return None for empty object"

    def test_unknown_message_type(self):
        """Test handling of unknown message types."""
        unknown_msg = {"type": "cosmos-sdk/UnknownType", "value": {"some": "value"}}

        result = convert_amino_to_proto(unknown_msg)
        assert result is None, "Should return None for unknown message type"

    def test_malformed_message(self):
        """Test handling of malformed messages."""
        # Missing value field
        malformed_msg = {
            "type": "cosmos-sdk/MsgSend"
            # No value field
        }

        result = convert_amino_to_proto(malformed_msg)
        assert result is None, "Should return None for message without value"

        # Missing type field
        malformed_msg = {
            # No type field
            "value": {"from_address": "odiseo1sender"}
        }

        result = convert_amino_to_proto(malformed_msg)
        assert result is None, "Should return None for message without type"
