"""
Tests using the isolated test client to avoid interfering with the running application.
"""
import pytest
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestIsolatedClient:
    """Tests that use the isolated test client from conftest.py."""
    
    def test_index_endpoint(self, test_client):
        """Test the index endpoint using the isolated test client."""
        response = test_client.get('/')
        
        logger.debug(f"Response data: {response.data}")
        assert response.status_code == 200
        assert b'<h1>Test App</h1>' in response.data
    
    def test_contracts_endpoint(self, test_client):
        """Test the contracts endpoint using the isolated test client."""
        response = test_client.get('/api/contracts')
        
        logger.debug(f"Response data: {response.data}")
        assert response.status_code == 200
        
        # Parse the response
        data = json.loads(response.data)
        assert isinstance(data, list)
        
        # Verify the mocked contract data
        assert len(data) == 1
        assert data[0]["transaction_id"] == "tx_123456"
        assert data[0]["content_hash"] == "hash_abcdef"
        assert data[0]["status"] == "pending"