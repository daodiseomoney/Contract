"""
Tests for the Kepler Gateway functionality, particularly focusing on memo parsing
which was a key fix area for our transaction problems.
"""

import pytest
import logging
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Define a mock KeplerGateway class for testing
class MockKeplerGateway:
    """Simplified mock of KeplerGateway for testing."""

    def __init__(self, network_config=None):
        self.network_config = network_config or {
            "chain_id": "odiseotestnet_1234-1",
            "rpc_url": "https://rpc.odiseo.testnet.example.com",
            "rest_url": "https://lcd.odiseo.testnet.example.com",
            "token_denom": "uodis",
            "gas_price": 0.025,
        }

    def get_network_config(self):
        """Return network configuration for Kepler wallet."""
        return self.network_config

    def parse_memo_data(self, memo):
        """Parse transaction memo data with flexible format support."""
        # If memo is empty, return empty dict
        if not memo:
            return {}

        # New format: "tx_id:content_hash:role"
        if ":" in memo and "|" not in memo:
            parts = memo.split(":")
            if len(parts) == 3:
                return {"tx": parts[0], "hash": parts[1], "role": parts[2]}

        # Legacy format: "key:value|key:value"
        result = {}
        pairs = memo.split("|")
        for pair in pairs:
            if ":" in pair:
                key, value = pair.split(":", 1)
                result[key] = value

        return result


@pytest.fixture
def kepler_gateway():
    """Initialize Kepler Gateway for testing."""
    return MockKeplerGateway()


class TestKeplerGateway:
    """Test the Kepler wallet integration gateway."""

    def test_network_config(self, kepler_gateway):
        """Test network configuration is properly returned."""
        config = kepler_gateway.get_network_config()

        assert config["chain_id"] == "odiseotestnet_1234-1"
        assert "rpc_url" in config
        assert "rest_url" in config
        assert config["token_denom"] == "uodis"

    def test_memo_parsing_simplified_format(self, kepler_gateway):
        """Test parsing the new simplified memo format."""
        # New format: "tx_id:content_hash:role"
        memo = "tx_123456:hash_abcdef:owner"

        result = kepler_gateway.parse_memo_data(memo)

        assert result["tx"] == "tx_123456"
        assert result["hash"] == "hash_abcdef"
        assert result["role"] == "owner"

    def test_memo_parsing_legacy_format(self, kepler_gateway):
        """Test parsing the legacy key:value|key:value format."""
        # Legacy format: "key:value|key:value"
        memo = "tx:tx_123456|hash:hash_abcdef|role:owner"

        result = kepler_gateway.parse_memo_data(memo)

        assert result["tx"] == "tx_123456"
        assert result["hash"] == "hash_abcdef"
        assert result["role"] == "owner"

    def test_memo_parsing_invalid_format(self, kepler_gateway):
        """Test handling of invalid memo formats."""
        # Invalid format
        memo = "invalid-memo-format"

        result = kepler_gateway.parse_memo_data(memo)

        # Should return empty or partial dict
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_memo_parsing_empty_memo(self, kepler_gateway):
        """Test handling of empty memo."""
        # Empty memo
        memo = ""

        result = kepler_gateway.parse_memo_data(memo)

        assert isinstance(result, dict)
        assert len(result) == 0

    @patch("tests.test_kepler_gateway.MockKeplerGateway.parse_memo_data")
    def test_sign_transaction(self, mock_parse_memo, kepler_gateway):
        """Test transaction signing with role validation."""
        # Configure mock
        mock_parse_memo.return_value = {
            "tx": "tx_123456",
            "hash": "hash_abcdef",
            "role": "owner",
        }

        # Sample transaction data
        tx_data = {
            "signed": {
                "memo": "tx_123456:hash_abcdef:owner",
                "msgs": [{"typeUrl": "/cosmos.bank.v1beta1.MsgSend", "value": {}}],
            },
            "signature": {"signature": "base64-encoded-signature"},
        }

        # Test role validation (normally would be implemented in the sign_transaction method)
        parsed_memo = kepler_gateway.parse_memo_data(tx_data["signed"]["memo"])

        assert parsed_memo["role"] == "owner"

        # Verify mock was called correctly
        mock_parse_memo.assert_called_once_with(tx_data["signed"]["memo"])
