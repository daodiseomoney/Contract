"""
BIMserver Gateway for integrating with BIMserver API.
Replaces the local storage approach with a model-driven architecture.
"""

import os
import requests
import logging
from typing import BinaryIO, Dict, List, Optional, cast
import json

# Set up logging
logger = logging.getLogger(__name__)


class BIMServerGateway:
    """
    Gateway for interacting with the BIMserver API.
    Handles authentication, project creation, file uploads, and retrievals.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize the BIMserver gateway with authentication credentials.

        Args:
            base_url: Base URL of the BIMserver instance (e.g., 'https://bimserver.example.com')
            username: BIMserver username
            password: BIMserver password
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = None
        self.headers = {"Content-Type": "application/json"}

        # Ensure we're authenticated
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate with the BIMserver and obtain a token.
        Raises exception if authentication fails.
        """
        try:
            endpoint = f"{self.base_url}/json"
            payload = {
                "request": {
                    "interface": "AuthInterface",
                    "method": "login",
                    "parameters": {
                        "username": self.username,
                        "password": self.password,
                    },
                }
            }

            response = requests.post(endpoint, json=payload)
            response.raise_for_status()

            result = response.json()
            if "response" in result and "result" in result["response"]:
                self.token = result["response"]["result"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                logger.info("Successfully authenticated with BIMserver")
            else:
                logger.error(f"Authentication failed: {result}")
                raise Exception("Failed to authenticate with BIMserver")

        except requests.RequestException as e:
            logger.error(f"Error connecting to BIMserver: {str(e)}")
            raise

    def _call_api(self, interface: str, method: str, parameters: Dict) -> Dict:
        """
        Make a call to the BIMserver JSON API.

        Args:
            interface: BIMserver interface name (e.g., 'ServiceInterface')
            method: Method name to call
            parameters: Parameters to pass to the method

        Returns:
            Response data from BIMserver
        """
        if not self.token:
            self._authenticate()

        endpoint = f"{self.base_url}/json"
        payload = {
            "request": {
                "interface": interface,
                "method": method,
                "parameters": parameters,
            }
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            result = response.json()
            if "response" in result:
                return result["response"]
            else:
                logger.error(f"API call failed: {result}")
                raise Exception(f"BIMserver API call to {interface}.{method} failed")

        except requests.RequestException as e:
            logger.error(f"Error calling BIMserver API: {str(e)}")
            raise

    def create_project(self, project_name: str, schema: str = "ifc2x3tc1") -> str:
        """
        Create a new project in BIMserver.

        Args:
            project_name: Name for the new project
            schema: Schema to use (e.g., 'ifc2x3tc1', 'ifc4')

        Returns:
            Project ID (poid) as a string
        """
        try:
            result = self._call_api(
                "ServiceInterface",
                "addProject",
                {"projectName": project_name, "schema": schema},
            )

            if "result" in result:
                project_id = result["result"]
                logger.info(f"Created project: {project_name} with ID: {project_id}")
                return project_id
            else:
                raise Exception("Failed to create project in BIMserver")

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

    def store_file(
        self,
        file: BinaryIO,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None,
    ) -> str:
        """
        Store BIM file in BIMserver and return revision ID.

        Args:
            file: File object to upload
            project_id: Optional project ID to upload to
            project_name: Optional project name (will create if project_id not provided)

        Returns:
            Revision ID (roid) as a string
        """
        try:
            # If project_id is not provided, create a new project or find existing
            if not project_id and project_name:
                # Try to find project by name first
                projects = self.get_projects()
                for project in projects:
                    if project["name"] == project_name:
                        project_id = project["id"]
                        break

                # If not found, create new project
                if not project_id:
                    project_id = self.create_project(project_name)
            elif not project_id:
                # Generate a project name from the filename if none provided
                filename = (
                    os.path.basename(file.name)
                    if hasattr(file, "name")
                    else "unnamed_project"
                )
                project_name = f"Project_{filename.split('.')[0]}"
                project_id = self.create_project(
                    project_name if project_name else "Default_Project"
                )

            # Read file content
            file_content = file.read()
            file.seek(0)  # Reset file pointer for potential reuse

            # Get the filename
            filename = (
                os.path.basename(file.name)
                if hasattr(file, "name")
                else "unnamed_file.ifc"
            )

            # Determine deserializer based on file extension
            extension = filename.split(".")[-1].lower()
            if extension == "ifc":
                deserializer = "ifc"
            elif extension == "dwg":
                deserializer = "dwg"  # Note: May need configuration in BIMserver
            else:
                deserializer = "ifc"  # Default to IFC

            # Make sure project_id is not None at this point
            if project_id is None:
                raise ValueError("project_id cannot be None when checking in a file")

            # First, checkin the file to get a topicId
            checkin_result = self._call_api(
                "ServiceInterface",
                "initiateCheckin",
                {
                    "poid": project_id,
                    "deserializerOid": self._get_deserializer_by_name(deserializer),
                },
            )

            if "result" not in checkin_result:
                raise Exception("Failed to initiate file check-in")

            topicId = checkin_result["result"]

            # Upload the file data
            upload_result = self._call_api(
                "ServiceInterface",
                "uploadData",
                {
                    "topicId": topicId,
                    "fileName": filename,
                    "data": self._encode_file_data(file_content),
                    "sync": True,
                },
            )

            # Finalize the checkin to get the revision ID
            finalize_result = self._call_api(
                "ServiceInterface", "finalizeCheckin", {"topicId": topicId}
            )

            if "result" in finalize_result:
                revision_id = finalize_result["result"]
                logger.info(f"Stored file: {filename} with revision ID: {revision_id}")
                return revision_id
            else:
                raise Exception("Failed to finalize file check-in")

        except Exception as e:
            logger.error(f"Error storing file: {str(e)}")
            raise

    def retrieve_file(self, revision_id: str, format: str = "ifc") -> bytes:
        """
        Retrieve file content from BIMserver.

        Args:
            revision_id: Revision ID (roid) to retrieve
            format: Output format (e.g., 'ifc', 'ifcxml', 'json')

        Returns:
            File content as bytes
        """
        try:
            # Get the serializer for the requested format
            serializer_id = self._get_serializer_by_name(format)

            # Download the file
            download_result = self._call_api(
                "ServiceInterface",
                "download",
                {"roid": revision_id, "serializerOid": serializer_id, "sync": True},
            )

            if "result" in download_result:
                # Decode base64 data or handle direct binary download
                file_data = self._decode_file_data(download_result["result"])
                return file_data
            else:
                raise Exception("Failed to download file from BIMserver")

        except Exception as e:
            logger.error(f"Error retrieving file: {str(e)}")
            raise

    def get_projects(self) -> List[Dict]:
        """
        Get all projects from BIMserver.

        Returns:
            List of project dictionaries
        """
        try:
            result = self._call_api(
                "ServiceInterface",
                "getAllProjects",
                {"onlyActive": True, "onlyTopLevel": False},
            )

            if "result" in result:
                return result["result"]
            else:
                raise Exception("Failed to get projects from BIMserver")

        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise

    def get_revisions(self, project_id: str) -> List[Dict]:
        """
        Get all revisions for a project.

        Args:
            project_id: Project ID (poid)

        Returns:
            List of revision dictionaries
        """
        try:
            result = self._call_api(
                "ServiceInterface", "getAllRevisionsOfProject", {"poid": project_id}
            )

            if "result" in result:
                return result["result"]
            else:
                raise Exception("Failed to get revisions from BIMserver")

        except Exception as e:
            logger.error(f"Error getting revisions: {str(e)}")
            raise

    def _get_deserializer_by_name(self, name: str) -> str:
        """Get the deserializer ID by name."""
        try:
            result = self._call_api(
                "PluginInterface", "getAllDeserializers", {"onlyEnabled": True}
            )

            if "result" in result:
                deserializers = result["result"]
                for deserializer in deserializers:
                    if deserializer["name"].lower() == name.lower():
                        return deserializer["oid"]

                raise Exception(f"Deserializer '{name}' not found")
            else:
                raise Exception("Failed to get deserializers from BIMserver")

        except Exception as e:
            logger.error(f"Error getting deserializer: {str(e)}")
            raise

    def _get_serializer_by_name(self, name: str) -> str:
        """Get the serializer ID by name."""
        try:
            result = self._call_api(
                "PluginInterface", "getAllSerializers", {"onlyEnabled": True}
            )

            if "result" in result:
                serializers = result["result"]
                for serializer in serializers:
                    if serializer["name"].lower() == name.lower():
                        return serializer["oid"]

                raise Exception(f"Serializer '{name}' not found")
            else:
                raise Exception("Failed to get serializers from BIMserver")

        except Exception as e:
            logger.error(f"Error getting serializer: {str(e)}")
            raise

    def _encode_file_data(self, data: bytes) -> str:
        """Encode binary data for BIMserver API (usually base64)."""
        import base64

        return base64.b64encode(data).decode("utf-8")

    def _decode_file_data(self, data: str) -> bytes:
        """Decode data from BIMserver API (usually from base64)."""
        import base64

        return base64.b64decode(data)
