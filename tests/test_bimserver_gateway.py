"""
Unit tests for the BIMserver Gateway functionality.
These tests verify the integration with BIMserver works correctly,
including proper error handling and fallback mechanisms.
"""

import pytest
import os
import io
import logging
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from src.gateways.bimserver_gateway import BIMServerGateway
from src.gateways.storage_factory import StorageFactory
from src.gateways.storage_gateway import LocalStorageGateway

# Sample test data
SAMPLE_PROJECT_ID = "12345"
SAMPLE_REVISION_ID = "67890"
SAMPLE_TOKEN = "test-token-123"
SAMPLE_USERNAME = "test@example.com"
SAMPLE_PASSWORD = "test-password"
SAMPLE_BASE_URL = "http://localhost:8080"


@pytest.fixture
def mock_successful_response():
    """Mock a successful response from BIMserver API."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"response": {"result": "test-result"}}
    return response


@pytest.fixture
def mock_error_response():
    """Mock an error response from BIMserver API."""
    response = MagicMock()
    response.status_code = 401  # Unauthorized
    response.json.return_value = {"response": {"error": "Authentication failed"}}
    return response


@pytest.fixture
def mock_bimserver_gateway():
    """Create a mock BIMserver gateway with authentication bypassed."""
    with patch(
        "src.gateways.bimserver_gateway.BIMServerGateway._authenticate"
    ) as mock_auth:
        gateway = BIMServerGateway(
            base_url=SAMPLE_BASE_URL, username=SAMPLE_USERNAME, password=SAMPLE_PASSWORD
        )
        gateway.token = SAMPLE_TOKEN
        gateway.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SAMPLE_TOKEN}",
        }
        return gateway


class TestBIMServerGateway:
    """Test suite for the BIMserver Gateway functionality."""

    def test_authentication_success(self, mock_successful_response):
        """Test successful authentication with BIMserver."""
        with patch("requests.post", return_value=mock_successful_response):
            gateway = BIMServerGateway(
                base_url=SAMPLE_BASE_URL,
                username=SAMPLE_USERNAME,
                password=SAMPLE_PASSWORD,
            )

            assert gateway.token == "test-result"
            assert gateway.headers["Authorization"] == f"Bearer test-result"

    def test_authentication_failure(self, mock_error_response):
        """Test authentication failure with BIMserver."""
        with patch("requests.post", return_value=mock_error_response):
            with pytest.raises(Exception) as excinfo:
                BIMServerGateway(
                    base_url=SAMPLE_BASE_URL,
                    username=SAMPLE_USERNAME,
                    password=SAMPLE_PASSWORD,
                )

            assert "Authentication failed" in str(
                excinfo.value
            ) or "Failed to authenticate with BIMserver" in str(excinfo.value)

    def test_api_call_success(self, mock_bimserver_gateway, mock_successful_response):
        """Test successful API call to BIMserver."""
        with patch("requests.post", return_value=mock_successful_response):
            result = mock_bimserver_gateway._call_api(
                interface="TestInterface",
                method="testMethod",
                parameters={"param1": "value1"},
            )

            assert result["result"] == "test-result"

    def test_create_project(self, mock_bimserver_gateway, mock_successful_response):
        """Test creating a project in BIMserver."""
        with patch("requests.post", return_value=mock_successful_response):
            project_id = mock_bimserver_gateway.create_project("Test Project")

            assert project_id == "test-result"

    def test_store_file(self, mock_bimserver_gateway, mock_successful_response):
        """Test storing a file in BIMserver."""
        with (
            patch("requests.post", return_value=mock_successful_response),
            patch.object(
                mock_bimserver_gateway,
                "_get_deserializer_by_name",
                return_value="ifc-deserializer",
            ),
        ):

            # Create a temporary test file
            test_file = io.BytesIO(b"test file content")
            test_file.name = "test.ifc"

            # Set up the mock responses for each API call in the sequence
            responses = [
                {"result": SAMPLE_PROJECT_ID},  # For creating the project
                {"result": "topic-123"},  # For initiating check-in
                {"result": "upload-success"},  # For uploading data
                {"result": SAMPLE_REVISION_ID},  # For finalizing check-in
            ]

            with patch.object(
                mock_bimserver_gateway, "_call_api", side_effect=responses
            ):
                revision_id = mock_bimserver_gateway.store_file(
                    file=test_file, project_name="Test Project"
                )

                assert revision_id == SAMPLE_REVISION_ID

    def test_retrieve_file(self, mock_bimserver_gateway, mock_successful_response):
        """Test retrieving a file from BIMserver."""
        with (
            patch("requests.post", return_value=mock_successful_response),
            patch.object(
                mock_bimserver_gateway,
                "_get_serializer_by_name",
                return_value="ifc-serializer",
            ),
            patch.object(
                mock_bimserver_gateway,
                "_decode_file_data",
                return_value=b"test file content",
            ),
        ):

            file_content = mock_bimserver_gateway.retrieve_file(
                revision_id=SAMPLE_REVISION_ID
            )

            assert file_content == b"test file content"

    def test_get_projects(self, mock_bimserver_gateway, mock_successful_response):
        """Test getting a list of projects from BIMserver."""
        with patch.object(
            mock_bimserver_gateway,
            "_call_api",
            return_value={"result": [{"id": "1", "name": "Project 1"}]},
        ):
            projects = mock_bimserver_gateway.get_projects()

            assert len(projects) == 1
            assert projects[0]["id"] == "1"
            assert projects[0]["name"] == "Project 1"

    def test_get_revisions(self, mock_bimserver_gateway, mock_successful_response):
        """Test getting a list of revisions for a project from BIMserver."""
        with patch.object(
            mock_bimserver_gateway,
            "_call_api",
            return_value={"result": [{"id": "1", "comment": "First revision"}]},
        ):
            revisions = mock_bimserver_gateway.get_revisions(SAMPLE_PROJECT_ID)

            assert len(revisions) == 1
            assert revisions[0]["id"] == "1"
            assert revisions[0]["comment"] == "First revision"

    def test_encoding_decoding(self, mock_bimserver_gateway):
        """Test file content encoding and decoding."""
        original_data = b"test binary data"
        encoded = mock_bimserver_gateway._encode_file_data(original_data)
        decoded = mock_bimserver_gateway._decode_file_data(encoded)

        assert decoded == original_data


class TestStorageFactory:
    """Test suite for the StorageFactory functionality."""

    def test_create_local_storage_when_bimserver_disabled(self):
        """Test creating a local storage gateway when BIMserver is disabled."""
        with patch("flask.current_app.config.get", return_value=False):
            storage = StorageFactory.create_storage_gateway()

            assert isinstance(storage, LocalStorageGateway)

    def test_create_bimserver_gateway_when_enabled(self):
        """Test creating a BIMserver gateway when BIMserver is enabled."""
        config_values = {
            "BIMSERVER_ENABLED": True,
            "BIMSERVER_URL": SAMPLE_BASE_URL,
            "BIMSERVER_USERNAME": SAMPLE_USERNAME,
            "BIMSERVER_PASSWORD": SAMPLE_PASSWORD,
        }

        with (
            patch(
                "flask.current_app.config.get",
                side_effect=lambda key, default=None: config_values.get(key, default),
            ),
            patch(
                "src.gateways.bimserver_gateway.BIMServerGateway.__init__",
                return_value=None,
            ),
            patch("src.gateways.bimserver_gateway.BIMServerGateway"),
        ):

            storage = StorageFactory.create_storage_gateway()

            assert isinstance(storage, BIMServerGateway)

    def test_fallback_to_local_storage_when_bimserver_fails(self):
        """Test fallback to local storage when BIMserver initialization fails."""
        config_values = {
            "BIMSERVER_ENABLED": True,
            "BIMSERVER_URL": SAMPLE_BASE_URL,
            "BIMSERVER_USERNAME": SAMPLE_USERNAME,
            "BIMSERVER_PASSWORD": SAMPLE_PASSWORD,
        }

        with (
            patch(
                "flask.current_app.config.get",
                side_effect=lambda key, default=None: config_values.get(key, default),
            ),
            patch(
                "src.gateways.bimserver_gateway.BIMServerGateway.__init__",
                side_effect=Exception("BIMserver connection failed"),
            ),
        ):

            storage = StorageFactory.create_storage_gateway()

            assert isinstance(storage, LocalStorageGateway)
