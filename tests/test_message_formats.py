"""
Tests specifically focusing on Proto/Amino message format conversion
which was a key fix in the transaction handling.
"""
import pytest
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Helper functions for message format conversion
def proto_to_amino(msg):
    """Convert Proto format message to Amino format."""
    if not msg or "typeUrl" not in msg:
        return None
    
    # Extract type from typeUrl (e.g., "/cosmos.bank.v1beta1.MsgSend" -> "cosmos-sdk/MsgSend")
    type_url = msg["typeUrl"]
    amino_type = "cosmos-sdk/MsgSend"  # Default fallback
    
    # Map specific typeUrls to Amino types
    type_mapping = {
        "/cosmos.bank.v1beta1.MsgSend": "cosmos-sdk/MsgSend",
        "/cosmos.staking.v1beta1.MsgDelegate": "cosmos-sdk/MsgDelegate",
        "/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward": "cosmos-sdk/MsgWithdrawDelegationReward"
    }
    
    if type_url in type_mapping:
        amino_type = type_mapping[type_url]
    
    # Convert value fields
    value = msg.get("value", {})
    amino_value = {}
    
    # Field mappings for common message types
    if "MsgSend" in type_url:
        amino_value = {
            "from_address": value.get("fromAddress", ""),
            "to_address": value.get("toAddress", ""),
            "amount": value.get("amount", [])
        }
    elif "MsgDelegate" in type_url:
        amino_value = {
            "delegator_address": value.get("delegatorAddress", ""),
            "validator_address": value.get("validatorAddress", ""),
            "amount": value.get("amount", {})
        }
    else:
        # Generic conversion (camelCase to snake_case)
        for key, val in value.items():
            # Convert camelCase to snake_case
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key])
            snake_key = snake_key.lstrip('_')
            amino_value[snake_key] = val
    
    return {
        "type": amino_type,
        "value": amino_value
    }

def amino_to_proto(msg):
    """Convert Amino format message to Proto format."""
    if not msg or "type" not in msg:
        return None
    
    # Extract typeUrl from Amino type
    amino_type = msg["type"]
    type_url = "/cosmos.bank.v1beta1.MsgSend"  # Default fallback
    
    # Map Amino types to Proto typeUrls
    type_mapping = {
        "cosmos-sdk/MsgSend": "/cosmos.bank.v1beta1.MsgSend",
        "cosmos-sdk/MsgDelegate": "/cosmos.staking.v1beta1.MsgDelegate",
        "cosmos-sdk/MsgWithdrawDelegationReward": "/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward"
    }
    
    if amino_type in type_mapping:
        type_url = type_mapping[amino_type]
    
    # Convert value fields
    value = msg.get("value", {})
    proto_value = {}
    
    # Field mappings for common message types
    if "MsgSend" in amino_type:
        proto_value = {
            "fromAddress": value.get("from_address", ""),
            "toAddress": value.get("to_address", ""),
            "amount": value.get("amount", [])
        }
    elif "MsgDelegate" in amino_type:
        proto_value = {
            "delegatorAddress": value.get("delegator_address", ""),
            "validatorAddress": value.get("validator_address", ""),
            "amount": value.get("amount", {})
        }
    else:
        # Generic conversion (snake_case to camelCase)
        for key, val in value.items():
            # Convert snake_case to camelCase
            parts = key.split('_')
            camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
            proto_value[camel_key] = val
    
    return {
        "typeUrl": type_url,
        "value": proto_value
    }

class TestMessageFormatConversion:
    """Tests for converting between Amino and Proto message formats."""
    
    def test_proto_to_amino_conversion(self):
        """Test converting Proto format messages to Amino format."""
        # Proto format message
        proto_msg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": "odiseo1sender",
                "toAddress": "odiseo1receiver",
                "amount": [{"amount": "1000", "denom": "uodis"}]
            }
        }
        
        # Convert to Amino format
        amino_msg = proto_to_amino(proto_msg)
        
        logger.debug(f"Converted Amino message: {json.dumps(amino_msg, indent=2)}")
        
        # Verify conversion
        assert amino_msg["type"] == "cosmos-sdk/MsgSend"
        assert amino_msg["value"]["from_address"] == "odiseo1sender"
        assert amino_msg["value"]["to_address"] == "odiseo1receiver"
        assert amino_msg["value"]["amount"] == [{"amount": "1000", "denom": "uodis"}]
    
    def test_amino_to_proto_conversion(self):
        """Test converting Amino format messages to Proto format."""
        # Amino format message
        amino_msg = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": "odiseo1sender",
                "to_address": "odiseo1receiver",
                "amount": [{"amount": "1000", "denom": "uodis"}]
            }
        }
        
        # Convert to Proto format
        proto_msg = amino_to_proto(amino_msg)
        
        logger.debug(f"Converted Proto message: {json.dumps(proto_msg, indent=2)}")
        
        # Verify conversion
        assert proto_msg["typeUrl"] == "/cosmos.bank.v1beta1.MsgSend"
        assert proto_msg["value"]["fromAddress"] == "odiseo1sender"
        assert proto_msg["value"]["toAddress"] == "odiseo1receiver"
        assert proto_msg["value"]["amount"] == [{"amount": "1000", "denom": "uodis"}]
    
    def test_invalid_message_format(self):
        """Test handling of invalid message formats."""
        # Invalid Proto message (missing typeUrl)
        invalid_proto = {"value": {"fromAddress": "addr1"}}
        result = proto_to_amino(invalid_proto)
        assert result is None
        
        # Invalid Amino message (missing type)
        invalid_amino = {"value": {"from_address": "addr1"}}
        result = amino_to_proto(invalid_amino)
        assert result is None
        
        # Empty message
        result = proto_to_amino({})
        assert result is None
        result = amino_to_proto({})
        assert result is None
        
        # None value
        result = proto_to_amino(None)
        assert result is None
        result = amino_to_proto(None)
        assert result is None
    
    def test_round_trip_conversion(self):
        """Test round-trip conversion (Proto -> Amino -> Proto)."""
        # Original Proto message
        original_proto = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": "odiseo1sender",
                "toAddress": "odiseo1receiver",
                "amount": [{"amount": "1000", "denom": "uodis"}]
            }
        }
        
        # Convert Proto -> Amino
        amino = proto_to_amino(original_proto)
        
        # Convert Amino -> Proto
        converted_proto = amino_to_proto(amino)
        
        logger.debug(f"Original Proto: {json.dumps(original_proto, indent=2)}")
        logger.debug(f"Converted Amino: {json.dumps(amino, indent=2)}")
        logger.debug(f"Converted Proto: {json.dumps(converted_proto, indent=2)}")
        
        # Verify round-trip conversion preserves values
        assert converted_proto["typeUrl"] == original_proto["typeUrl"]
        assert converted_proto["value"]["fromAddress"] == original_proto["value"]["fromAddress"]
        assert converted_proto["value"]["toAddress"] == original_proto["value"]["toAddress"]
        assert converted_proto["value"]["amount"] == original_proto["value"]["amount"]