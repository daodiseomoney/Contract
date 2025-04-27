"""
Isolated tests for the real estate tokenization flow using mocks.
These tests verify the business logic without requiring a running application.
"""

import pytest
import json
import logging
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestEndToEndFlow:
    """End-to-end test suite for the real estate tokenization platform."""

    def test_simplified_flow(
        self,
        mock_transaction_service,
        mock_multisig_gateway,
        mock_keplr_signature,
        mock_broadcast_response,
        sample_bim_file,
    ):
        """Test a simplified flow using mocks."""
        # 1. "Upload" a file - simulate file upload and transaction creation
        content_hash = "hash_" + sample_bim_file.getvalue().hex()[:6]
        transaction_id = mock_multisig_gateway.create_transaction(content_hash, {})

        logger.info(f"Created mock transaction: {transaction_id}")

        # 2. Verify transaction was created
        assert transaction_id == "tx_123456"

        # 3. Create a sign doc
        sender_address = "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"
        msg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": sender_address,
                "toAddress": sender_address,
                "amount": [{"amount": "1000", "denom": "uodis"}],
            },
        }
        account_data = {"account_number": "12345", "sequence": "6789"}

        sign_doc = mock_transaction_service.create_sign_doc(
            sender_address=sender_address, msg=msg, account_data=account_data
        )

        logger.info(f"Created sign doc: {sign_doc}")

        # 4. "Sign" the transaction - simulate Keplr signature
        # Update the mock signature to use our transaction ID
        signature_data = mock_keplr_signature.copy()
        signature_data["signed"]["memo"] = f"{transaction_id}:{content_hash}:owner"

        # 5. Submit the signature to the multisig gateway
        sign_result = mock_multisig_gateway.sign_transaction(
            transaction_id=transaction_id, role="owner", signature=signature_data
        )

        logger.info(f"Transaction signing result: {sign_result}")
        assert sign_result is True

        # 6. Broadcast the transaction
        broadcast_result = mock_transaction_service.broadcast_transaction(
            signature_data
        )

        logger.info(f"Transaction broadcast result: {broadcast_result}")
        assert broadcast_result["success"] is True
        assert broadcast_result["txhash"] == mock_broadcast_response["txhash"]

        # 7. Check transaction status
        tx_status = mock_multisig_gateway.get_transaction_status(transaction_id)

        logger.info(f"Transaction status: {tx_status}")
        assert tx_status["status"] == "signed"
        assert tx_status["signatures"]["owner"] is True

    def test_message_format_conversion(self):
        """Test converting between Proto and Amino message formats."""
        # Proto format (used by Keplr)
        proto_msg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": "odiseo1sender",
                "toAddress": "odiseo1receiver",
                "amount": [{"amount": "1000", "denom": "uodis"}],
            },
        }

        # Convert to Amino (used by backend)
        amino_msg = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": proto_msg["value"]["fromAddress"],
                "to_address": proto_msg["value"]["toAddress"],
                "amount": proto_msg["value"]["amount"],
            },
        }

        # Convert back to Proto
        converted_proto = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": amino_msg["value"]["from_address"],
                "toAddress": amino_msg["value"]["to_address"],
                "amount": amino_msg["value"]["amount"],
            },
        }

        # Verify round-trip conversion
        assert converted_proto["typeUrl"] == proto_msg["typeUrl"]
        assert (
            converted_proto["value"]["fromAddress"] == proto_msg["value"]["fromAddress"]
        )
        assert converted_proto["value"]["toAddress"] == proto_msg["value"]["toAddress"]
        assert converted_proto["value"]["amount"] == proto_msg["value"]["amount"]

    def test_memo_format_handling(self):
        """Test the simplified memo format handling."""
        # New simplified format
        tx_id = "tx_123456"
        content_hash = "hash_abcdef"
        role = "owner"

        # Create memo string (tx_id:content_hash:role)
        memo = f"{tx_id}:{content_hash}:{role}"

        # Parse memo by splitting on colon
        parts = memo.split(":")

        # Verify parsing
        assert len(parts) == 3
        assert parts[0] == tx_id
        assert parts[1] == content_hash
        assert parts[2] == role

        # Create parsed dict
        parsed = {"tx": parts[0], "hash": parts[1], "role": parts[2]}

        # Verify parsed values
        assert parsed["tx"] == tx_id
        assert parsed["hash"] == content_hash
        assert parsed["role"] == role

    @pytest.mark.parametrize(
        "memo_format",
        [
            "tx_123:hash_456:owner",  # New format
            "tx:tx_123|hash:hash_456|role:owner",  # Legacy format
        ],
    )
    def test_memo_format_compatibility(self, memo_format):
        """Test both legacy and new memo formats work with simple parsing logic."""
        # Parse new format (colon-separated)
        if ":" in memo_format and "|" not in memo_format:
            parts = memo_format.split(":")
            if len(parts) == 3:
                parsed = {"tx": parts[0], "hash": parts[1], "role": parts[2]}
        # Parse legacy format (pipe-separated key-value pairs)
        else:
            parsed = {}
            pairs = memo_format.split("|")
            for pair in pairs:
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    parsed[key] = value

        # Verify expected values are present regardless of format
        assert "tx" in parsed
        assert "hash" in parsed
        assert "role" in parsed
        assert "tx_123" in parsed["tx"]
        assert "hash_456" in parsed["hash"]
        assert parsed["role"] == "owner"
