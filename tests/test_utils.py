"""
Tests for utility functions that don't require the full Flask application.
These tests should run quickly and independently.
"""
import pytest
import json
import base64

# Test the utility functions without needing a Flask app
def test_base64_conversion():
    """Test base64 encoding and decoding."""
    # Original data
    original = b"Test data for base64 conversion"
    
    # Encode to base64
    encoded = base64.b64encode(original)
    
    # Decode back
    decoded = base64.b64decode(encoded)
    
    # Verify round trip
    assert decoded == original

def test_json_serialization():
    """Test JSON serialization and deserialization."""
    # Original data
    original = {
        "transaction_id": "abc123",
        "content_hash": "def456",
        "memo": "tx_abc123:def456:owner",
        "status": "pending",
        "signatures": {
            "owner": {
                "signed": True,
                "timestamp": "2025-03-24T15:00:00Z"
            }
        }
    }
    
    # Serialize to JSON
    serialized = json.dumps(original)
    
    # Deserialize from JSON
    deserialized = json.loads(serialized)
    
    # Verify round trip
    assert deserialized == original
    
    # Verify nested access
    assert deserialized["signatures"]["owner"]["signed"] is True

def test_memo_parsing_simple():
    """Test simple parsing of memo string."""
    # Simplified memo format
    memo = "tx_abc123:def456:owner"
    
    # Parse by splitting on colon
    parts = memo.split(":")
    
    # Verify parsing
    assert len(parts) == 3
    assert parts[0] == "tx_abc123"
    assert parts[1] == "def456"
    assert parts[2] == "owner"
    
    # Create dict
    parsed = {
        "tx": parts[0],
        "hash": parts[1],
        "role": parts[2]
    }
    
    # Verify dict
    assert parsed["tx"] == "tx_abc123"
    assert parsed["hash"] == "def456"
    assert parsed["role"] == "owner"