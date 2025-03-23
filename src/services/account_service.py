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
            "rest+https://odiseo.test.api.nodeshub.online",      # REST API endpoint first
            "http+https://odiseo.test.rpc.nodeshub.online",      # HTTP endpoint as fallback
            "grpc+https://odiseo.test.rpc.nodeshub.online:443"   # gRPC as last resort
        ]

        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url=self.endpoints[0],  # Start with REST endpoint
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.logger.debug(f"Initializing AccountService with network config: {self.network}")

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
                base_url = endpoint.replace('rest+', '').replace('http+', '').replace('grpc+', '')
                try:
                    response = requests.get(base_url, timeout=5)
                    self.logger.debug(f"Endpoint {base_url} test response: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Failed to test endpoint {base_url}: {str(e)}")
                    continue

                self.client = LedgerClient(self.network)

                # Verify client works by querying chain ID
                try:
                    addr = Address("odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705")
                    self.client.query_account(addr)
                    self.logger.info(f"Successfully connected to endpoint: {endpoint}")
                    return
                except Exception as e:
                    if "not found" in str(e).lower():  # This is ok - just means account doesn't exist
                        self.logger.info(f"Successfully connected to endpoint: {endpoint}")
                        return
                    last_error = e
                    self.logger.warning(f"Client test failed for endpoint {endpoint}: {str(e)}")
                    continue

            except Exception as e:
                last_error = e
                self.logger.warning(f"Failed to connect to endpoint {endpoint}: {str(e)}")
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
            if not address.startswith('odiseo1'):
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
                    account_data = self.client.query_account(addr)
                    self.logger.debug(f"Raw account data response: {account_data}")

                    if not account_data:
                        self.logger.error("No account data found")
                        raise ValueError("No account data found for the address")

                    result = {
                        "account_number": str(account_data.account_number),
                        "sequence": str(account_data.sequence),
                        "address": address
                    }

                    self.logger.info(f"Successfully retrieved account data: {result}")
                    return result

                except Exception as e:
                    last_error = e
                    if "403" in str(e) or "401" in str(e):
                        self.logger.warning(f"Authentication error on attempt {attempt + 1}, trying to reinitialize client")
                        try:
                            self.initialize_client()
                            continue
                        except Exception as reinit_error:
                            self.logger.error(f"Failed to reinitialize client: {str(reinit_error)}")
                    else:
                        self.logger.error(f"Error querying account on attempt {attempt + 1}: {str(e)}")

                    if attempt == max_retries - 1:
                        raise ValueError(f"Failed to get account data after {max_retries} attempts: {str(last_error)}")

        except ValueError as ve:
            self.logger.error(f"Account data error: {str(ve)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting account data: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)