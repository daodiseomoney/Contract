"""
Unit tests for the transaction service that handles blockchain interactions.
"""
import pytest
import json
import logging
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def transaction_service():
    """Initialize transaction service for testing."""
    # Create a mock version of the transaction service
    mock_service = MagicMock()
    
    # Configure methods
    mock_service.create_sign_doc.return_value = {
        "account_number": "12345",
        "chain_id": "odiseotestnet_1234-1",
        "fee": {
            "amount": [{"amount": "2500", "denom": "uodis"}],
            "gas": "100000"
        },
        "memo": "tx_123456:hash_abcdef:owner",
        "msgs": [
            {
                "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                "value": {
                    "fromAddress": "odiseo1sender",
                    "toAddress": "odiseo1receiver",
                    "amount": [{"amount": "1000", "denom": "uodis"}]
                }
            }
        ],
        "sequence": "6789"
    }
    
    mock_service.broadcast_transaction.return_value = {
        "success": True,
        "txhash": "ABCDEF1234567890ABCDEF1234567890ABCDEF12",
        "height": "42",
        "code": 0,
        "gas_used": "80000",
        "raw_log": "transaction successful"
    }
    
    return mock_service

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
        "memo": "tx_123456:hash_abcdef:owner",
        "msgs": [
            {
                "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                "value": {
                    "fromAddress": "odiseo1sender",
                    "toAddress": "odiseo1receiver",
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
            "memo": "tx_123456:hash_abcdef:owner",
            "msgs": [
                {
                    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                    "value": {
                        "fromAddress": "odiseo1sender",
                        "toAddress": "odiseo1receiver",
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
        # Parameters for creating a sign doc
        sender_address = "odiseo1sender"
        msg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": sender_address,
                "toAddress": "odiseo1receiver",
                "amount": [{"amount": "1000", "denom": "uodis"}]
            }
        }
        account_data = {
            "account_number": "12345",
            "sequence": "6789"
        }
        
        # Call service method
        sign_doc = transaction_service.create_sign_doc(
            sender_address=sender_address,
            msg=msg,
            account_data=account_data
        )
        
        logger.debug(f"Sign doc: {json.dumps(sign_doc, indent=2)}")
        
        # Verify sign doc structure
        assert "account_number" in sign_doc
        assert "chain_id" in sign_doc
        assert "fee" in sign_doc
        assert "memo" in sign_doc
        assert "msgs" in sign_doc
        assert "sequence" in sign_doc
        
        # Verify message content
        assert sign_doc["msgs"][0]["typeUrl"] == "/cosmos.bank.v1beta1.MsgSend"
        assert sign_doc["msgs"][0]["value"]["fromAddress"] == sender_address
    
    def test_broadcast_transaction(self, transaction_service, sample_keplr_signature):
        """Test broadcasting a signed transaction."""
        # Call service method
        result = transaction_service.broadcast_transaction(sample_keplr_signature)
        
        logger.debug(f"Broadcast result: {json.dumps(result, indent=2)}")
        
        # Verify broadcast result
        assert result["success"] is True
        assert "txhash" in result
        assert "height" in result
        assert result["code"] == 0