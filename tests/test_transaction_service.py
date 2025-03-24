"""
Unit tests for the transaction service that handles blockchain interactions.
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from src.services.transaction_service import TransactionService

@pytest.fixture
def transaction_service():
    """Initialize transaction service for testing."""
    service = TransactionService()
    # Use a mock client instead of initializing the real one
    service.client = MagicMock()
    return service

@pytest.fixture
def sample_sign_doc():
    """Create a sample sign document for Keplr."""
    return {
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
    }

@pytest.fixture
def sample_keplr_signature():
    """Sample Keplr signature response."""
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

class TestTransactionService:
    """Test the transaction service for creating and broadcasting transactions."""
    
    def test_create_sign_doc(self, transaction_service):
        """Test creating a sign doc for Keplr wallet."""
        sender_address = "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt"
        msg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": sender_address,
                "toAddress": sender_address,
                "amount": [{"amount": "1000", "denom": "uodis"}]
            }
        }
        account_data = {
            "account_number": "12345",
            "sequence": "6789"
        }
        
        # Mock account service
        with patch.object(transaction_service, 'get_account_data',
                         return_value=account_data):
            sign_doc = transaction_service.create_sign_doc(
                sender_address=sender_address,
                msg=msg,
                account_data=account_data
            )
            
            # Verify the sign doc structure
            assert sign_doc["chain_id"] == "odiseotestnet_1234-1"
            assert sign_doc["account_number"] == account_data["account_number"]
            assert sign_doc["sequence"] == account_data["sequence"]
            assert "msgs" in sign_doc
            assert "fee" in sign_doc
    
    def test_broadcast_transaction(self, transaction_service, sample_keplr_signature):
        """Test broadcasting a signed transaction."""
        # Mock the broadcast response
        mock_response = {
            "success": True,
            "txhash": "ABCDEF1234567890ABCDEF1234567890ABCDEF12",
            "height": "42",
            "code": 0,
            "gas_used": "80000",
            "raw_log": "transaction successful"
        }
        transaction_service.client.broadcast_tx.return_value = mock_response
        
        # Call the method
        result = transaction_service.broadcast_transaction(sample_keplr_signature)
        
        # Verify result
        assert result["success"] is True
        assert "txhash" in result
        assert result["txhash"] == mock_response["txhash"]
        
        # Verify the client was called correctly
        assert transaction_service.client.broadcast_tx.called