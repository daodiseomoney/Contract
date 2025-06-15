from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.crypto.address import Address
import logging
import requests


class AccountService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Define multiple endpoints with proper protocols for fallback
        self.endpoints = [
            "rest+https://odiseo.test.api.nodeshub.online",  # REST API endpoint first
            "http+https://odiseo.test.rpc.nodeshub.online",  # HTTP endpoint as fallback
            "grpc+https://odiseo.test.rpc.nodeshub.online:443",  # gRPC as last resort
        ]

        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url=self.endpoints[0],  # Start with REST endpoint
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis",
        )
        self.logger.debug(
            f"Initializing AccountService with network config: {self.network}"
        )

        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """Initialize client with fallback support"""
        last_error = None
        for endpoint in self.endpoints:
            try:
                self.network.url = endpoint
                self.logger.info(f"Attempting to connect to endpoint: {endpoint}")

                # Test endpoint accessibility before creating client
                base_url = (
                    endpoint.replace("rest+", "")
                    .replace("http+", "")
                    .replace("grpc+", "")
                )
                try:
                    response = requests.get(base_url, timeout=5)
                    self.logger.debug(
                        f"Endpoint {base_url} test response: {response.status_code}"
                    )
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Failed to test endpoint {base_url}: {str(e)}")
                    continue

                self.client = LedgerClient(self.network)
                self.logger.info(f"Successfully connected to endpoint: {endpoint}")
                return

            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Failed to connect to endpoint {endpoint}: {str(e)}"
                )
                continue

        if not self.client:
            error_msg = f"Failed to connect to any available endpoints. Last error: {str(last_error)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg)

    def get_account_data(self, address: str) -> dict:
        """Get account number and sequence for an address"""
        try:
            self.logger.info(f"Fetching account data for address: {address}")

            # Validate address format
            if not address.startswith("odiseo1"):
                self.logger.error(f"Invalid address format: {address}")
                raise ValueError("Invalid address format. Must start with 'odiseo1'")

            # Create Address object
            try:
                addr = Address(address)
                self.logger.debug(f"Created Address object: {addr}")
            except Exception as e:
                self.logger.error(f"Failed to create Address object: {str(e)}")
                raise ValueError(f"Invalid address format: {str(e)}")

            # Query account data with retry logic
            max_retries = 3
            last_error = None

            for attempt in range(max_retries):
                try:
                    # Get raw account data
                    account = self.client.query_account(addr)
                    self.logger.debug(f"Raw account data type: {type(account)}")
                    self.logger.debug(
                        f"Raw account data: {account.__dict__ if hasattr(account, '__dict__') else account}"
                    )

                    # Extract account data based on CosmPy 0.9.0 structure
                    if hasattr(account, "sequence"):
                        # New CosmPy structure
                        result = {
                            "account_number": str(
                                getattr(account, "account_number", "0")
                            ),
                            "sequence": str(account.sequence),
                            "address": address,
                        }
                    elif hasattr(account, "base_vesting_account"):
                        # Handle vesting account structure
                        base_account = account.base_vesting_account.base_account
                        result = {
                            "account_number": str(
                                getattr(base_account, "account_number", "0")
                            ),
                            "sequence": str(getattr(base_account, "sequence", "0")),
                            "address": address,
                        }
                    else:
                        # Handle other account types
                        self.logger.debug("Account attributes:", vars(account))
                        result = {
                            "account_number": "0",  # Default values if not found
                            "sequence": "0",
                            "address": address,
                        }

                    self.logger.info(f"Successfully retrieved account data: {result}")
                    return result

                except Exception as e:
                    last_error = e
                    if "403" in str(e) or "401" in str(e):
                        self.logger.warning(
                            f"Authentication error on attempt {attempt + 1}, trying next endpoint"
                        )
                        try:
                            self.initialize_client()
                            continue
                        except Exception as reinit_error:
                            self.logger.error(
                                f"Failed to reinitialize client: {str(reinit_error)}"
                            )
                    else:
                        self.logger.error(
                            f"Error querying account on attempt {attempt + 1}: {str(e)}"
                        )

                    if attempt == max_retries - 1:
                        raise ValueError(
                            f"Failed to get account data after {max_retries} attempts: {str(last_error)}"
                        )

        except ValueError as ve:
            self.logger.error(f"Account data error: {str(ve)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting account data: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)
