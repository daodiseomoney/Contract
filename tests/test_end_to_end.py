import pytest
import os
import json
import base64
import time
import logging
from io import BytesIO
from unittest.mock import patch, MagicMock

# Configure logging for test debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the Flask app fixture to use in tests
@pytest.fixture
def client():
    # Import main app here to avoid circular imports
    import main
    main.app.config['TESTING'] = True
    
    with main.app.test_client() as client:
        yield client

# Mock data for testing
@pytest.fixture
def sample_bim_file():
    """Create a sample BIM file for testing."""
    file_content = b"Sample BIM file content for testing purposes"
    return BytesIO(file_content)

@pytest.fixture
def mock_account_data():
    """Mock account data returned from Keplr/blockchain."""
    return {
        "address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
        "account_number": "12345",
        "sequence": "6789"
    }

@pytest.fixture
def mock_keplr_signature():
    """Mock signature response similar to what Keplr wallet would return."""
    return {
        "signed": {
            "account_number": "12345",
            "chain_id": "odiseotestnet_1234-1",
            "fee": {
                "amount": [{"amount": "2500", "denom": "uodis"}],
                "gas": "100000"
            },
            "memo": "tx_123:content_hash_456:owner",
            "msgs": [
                {
                    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                    "value": {
                        "fromAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        "amount": [{"amount": "1000", "denom": "uodis"}]
                    }
                }
            ],
            "sequence": "6789"
        },
        "signature": {
            "pub_key": {
                "type": "tendermint/PubKeySecp256k1",
                "value": "A4VPT8ybcJHimQK9HeIOt1YxV1J+e/Z+Q9UkodyDjT9M"
            },
            "signature": "ZW5jb2RlZC1zaWduYXR1cmUtdmFsdWUtZm9yLXRlc3Rpbmc="
        }
    }

@pytest.fixture
def mock_broadcast_response():
    """Mock successful transaction broadcast response."""
    return {
        "success": True,
        "txhash": "ABCDEF1234567890ABCDEF1234567890ABCDEF12",
        "height": "42",
        "code": 0,
        "gas_used": "80000",
        "raw_log": "transaction successful"
    }

