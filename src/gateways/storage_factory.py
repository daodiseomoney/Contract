"""
Factory for creating storage gateways based on configuration.
Supports both local storage and BIMserver storage.
"""

import os
import logging
from typing import Union
from flask import current_app
from src.gateways.storage_gateway import LocalStorageGateway
from src.gateways.bimserver_gateway import BIMServerGateway

# Set up logging
logger = logging.getLogger(__name__)


class StorageFactory:
    """Factory for creating storage gateway instances based on configuration."""

    @staticmethod
    def create_storage_gateway() -> Union[LocalStorageGateway, BIMServerGateway]:
        """
        Create and return the appropriate storage gateway based on configuration.

        Returns:
            Either a LocalStorageGateway or BIMServerGateway instance
        """
        # Check if BIMserver is enabled in configuration
        bimserver_enabled = current_app.config.get("BIMSERVER_ENABLED", False)

        if bimserver_enabled:
            logger.info("Using BIMServer storage gateway")
            # Get BIMserver configuration
            bimserver_url = current_app.config.get("BIMSERVER_URL")
            bimserver_username = current_app.config.get("BIMSERVER_USERNAME")
            bimserver_password = current_app.config.get("BIMSERVER_PASSWORD")

            # Validate configuration
            if not all([bimserver_url, bimserver_username, bimserver_password]):
                logger.warning(
                    "Incomplete BIMserver configuration. Falling back to local storage."
                )
                return LocalStorageGateway()

            try:
                # Try to create BIMServer gateway
                return BIMServerGateway(
                    base_url=bimserver_url,
                    username=bimserver_username,
                    password=bimserver_password,
                )
            except Exception as e:
                logger.error(f"Failed to initialize BIMServer gateway: {str(e)}")
                logger.warning("Falling back to local storage gateway")
                return LocalStorageGateway()
        else:
            logger.info("Using local storage gateway")
            return LocalStorageGateway()
