from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.crypto.address import Address
import logging

class AccountService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.network = NetworkConfig(
            chain_id="odiseotestnet_1234-1",
            url="grpc+https://odiseo.test.rpc.nodeshub.online",
            fee_minimum_gas_price=0.025,
            fee_denomination="uodis",
            staking_denomination="uodis"
        )
        self.logger.debug(f"Initializing AccountService with network config: {self.network}")

        try:
            self.client = LedgerClient(self.network)
            self.logger.info("LedgerClient initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LedgerClient: {str(e)}")
            raise

    def get_account_data(self, address: str) -> dict:
        """Get account number and sequence for an address"""
        try:
            self.logger.info(f"Fetching account data for address: {address}")

            # Create Address object
            addr = Address(address)
            self.logger.debug(f"Created Address object: {addr}")

            # Query account data
            account_data = self.client.query_account(addr)
            self.logger.debug(f"Raw account data response: {account_data}")

            if not account_data:
                self.logger.error("No account data found")
                raise ValueError("No account data found")

            result = {
                "account_number": str(account_data.account_number),
                "sequence": str(account_data.sequence),
                "address": address
            }

            self.logger.info(f"Successfully retrieved account data: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to get account data: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to get account data: {str(e)}")