"""
Tests for utility functions that don't require the full Flask application.
These tests should run quickly and independently.
"""
import pytest
import json
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_base64_conversion():
    """Test base64 encoding and decoding."""
    # Test data
    original_data = b"Test data for base64 conversion"
    
    # Encode
    encoded = base64.b64encode(original_data).decode('utf-8')
    logger.debug(f"Encoded data: {encoded}")
    
    # Decode
    decoded = base64.b64decode(encoded)
    logger.debug(f"Decoded data: {decoded}")
    
    # Verify
    assert decoded == original_data
    
    # Test with string
    string_data = "String data for base64 conversion"
    encoded_str = base64.b64encode(string_data.encode('utf-8')).decode('utf-8')
    decoded_str = base64.b64decode(encoded_str).decode('utf-8')
    assert decoded_str == string_data

def test_json_serialization():
    """Test JSON serialization and deserialization."""
    # Test data
    original_data = {
        "string": "test string",
        "number": 42,
        "float": 3.14159,
        "boolean": True,
        "array": [1, 2, 3, 4, 5],
        "object": {
            "nested": "value",
            "nested_array": [6, 7, 8]
        },
        "null": None
    }
    
    # Serialize
    serialized = json.dumps(original_data)
    logger.debug(f"Serialized data: {serialized}")
    
    # Deserialize
    deserialized = json.loads(serialized)
    logger.debug(f"Deserialized data: {deserialized}")
    
    # Verify
    assert deserialized == original_data
    assert deserialized["string"] == original_data["string"]
    assert deserialized["number"] == original_data["number"]
    assert deserialized["float"] == original_data["float"]
    assert deserialized["boolean"] == original_data["boolean"]
    assert deserialized["array"] == original_data["array"]
    assert deserialized["object"]["nested"] == original_data["object"]["nested"]
    assert deserialized["object"]["nested_array"] == original_data["object"]["nested_array"]
    assert deserialized["null"] == original_data["null"]

def test_memo_parsing_simple():
    """Test simple parsing of memo string."""
    # New format memo
    memo = "tx_123456:hash_abcdef:owner"
    
    # Parse
    parts = memo.split(":")
    
    # Verify
    assert len(parts) == 3
    assert parts[0] == "tx_123456"
    assert parts[1] == "hash_abcdef"
    assert parts[2] == "owner"
    
    # Legacy format
    legacy_memo = "tx:tx_123456|hash:hash_abcdef|role:owner"
    
    # Parse legacy format
    result = {}
    pairs = legacy_memo.split("|")
    for pair in pairs:
        if ":" in pair:
            key, value = pair.split(":", 1)
            result[key] = value
    
    # Verify
    assert result["tx"] == "tx_123456"
    assert result["hash"] == "hash_abcdef"
    assert result["role"] == "owner"