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
            "grpc+https://odiseo.test.rpc.nodeshub.online:443",  # Primary gRPC endpoint
            "rest+https://odiseo.test.api.nodeshub.online",      # REST API endpoint as fallback
        ]

        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url=self.endpoints[0],  # Start with gRPC endpoint
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.logger.debug(f"Initializing AccountService with network config: {self.network}")

        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """Initialize client with fallback support"""
        for endpoint in self.endpoints:
            try:
                self.network.url = endpoint
                self.logger.info(f"Attempting to connect to endpoint: {endpoint}")

                # Test endpoint accessibility before creating client
                base_url = endpoint.replace('grpc+', '').replace('rest+', '')
                if base_url.startswith('https://'):
                    response = requests.get(base_url, timeout=5)
                    self.logger.debug(f"Endpoint {base_url} test response: {response.status_code}")
                    if response.status_code not in [200, 404]:  # 404 is ok as we're just testing connectivity
                        self.logger.warning(f"Endpoint {base_url} returned status code {response.status_code}")
                        continue

                self.client = LedgerClient(self.network)
                # Test the client with a basic query
                try:
                    # Query bank params as a basic connectivity test
                    tx = self.client.query_broadcast_tx("0" * 64)  # Query a dummy tx to test connection
                    self.logger.info(f"Successfully connected to endpoint: {endpoint}")
                    return
                except Exception as e:
                    self.logger.warning(f"Client test failed for endpoint {endpoint}: {str(e)}")
                    continue

            except Exception as e:
                self.logger.warning(f"Failed to connect to endpoint {endpoint}: {str(e)}")
                continue

        if not self.client:
            error_msg = "Failed to connect to any available endpoints"
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

            # Query account data
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
                error_msg = str(e)
                if "403" in error_msg or "401" in error_msg:
                    # Try to reinitialize with a different endpoint
                    self.logger.warning("Authentication error, attempting to reinitialize with different endpoint")
                    try:
                        self.initialize_client()
                        return self.get_account_data(address)
                    except Exception as reinit_error:
                        error_msg = f"Failed to reconnect to alternate endpoints: {str(reinit_error)}"
                elif "Connection refused" in error_msg:
                    error_msg = "Could not connect to blockchain network. Please verify the network is accessible."
                else:
                    error_msg = f"Failed to get account data: {error_msg}"

                self.logger.error(error_msg, exc_info=True)
                raise ValueError(error_msg)

        except ValueError as ve:
            self.logger.error(f"Account data error: {str(ve)}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting account data: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)