# Test the complete flow
class TestEndToEndFlow:
    """End-to-end test suite for the real estate tokenization platform."""
    
    def test_file_upload(self, client, sample_bim_file):
        """Test file upload endpoint returns expected transaction data."""
        # Prepare test file
        data = {
            'file': (sample_bim_file, 'test.bim'),
            'name': 'Test Property',
            'address': '123 Test Street, Testville',
            'roles[]': ['owner', 'architect'],
            'percentages[]': ['60', '40']
        }

        # Send upload request
        logger.info("Sending file upload request")
        response = client.post('/api/upload', 
                              data=data, 
                              content_type='multipart/form-data')
        
        logger.debug(f"Upload response: {response.data}")
        assert response.status_code == 200
        
        # Parse response data
        response_data = json.loads(response.data)
        assert 'transaction' in response_data
        assert 'transaction_id' in response_data['transaction']
        assert 'content_hash' in response_data['transaction']
        
        # Return values needed for next test
        return response_data['transaction']
    
    @patch('src.controllers.account_controller.AccountService.get_account_data')
    def test_account_info(self, mock_get_account, client, mock_account_data):
        """Test account data retrieval."""
        # Mock the account service response
        mock_get_account.return_value = mock_account_data
        
        # Request account info
        response = client.get('/api/account?address=odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt')
        
        logger.debug(f"Account info response: {response.data}")
        assert response.status_code == 200
        
        # Verify response
        account_data = json.loads(response.data)
        assert account_data['account_number'] == mock_account_data['account_number']
        assert account_data['sequence'] == mock_account_data['sequence']
        
    @patch('src.controllers.transaction_controller.transaction_service.broadcast_transaction')
    def test_sign_transaction(self, mock_broadcast, client, mock_keplr_signature, mock_broadcast_response):
        """Test transaction signing endpoint with mocked Keplr signature."""
        # Setup mocks
        mock_broadcast.return_value = mock_broadcast_response
        
        # Prepare signature payload
        payload = mock_keplr_signature
        
        # Send signature to endpoint
        logger.info("Sending transaction sign request")
        response = client.post('/api/sign',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        logger.debug(f"Sign response: {response.data}")
        assert response.status_code == 200
        
        # Verify response indicates success
        response_data = json.loads(response.data)
        assert response_data.get('success') is True
        assert 'txhash' in response_data
    
    def test_broadcast_transaction(self, client, mock_keplr_signature, mock_broadcast_response):
        """Test direct broadcast endpoint with mock transaction data."""
        with patch('src.services.transaction_service.TransactionService.broadcast_transaction', 
                   return_value=mock_broadcast_response):
            
            # Create broadcast request payload
            # This uses the signed transaction format from Keplr
            tx_body = {
                'tx': {
                    'msg': mock_keplr_signature['signed']['msgs'],
                    'fee': mock_keplr_signature['signed']['fee'],
                    'memo': mock_keplr_signature['signed']['memo'],
                    'signatures': [{
                        'pub_key': mock_keplr_signature['signature']['pub_key'],
                        'signature': mock_keplr_signature['signature']['signature']
                    }]
                },
                'mode': 'block'
            }
            
            # Send broadcast request
            logger.info("Sending transaction broadcast request")
            response = client.post('/api/broadcast',
                                  data=json.dumps(tx_body),
                                  content_type='application/json')
            
            logger.debug(f"Broadcast response: {response.data}")
            assert response.status_code == 200
            
            # Verify successful broadcast
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            assert response_data['txhash'] == mock_broadcast_response['txhash']
    
    def test_contracts_endpoint(self, client):
        """Test contracts endpoint returns transaction data."""
        # Get contracts list
        response = client.get('/api/contracts')
        
        logger.debug(f"Contracts response: {response.data}")
        assert response.status_code == 200
        
        # Verify response format
        contracts_data = json.loads(response.data)
        assert isinstance(contracts_data, list)
        
        # If contracts exist, validate fields
        if contracts_data:
            contract = contracts_data[0]
            assert 'transaction_id' in contract
            assert 'status' in contract
    
    def test_full_e2e_flow(self, client, sample_bim_file, mock_account_data, mock_keplr_signature, mock_broadcast_response):
        """Simulate the complete end-to-end flow."""
        # Setup mocks
        with patch('src.controllers.account_controller.AccountService.get_account_data', return_value=mock_account_data), \
             patch('src.controllers.transaction_controller.transaction_service.broadcast_transaction', return_value=mock_broadcast_response):
            
            # 1. First upload a file
            transaction = self.test_file_upload(client, sample_bim_file)
            logger.info(f"Created transaction: {transaction}")
            transaction_id = transaction['transaction_id']
            
            # 2. Update mock signature with actual transaction ID
            mock_keplr_signature['signed']['memo'] = f"{transaction_id}:{transaction['content_hash']}:owner"
            
            # 3. Now sign the transaction with our mock Keplr data
            sign_response = client.post('/api/sign',
                                       data=json.dumps(mock_keplr_signature),
                                       content_type='application/json')
            sign_data = json.loads(sign_response.data)
            logger.info(f"Sign response: {sign_data}")
            
            assert sign_response.status_code == 200
            assert sign_data.get('success') is True
            
            # 4. Verify the transaction appears in contracts list
            # Wait a moment for any async processing
            time.sleep(0.5)
            contracts_response = client.get('/api/contracts')
            contracts = json.loads(contracts_response.data)
            
            # Find our transaction in the list
            matching_contracts = [c for c in contracts if c.get('transaction_id') == transaction_id]
            assert len(matching_contracts) > 0, f"Transaction {transaction_id} not found in contracts"
            
            contract = matching_contracts[0]
            assert contract['status'] in ['signed', 'pending']
            
            logger.info("End-to-end test completed successfully")

# Extra utility tests
class TestUtilities:
    """Additional tests for utility functions used in the application."""
    
    def test_memo_parsing(self):
        """Test both legacy and new memo formats."""
        from src.gateways.kepler_gateway import KeplerGateway
        
        # Setup
        config = {
            'chain_id': 'odiseotestnet_1234-1',
            'rpc_url': 'https://rpc.example.com',
            'api_url': 'https://api.example.com'
        }
        kepler = KeplerGateway(config)
        
        # Test new simplified format
        new_memo = "tx_123:hash_456:owner"
        parsed_new = kepler.parse_memo_data(new_memo)
        assert parsed_new.get('tx') == 'tx_123'
        assert parsed_new.get('hash') == 'hash_456'
        assert parsed_new.get('role') == 'owner'
        
        # Test legacy format
        legacy_memo = "tx:tx_123|hash:hash_456|role:owner"
        parsed_legacy = kepler.parse_memo_data(legacy_memo)
        assert parsed_legacy.get('tx') == 'tx_123'
        assert parsed_legacy.get('hash') == 'hash_456'
        assert parsed_legacy.get('role') == 'owner'
    
    def test_message_format_conversion(self):
        """Test conversion between Amino and Proto message formats."""
        from src.controllers.transaction_controller import logger
        
        # Proto format message
        proto_msg = {
            'typeUrl': '/cosmos.bank.v1beta1.MsgSend',
            'value': {
                'fromAddress': 'odiseo1sender',
                'toAddress': 'odiseo1receiver',
                'amount': [{'amount': '1000', 'denom': 'uodis'}]
            }
        }
        
        # Mock processing function similar to our controller logic
        def process_message(msg):
            processed_msgs = []
            
            if isinstance(msg, dict):
                if 'typeUrl' in msg and 'value' in msg:
                    if msg['typeUrl'] == '/cosmos.bank.v1beta1.MsgSend':
                        value = msg.get('value', {})
                        amino_msg = {
                            'type': 'cosmos-sdk/MsgSend',
                            'value': {
                                'from_address': value.get('fromAddress', ''),
                                'to_address': value.get('toAddress', ''),
                                'amount': value.get('amount', [])
                            }
                        }
                        processed_msgs.append(amino_msg)
            
            return processed_msgs
        
        # Test conversion
        result = process_message(proto_msg)
        assert len(result) == 1
        
        amino_msg = result[0]
        assert amino_msg['type'] == 'cosmos-sdk/MsgSend'
        assert amino_msg['value']['from_address'] == 'odiseo1sender'
        assert amino_msg['value']['to_address'] == 'odiseo1receiver'
        assert amino_msg['value']['amount'][0]['amount'] == '1000'