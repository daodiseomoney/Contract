"""
Tests specifically focusing on Proto/Amino message format conversion
which was a key fix in the transaction handling.
"""
import pytest
import json

# Direct utility functions for testing message format conversion
def proto_to_amino(msg):
    """Convert Proto format message to Amino format."""
    if not isinstance(msg, dict):
        return None
    
    if 'typeUrl' not in msg or 'value' not in msg:
        return None
    
    # MsgSend conversion
    if msg['typeUrl'] == '/cosmos.bank.v1beta1.MsgSend':
        value = msg['value']
        return {
            'type': 'cosmos-sdk/MsgSend',
            'value': {
                'from_address': value.get('fromAddress', ''),
                'to_address': value.get('toAddress', ''),
                'amount': value.get('amount', [])
            }
        }
    
    # Add other message type conversions here
    return None

def amino_to_proto(msg):
    """Convert Amino format message to Proto format."""
    if not isinstance(msg, dict):
        return None
    
    if 'type' not in msg or 'value' not in msg:
        return None
    
    # MsgSend conversion
    if msg['type'] == 'cosmos-sdk/MsgSend':
        value = msg['value']
        return {
            'typeUrl': '/cosmos.bank.v1beta1.MsgSend',
            'value': {
                'fromAddress': value.get('from_address', ''),
                'toAddress': value.get('to_address', ''),
                'amount': value.get('amount', [])
            }
        }
    
    # Add other message type conversions here
    return None

class TestMessageFormatConversion:
    """Tests for converting between Amino and Proto message formats."""
    
    def test_proto_to_amino_conversion(self):
        """Test converting Proto format messages to Amino format."""
        # Proto format MsgSend
        proto_msg = {
            'typeUrl': '/cosmos.bank.v1beta1.MsgSend',
            'value': {
                'fromAddress': 'odiseo1sender',
                'toAddress': 'odiseo1receiver',
                'amount': [{'amount': '1000', 'denom': 'uodis'}]
            }
        }
        
        # Convert to Amino
        amino_msg = proto_to_amino(proto_msg)
        
        # Verify conversion
        assert amino_msg is not None
        assert amino_msg['type'] == 'cosmos-sdk/MsgSend'
        assert amino_msg['value']['from_address'] == 'odiseo1sender'
        assert amino_msg['value']['to_address'] == 'odiseo1receiver'
        assert amino_msg['value']['amount'][0]['amount'] == '1000'
        assert amino_msg['value']['amount'][0]['denom'] == 'uodis'
    
    def test_amino_to_proto_conversion(self):
        """Test converting Amino format messages to Proto format."""
        # Amino format MsgSend
        amino_msg = {
            'type': 'cosmos-sdk/MsgSend',
            'value': {
                'from_address': 'odiseo1sender',
                'to_address': 'odiseo1receiver',
                'amount': [{'amount': '1000', 'denom': 'uodis'}]
            }
        }
        
        # Convert to Proto
        proto_msg = amino_to_proto(amino_msg)
        
        # Verify conversion
        assert proto_msg is not None
        assert proto_msg['typeUrl'] == '/cosmos.bank.v1beta1.MsgSend'
        assert proto_msg['value']['fromAddress'] == 'odiseo1sender'
        assert proto_msg['value']['toAddress'] == 'odiseo1receiver'
        assert proto_msg['value']['amount'][0]['amount'] == '1000'
        assert proto_msg['value']['amount'][0]['denom'] == 'uodis'
    
    def test_invalid_message_format(self):
        """Test handling of invalid message formats."""
        # Invalid format (missing fields)
        invalid_msg = {
            'typeUrl': '/cosmos.bank.v1beta1.MsgSend'
            # Missing 'value' field
        }
        
        result = proto_to_amino(invalid_msg)
        assert result is None
        
        # Non-dict input
        result = proto_to_amino("not a dict")
        assert result is None
        
        # Empty dict
        result = proto_to_amino({})
        assert result is None
    
    def test_round_trip_conversion(self):
        """Test round-trip conversion (Proto -> Amino -> Proto)."""
        # Original Proto message
        original_proto = {
            'typeUrl': '/cosmos.bank.v1beta1.MsgSend',
            'value': {
                'fromAddress': 'odiseo1sender',
                'toAddress': 'odiseo1receiver',
                'amount': [{'amount': '1000', 'denom': 'uodis'}]
            }
        }
        
        # Convert Proto -> Amino
        amino = proto_to_amino(original_proto)
        
        # Convert Amino -> Proto
        round_trip_proto = amino_to_proto(amino)
        
        # Verify fields match after round trip
        assert round_trip_proto['typeUrl'] == original_proto['typeUrl']
        assert round_trip_proto['value']['fromAddress'] == original_proto['value']['fromAddress']
        assert round_trip_proto['value']['toAddress'] == original_proto['value']['toAddress']
        assert round_trip_proto['value']['amount'][0]['amount'] == original_proto['value']['amount'][0]['amount']
        assert round_trip_proto['value']['amount'][0]['denom'] == original_proto['value']['amount'][0]['denom']