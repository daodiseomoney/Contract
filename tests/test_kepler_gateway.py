"""
Tests for the Kepler Gateway functionality, particularly focusing on memo parsing
which was a key fix area for our transaction problems.
"""
import pytest
from unittest.mock import patch

from src.gateways.kepler_gateway import KeplerGateway, KeplerSignatureRole

@pytest.fixture
def kepler_gateway():
    """Initialize Kepler Gateway for testing."""
    config = {
        'chain_id': 'odiseotestnet_1234-1',
        'rpc_url': 'https://rpc-test.odiseo.zone',
        'api_url': 'https://api-test.odiseo.zone' 
    }
    return KeplerGateway(config)

class TestKeplerGateway:
    """Test the Kepler wallet integration gateway."""
    
    def test_network_config(self, kepler_gateway):
        """Test network configuration is properly returned."""
        config = kepler_gateway.get_network_config()
        
        assert config['chainId'] == 'odiseotestnet_1234-1'
        assert 'rpc' in config
        assert 'rest' in config
    
    def test_memo_parsing_simplified_format(self, kepler_gateway):
        """Test parsing the new simplified memo format."""
        # New format: "tx_id:content_hash:role"
        memo = "tx_abc123:hash_def456:owner"
        
        result = kepler_gateway.parse_memo_data(memo)
        
        assert result['tx'] == 'tx_abc123'
        assert result['hash'] == 'hash_def456'
        assert result['role'] == 'owner'
    
    def test_memo_parsing_legacy_format(self, kepler_gateway):
        """Test parsing the legacy key:value|key:value format."""
        # Legacy format: "key:value|key:value|key:value"
        memo = "tx:tx_abc123|hash:hash_def456|role:owner"
        
        result = kepler_gateway.parse_memo_data(memo)
        
        assert result['tx'] == 'tx_abc123'
        assert result['hash'] == 'hash_def456'
        assert result['role'] == 'owner'
    
    def test_memo_parsing_invalid_format(self, kepler_gateway):
        """Test handling of invalid memo formats."""
        # Invalid format should return empty dict
        memo = "invalid_format_memo"
        
        result = kepler_gateway.parse_memo_data(memo)
        
        # Either empty dict or dict with error indication
        assert isinstance(result, dict)
        if result:
            assert 'error' in result
    
    def test_memo_parsing_empty_memo(self, kepler_gateway):
        """Test handling of empty memo."""
        memo = ""
        
        result = kepler_gateway.parse_memo_data(memo)
        
        # Should handle empty string gracefully
        assert isinstance(result, dict)
        assert len(result) == 0
    
    @patch('src.gateways.kepler_gateway.KeplerGateway.parse_memo_data')
    def test_sign_transaction(self, mock_parse_memo, kepler_gateway):
        """Test transaction signing with role validation."""
        # Setup mock
        mock_parse_memo.return_value = {
            'tx': 'tx_123',
            'hash': 'hash_456',
            'role': 'owner'
        }
        
        # Test data
        tx_data = {
            'signed': {
                'memo': 'tx_123:hash_456:owner',
                'msgs': []
            },
            'signature': {}
        }
        
        # Call with matching role
        result = kepler_gateway.sign_transaction(tx_data, KeplerSignatureRole.OWNER)
        
        # Should process successfully when roles match
        assert mock_parse_memo.called
        assert result is not None
        
        # Reset mock for next test
        mock_parse_memo.reset_mock()
        mock_parse_memo.return_value = {
            'tx': 'tx_123',
            'hash': 'hash_456',
            'role': 'owner'  # Memo says owner
        }
        
        # Call with non-matching role
        with pytest.raises(Exception):
            # Should raise exception when roles don't match
            kepler_gateway.sign_transaction(tx_data, KeplerSignatureRole.CONTRIBUTOR)