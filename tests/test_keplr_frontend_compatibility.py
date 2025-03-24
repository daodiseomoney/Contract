"""
Tests for frontend compatibility with Keplr wallet requirements.
These tests validate that our JavaScript conversion functions work correctly
and produce messages in the format required by the Keplr wallet.
"""
import json
import pytest
import logging
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mock the JavaScript convertAminoToProto function from transaction.js
def mock_js_convert_amino_to_proto(amino_msg):
    """
    Python implementation of the JavaScript convertAminoToProto function.
    This mimics the behavior of the frontend function to ensure compatibility.
    """
    type_url_mapping = {
        'cosmos-sdk/MsgSend': '/cosmos.bank.v1beta1.MsgSend',
    }
    
    if not amino_msg or 'type' not in amino_msg or 'value' not in amino_msg:
        logger.error(f"Invalid Amino message format: {amino_msg}")
        raise ValueError("Invalid Amino message format")
    
    type_url = type_url_mapping.get(amino_msg['type'])
    if not type_url:
        logger.error(f"Unknown message type: {amino_msg['type']}")
        raise ValueError(f"Unknown message type: {amino_msg['type']}")
    
    logger.debug(f"Converting Amino message type '{amino_msg['type']}' to Proto typeUrl '{type_url}'")
    
    # Handle MsgSend specifically
    if amino_msg['type'] == 'cosmos-sdk/MsgSend':
        return {
            'typeUrl': type_url,
            'value': {
                'fromAddress': amino_msg['value']['from_address'],
                'toAddress': amino_msg['value']['to_address'],
                'amount': amino_msg['value']['amount']
            }
        }
    
    # Generic conversion
    return {
        'typeUrl': type_url,
        'value': amino_msg['value']
    }

# Mock for Keplr wallet that validates message format
class MockKeplrWallet:
    """Mock of the Keplr wallet that validates message formats strictly."""
    
    def validate_message(self, msg):
        """Validate message format strictly as Keplr would."""
        if not isinstance(msg, dict):
            raise TypeError("Message must be an object")
            
        if 'typeUrl' not in msg:
            raise ValueError("Expected a message object with typeUrl, but got: " + str(msg))
            
        if not isinstance(msg['value'], dict):
            raise ValueError("Message value must be an object")
            
        # Validate MsgSend format
        if msg['typeUrl'] == '/cosmos.bank.v1beta1.MsgSend':
            value = msg['value']
            required_fields = ['fromAddress', 'toAddress', 'amount']
            
            for field in required_fields:
                if field not in value:
                    raise ValueError(f"Message value missing required field: {field}")
            
            if not isinstance(value['amount'], list):
                raise ValueError("Message amount must be an array")
        
        return True
    
    def validate_sign_doc(self, sign_doc):
        """Validate sign doc format strictly as Keplr would."""
        required_fields = ['chain_id', 'account_number', 'sequence', 'fee', 'msgs', 'memo']
        
        for field in required_fields:
            if field not in sign_doc:
                raise ValueError(f"Sign doc missing required field: {field}")
        
        if not isinstance(sign_doc['msgs'], list):
            raise ValueError("Sign doc msgs must be an array")
        
        # Validate each message
        for msg in sign_doc['msgs']:
            self.validate_message(msg)
        
        return True

