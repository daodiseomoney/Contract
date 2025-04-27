"""
Pytest fixtures shared across multiple test files.
This file configures the test environment and provides common fixtures.
"""

import pytest
import os
import json
import base64
import logging
from io import BytesIO
from unittest.mock import patch, MagicMock

# Configure logging for test debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Create a separate test Flask app instead of importing the main one
# This prevents the tests from interfering with the running application
@pytest.fixture
def test_client():
    """Create a test Flask app instance for isolated testing."""
    from flask import Flask, jsonify, request

    # Create a test Flask app
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True
    test_app.config["SERVER_NAME"] = "localhost"

    # Simple routes to test with
    @test_app.route("/")
    def index():
        return "<html><body><h1>Test App</h1></body></html>"

    @test_app.route("/api/contracts")
    def contracts():
        # Mock response
        return jsonify(
            [
                {
                    "transaction_id": "tx_123456",
                    "content_hash": "hash_abcdef",
                    "status": "pending",
                    "created_at": "2025-03-24T15:00:00Z",
                }
            ]
        )

    # Return the test client
    with test_app.test_client() as client:
        yield client


# Mock data fixtures
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
        "sequence": "6789",
    }


@pytest.fixture
def mock_keplr_signature():
    """Mock signature response similar to what Keplr wallet would return."""
    return {
        "signed": {
            "account_number": "12345",
            "chain_id": "odiseotestnet_1234-1",
            "fee": {"amount": [{"amount": "2500", "denom": "uodis"}], "gas": "100000"},
            "memo": "tx_123:content_hash_456:owner",
            "msgs": [
                {
                    "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                    "value": {
                        "fromAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        "amount": [{"amount": "1000", "denom": "uodis"}],
                    },
                }
            ],
            "sequence": "6789",
        },
        "signature": {
            "pub_key": {
                "type": "tendermint/PubKeySecp256k1",
                "value": "A4VPT8ybcJHimQK9HeIOt1YxV1J+e/Z+Q9UkodyDjT9M",
            },
            "signature": "ZW5jb2RlZC1zaWduYXR1cmUtdmFsdWUtZm9yLXRlc3Rpbmc=",
        },
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
        "raw_log": "transaction successful",
    }


# Service mocks
@pytest.fixture
def mock_transaction_service():
    """Mock transaction service for testing."""
    # Create a mock for the transaction service
    mock_service = MagicMock()

    # Configure the mock methods
    mock_service.create_sign_doc.return_value = {
        "account_number": "12345",
        "chain_id": "odiseotestnet_1234-1",
        "fee": {"amount": [{"amount": "2500", "denom": "uodis"}], "gas": "100000"},
        "memo": "tx_123:content_hash_456:owner",
        "msgs": [
            {
                "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                "value": {
                    "fromAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "toAddress": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"amount": "1000", "denom": "uodis"}],
                },
            }
        ],
        "sequence": "6789",
    }

    mock_service.broadcast_transaction.return_value = {
        "success": True,
        "txhash": "ABCDEF1234567890ABCDEF1234567890ABCDEF12",
        "height": "42",
        "code": 0,
        "gas_used": "80000",
        "raw_log": "transaction successful",
    }

    return mock_service


@pytest.fixture
def mock_multisig_gateway():
    """Mock MultiSig blockchain gateway for testing."""
    # Create a mock for the MultiSigBlockchainGateway
    mock_gateway = MagicMock()

    # Configure the mock methods
    mock_gateway.create_transaction.return_value = "tx_123456"

    mock_gateway.sign_transaction.return_value = True

    mock_gateway.get_transaction_status.return_value = {
        "transaction_id": "tx_123456",
        "content_hash": "hash_abcdef",
        "status": "signed",
        "signatures": {"owner": True, "contributor": False, "validator": False},
    }

    mock_gateway.get_active_contracts.return_value = [
        {
            "transaction_id": "tx_123456",
            "content_hash": "hash_abcdef",
            "status": "pending",
            "created_at": "2025-03-24T15:00:00Z",
        }
    ]

    return mock_gateway


# Utility for base64 encoding/decoding
def base64_encode(data):
    """Base64 encode bytes data."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")


def base64_decode(data):
    """Base64 decode string to bytes."""
    return base64.b64decode(data)


# Register a marker for slow tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
