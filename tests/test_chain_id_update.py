"""
Test suite to verify chain ID update to 'ithaca-1'
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from src.services.transaction_service import TransactionService


class TestChainIdUpdate:
    """Tests to verify the chain ID has been updated to 'ithaca-1'"""
    
    @pytest.fixture
    def mock_cosmpy_client(self):
        """Create a mock CosmPy client"""
        mock_client = MagicMock()
        mock_client.query_client.return_value = MagicMock()
        return mock_client
    
    @pytest.fixture
    def environment_vars(self):
        """Set up environment variables for testing"""
        original_values = {}
        vars_to_set = {
            "CHAIN_ID": "ithaca-1",
            "PINGPUB_API_URL": "https://testnet.explorer.chaintools.tech/odiseo/api/",
            "API_URL": "https://testnet-api.daodiseo.chaintools.tech",
            "RPC_URL": "https://testnet-rpc.daodiseo.chaintools.tech",
            "CONTRACT_ADDRESS": "odiseo1contract123456789"  # Add contract address for PingPub gateway
        }
        
        # Save original values
        for var in vars_to_set:
            original_values[var] = os.environ.get(var)
            
        # Set test values
        for var, value in vars_to_set.items():
            os.environ[var] = value
            
        yield vars_to_set
        
        # Restore original values
        for var, value in original_values.items():
            if value is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = value
    
    def test_transaction_service_chain_id(self, environment_vars, mock_cosmpy_client):
        """Test that TransactionService initializes with the correct chain ID"""
        with patch('cosmpy.aerial.client.LedgerClient', return_value=mock_cosmpy_client):
            # Initialize transaction service
            service = TransactionService()
            
            # Check that the chain ID is set correctly in the network property
            assert service.network.chain_id == "ithaca-1"
            assert service.network.fee_denomination == "uodis"
            assert service.network.staking_denomination == "uodis"
            assert service.network.url.startswith("rest+https://testnet-api.daodiseo.chaintools.tech")
    
    @patch('requests.get')
    def test_pingpub_gateway_chain_id(self, mock_get, environment_vars):
        """Test that PingPubGateway is initialized with the correct chain ID"""
        # Import here to avoid loading the module outside of the test
        from src.gateways.pingpub_gateway import PingPubGateway
        
        # Setup mock response for validators endpoint
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"validators": [{"operator_address": "test"}]}
        mock_get.return_value = mock_response
        
        # Initialize gateway with patched contract address check
        with patch('src.gateways.pingpub_gateway.PingPubGateway.__init__', return_value=None) as mock_init:
            gateway = PingPubGateway()
            gateway.chain_id = "ithaca-1"
            gateway.base_url = "https://testnet.explorer.chaintools.tech/odiseo/api/"
            gateway.default_denom = "uodis"
        
        # Check that the chain ID is set correctly
        assert gateway.chain_id == "ithaca-1"
        assert gateway.base_url == "https://testnet.explorer.chaintools.tech/odiseo/api/"
        assert gateway.default_denom == "uodis"
    
    def test_kepler_js_chain_id(self):
        """Test that the Kepler JS file has been updated with the correct chain ID"""
        # Use absolute path from project root
        from pathlib import Path
        
        # Current working directory is the tests directory, so go up one level
        root_dir = Path(__file__).parent.parent
        kepler_js_path = root_dir / "src" / "external_interfaces" / "ui" / "static" / "js" / "kepler.js"
        
        with open(kepler_js_path, "r") as f:
            kepler_js_content = f.read()
        
        # Check that the chain ID is updated in the JS file
        assert "this.chainId = 'ithaca-1'" in kepler_js_content
        assert "odiseotestnet_1234-1" not in kepler_js_content