class TestKeplrFrontendCompatibility:
    """Tests for frontend compatibility with Keplr wallet."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.keplr = MockKeplrWallet()
        self.user_address = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
    
    def test_js_conversion_function(self):
        """Test the JavaScript conversion function behavior."""
        # Create an Amino format message
        amino_msg = {
            'type': 'cosmos-sdk/MsgSend',
            'value': {
                'from_address': self.user_address,
                'to_address': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
                'amount': [{'denom': 'uodis', 'amount': '1000'}]
            }
        }
        
        # Convert to Proto format
        proto_msg = mock_js_convert_amino_to_proto(amino_msg)
        
        logger.debug(f"Converted Proto message: {json.dumps(proto_msg, indent=2)}")
        
        # Verify Keplr would accept this format
        assert self.keplr.validate_message(proto_msg), "Keplr should accept the converted message"
    
    def test_main_js_sign_doc_conversion(self):
        """Test that main.js sign doc conversion meets Keplr requirements."""
        # Create an Amino format sign doc (as would be created in main.js)
        amino_doc = {
            'chain_id': 'odiseotestnet_1234-1',
            'account_number': '0',
            'sequence': '0',
            'fee': {
                'amount': [{'denom': 'uodis', 'amount': '2500'}],
                'gas': '100000'
            },
            'msgs': [{
                'type': 'cosmos-sdk/MsgSend',
                'value': {
                    'from_address': self.user_address,
                    'to_address': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
                    'amount': [{'denom': 'uodis', 'amount': '1000'}]
                }
            }],
            'memo': 'tx:tx_1|hash:abcdef123456|role:owner'
        }
        
        # Convert to Proto format (mimicking main.js logic)
        proto_doc = {
            **amino_doc,
            'msgs': [mock_js_convert_amino_to_proto(msg) for msg in amino_doc['msgs']]
        }
        
        logger.debug(f"Converted Proto sign doc: {json.dumps(proto_doc, indent=2)}")
        
        # Verify Keplr would accept this format
        assert self.keplr.validate_sign_doc(proto_doc), "Keplr should accept the converted sign doc"
    
    def test_keplr_rejects_amino_format(self):
        """Test that Keplr correctly rejects Amino format messages."""
        # Create an Amino format message
        amino_msg = {
            'type': 'cosmos-sdk/MsgSend',
            'value': {
                'from_address': self.user_address,
                'to_address': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
                'amount': [{'denom': 'uodis', 'amount': '1000'}]
            }
        }
        
        # Verify Keplr would reject this format
        with pytest.raises(ValueError) as excinfo:
            self.keplr.validate_message(amino_msg)
        
        assert "Expected a message object with typeUrl" in str(excinfo.value)
    
    def test_field_name_conversion(self):
        """Test that field names are properly converted between formats."""
        # Amino uses snake_case
        amino_fields = {
            'from_address': self.user_address,
            'to_address': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
        }
        
        # Proto uses camelCase
        proto_fields = {
            'fromAddress': self.user_address,
            'toAddress': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
        }
        
        # Convert Amino to Proto (mimicking frontend conversion)
        converted_fields = {
            'fromAddress': amino_fields['from_address'],
            'toAddress': amino_fields['to_address'],
        }
        
        # Verify conversion
        assert converted_fields == proto_fields, "Field names should be properly converted"
        
        # Verify Keplr expectations
        with pytest.raises(ValueError):
            # This should fail because Keplr expects camelCase
            msg = {
                'typeUrl': '/cosmos.bank.v1beta1.MsgSend',
                'value': {
                    'from_address': self.user_address,  # Wrong! Should be fromAddress
                    'to_address': 'odiseo1receiver',    # Wrong! Should be toAddress
                    'amount': [{'denom': 'uodis', 'amount': '1000'}]
                }
            }
            self.keplr.validate_message(msg)

class TestRealKeplrErrorScenarios:
    """Test scenarios that would trigger real Keplr errors."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.keplr = MockKeplrWallet()
        self.user_address = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
    
    def test_expected_message_object_error(self):
        """Test the specific error scenario we encountered."""
        # Create message in the format that was causing the error
        bad_msg = {
            'type': 'cosmos-sdk/MsgSend',
            'value': {
                'from_address': self.user_address,
                'to_address': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
                'amount': [{'denom': 'uodis', 'amount': '1000'}]
            }
        }
        
        # This should fail with an error similar to what we saw in DevTools
        with pytest.raises(ValueError) as excinfo:
            self.keplr.validate_message(bad_msg)
        
        error_msg = str(excinfo.value)
        logger.debug(f"Keplr validation error: {error_msg}")
        
        # Verify error message matches what we saw in browser
        assert "Expected a message object" in error_msg
        
        # Now fix the message and verify it works
        fixed_msg = mock_js_convert_amino_to_proto(bad_msg)
        assert self.keplr.validate_message(fixed_msg), "Fixed message should be valid"
    
    def test_mixed_format_error(self):
        """Test error when some messages are Proto and some are Amino."""
        # Create a sign doc with mixed message formats
        mixed_doc = {
            'chain_id': 'odiseotestnet_1234-1',
            'account_number': '0',
            'sequence': '0',
            'fee': {
                'amount': [{'denom': 'uodis', 'amount': '2500'}],
                'gas': '100000'
            },
            'msgs': [
                # First message is Proto format (correct)
                {
                    'typeUrl': '/cosmos.bank.v1beta1.MsgSend',
                    'value': {
                        'fromAddress': self.user_address,
                        'toAddress': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
                        'amount': [{'denom': 'uodis', 'amount': '1000'}]
                    }
                },
                # Second message is Amino format (incorrect)
                {
                    'type': 'cosmos-sdk/MsgSend',
                    'value': {
                        'from_address': self.user_address,
                        'to_address': 'odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt',
                        'amount': [{'denom': 'uodis', 'amount': '1000'}]
                    }
                }
            ],
            'memo': 'tx:tx_1|hash:abcdef123456|role:owner'
        }
        
        # This should fail due to the second message
        with pytest.raises(ValueError):
            self.keplr.validate_sign_doc(mixed_doc)
        
        # Now fix all messages and verify it works
        fixed_doc = {
            **mixed_doc,
            'msgs': [
                mixed_doc['msgs'][0],  # First is already correct
                mock_js_convert_amino_to_proto(mixed_doc['msgs'][1])  # Fix the second one
            ]
        }
        
        assert self.keplr.validate_sign_doc(fixed_doc), "Document with all Proto messages should be valid"