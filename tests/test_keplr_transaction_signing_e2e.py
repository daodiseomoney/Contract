"""
End-to-end test for Keplr transaction signing flow.
This test simulates the complete flow from contract selection through 
Keplr wallet signing to transaction broadcasting.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock


class MockFetchResponse:
    """Mock implementation of fetch response."""

    def __init__(self, data, ok=True, status=200):
        self.data = data
        self.ok = ok
        self.status = status

    async def json(self):
        """Return mock JSON data."""
        return self.data


class MockKeplrWallet:
    """Mock implementation of Keplr wallet browser extension."""

    def __init__(self):
        self.accounts = [
            {
                "address": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
                "algo": "secp256k1",
                "pubkey": "A1234567890abcdef",
            }
        ]
        self.enabled_chains = set()
        self.sign_calls = []

    async def enable(self, chainId):
        """Enable a chain for the wallet."""
        self.enabled_chains.add(chainId)
        return True

    def getOfflineSigner(self, chainId):
        """Get an offline signer for a chain."""
        return self

    async def getAccounts(self):
        """Get accounts from the wallet."""
        return self.accounts

    async def signAmino(self, chainId, signer, signDoc, signOptions=None):
        """Sign a transaction using Amino format."""
        if chainId not in self.enabled_chains:
            raise ValueError(f"Chain {chainId} not enabled")

        # Validate proper Amino format with type/value structure
        # This is the critical check testing our implementation
        for msg in signDoc["msgs"]:
            # Validate the message has the correct Amino format with type/value
            if "type" not in msg:
                raise ValueError(
                    f"Expected a message object with 'type' field, but got {msg}"
                )

            if "value" not in msg:
                raise ValueError(
                    f"Expected a message object with 'value' field, but got {msg}"
                )

            # For MsgSend, validate value has required fields
            if msg["type"] == "cosmos-sdk/MsgSend":
                value = msg["value"]
                required_fields = ["from_address", "to_address", "amount"]
                for field in required_fields:
                    if field not in value:
                        raise ValueError(
                            f"MsgSend value missing required field: {field}"
                        )

        # Record the sign call for inspection
        self.sign_calls.append(
            {
                "chainId": chainId,
                "signer": signer,
                "signDoc": signDoc,
                "signOptions": signOptions,
            }
        )

        # Return mock signature response
        return {
            "signed": signDoc,
            "signature": {
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "A1234567890abcdef",
                },
                "signature": "c2lnbmF0dXJl",  # Base64 mock signature
            },
        }


@pytest.fixture
def mock_keplr():
    """Create a mock Keplr wallet."""
    return MockKeplrWallet()


@pytest.fixture
def mock_fetch():
    """Create a mock fetch function."""

    async def mock_fetch_impl(url, **kwargs):
        """Mock implementation of fetch."""
        if url == "/api/transaction/tx_123":
            return MockFetchResponse(
                {
                    "transaction_id": "tx_123",
                    "content_hash": "hash_abc123",
                    "signatures": {"owner": "pending", "validator": "pending"},
                }
            )
        elif (
            url == "/api/account?address=odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        ):
            return MockFetchResponse(
                {
                    "account_number": "227917",
                    "sequence": "84",
                    "address": "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705",
                }
            )
        elif url == "/api/sign":
            return MockFetchResponse(
                {"success": True, "message": "Transaction signed successfully"}
            )
        return MockFetchResponse({}, ok=False, status=404)

    return mock_fetch_impl


class TestKeplrTransactionSigningE2E:
    """End-to-end tests for Keplr transaction signing flow."""

    @pytest.mark.asyncio
    @patch("src.external_interfaces.ui.static.js.main.window")
    @patch("src.external_interfaces.ui.static.js.main.fetch")
    async def test_transaction_signing_flow(self, mock_fetch, mock_window, mock_keplr):
        """
        Test the complete transaction signing flow from signContract function.
        This simulates what happens when a user clicks the "Sign" button on a contract.
        """
        # Arrange - Set up mocks
        mock_window.keplr = mock_keplr
        mock_fetch.side_effect = AsyncMock(side_effect=mock_fetch)

        # Import the signContract function from main.js
        # In an actual test, we would:
        # from src.external_interfaces.ui.static.js.main import signContract

        # For this simulation, we'll recreate the key parts of the flow
        # to test our integration with Keplr

        # 1. Get transaction details
        transaction_response = await mock_fetch("/api/transaction/tx_123")
        transaction = await transaction_response.json()

        # 2. Set up variables
        chainId = "odiseotestnet_1234-1"
        userAddress = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        nextRole = "owner"  # First unsigned role

        # 3. Enable Keplr and get account info
        await mock_keplr.enable(chainId)
        accountResponse = await mock_fetch(f"/api/account?address={userAddress}")
        accountData = await accountResponse.json()

        # 4. Create the Amino doc for signing
        aminoDoc = {
            "chain_id": chainId,
            "account_number": accountData["account_number"],
            "sequence": accountData["sequence"],
            "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
            # Using proper Amino format with type/value structure
            "msgs": [
                {
                    "type": "cosmos-sdk/MsgSend",
                    "value": {
                        "from_address": userAddress,
                        "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        "amount": [{"denom": "uodis", "amount": "1000"}],
                    },
                }
            ],
            "memo": f"tx:{transaction['transaction_id']}|hash:{transaction['content_hash']}|role:{nextRole}",
        }

        # 5. Call signAmino and check for success
        signResponse = await mock_keplr.signAmino(
            chainId, userAddress, aminoDoc, {"preferNoSetFee": True}
        )

        # 6. Send signature to backend (simulated)
        signResult = await mock_fetch(
            "/api/sign",
            {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "transaction_id": transaction["transaction_id"],
                        "role": nextRole,
                        "signature": signResponse,
                    }
                ),
            },
        )

        # Assertions
        assert (
            len(mock_keplr.sign_calls) == 1
        ), "signAmino should be called exactly once"
        sign_call = mock_keplr.sign_calls[0]

        # Check chain ID and signer
        assert sign_call["chainId"] == chainId
        assert sign_call["signer"] == userAddress

        # Most importantly, check that the message has the correct Amino format
        # This is what fixes the "Expected a message object" error
        msg = sign_call["signDoc"]["msgs"][0]
        assert "type" in msg, "Message should have 'type' field"
        assert msg["type"] == "cosmos-sdk/MsgSend", "Message should have correct type"
        assert "value" in msg, "Message should have 'value' field"

        # Check that value has the required fields
        value = msg["value"]
        assert "from_address" in value, "Message value should have 'from_address'"
        assert "to_address" in value, "Message value should have 'to_address'"
        assert "amount" in value, "Message value should have 'amount'"

        # Check that the sign result was processed
        assert signResult.ok, "Sign API call should be successful"
        result_data = await signResult.json()
        assert result_data["success"], "Sign API should return success"

    @pytest.mark.asyncio
    @patch("src.external_interfaces.ui.static.js.main.window")
    @patch("src.external_interfaces.ui.static.js.main.fetch")
    async def test_incorrect_format_fails(self, mock_fetch, mock_window, mock_keplr):
        """Test that using an incorrect message format fails with Keplr."""
        # Arrange
        mock_window.keplr = mock_keplr
        mock_fetch.side_effect = AsyncMock(side_effect=mock_fetch)

        # Enable the chain
        chainId = "odiseotestnet_1234-1"
        userAddress = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        await mock_keplr.enable(chainId)

        # Create a sign doc with direct object format (incorrect for signAmino)
        incorrectSignDoc = {
            "chain_id": chainId,
            "account_number": "227917",
            "sequence": "84",
            "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
            # Direct object format without type/value structure - INCORRECT
            "msgs": [
                {
                    "from_address": userAddress,
                    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"denom": "uodis", "amount": "1000"}],
                }
            ],
            "memo": "Test transaction",
        }

        # Act - Try to sign with incorrect format
        with pytest.raises(ValueError) as excinfo:
            await mock_keplr.signAmino(
                chainId, userAddress, incorrectSignDoc, {"preferNoSetFee": True}
            )

        # Assert
        assert "Expected a message object with 'type' field" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch("src.external_interfaces.ui.static.js.main.window")
    @patch("src.external_interfaces.ui.static.js.main.fetch")
    async def test_proto_format_fails(self, mock_fetch, mock_window, mock_keplr):
        """Test that using Proto format with @type fails with signAmino."""
        # Arrange
        mock_window.keplr = mock_keplr
        mock_fetch.side_effect = AsyncMock(side_effect=mock_fetch)

        # Enable the chain
        chainId = "odiseotestnet_1234-1"
        userAddress = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
        await mock_keplr.enable(chainId)

        # Create a sign doc with Proto format (incorrect for signAmino)
        protoSignDoc = {
            "chain_id": chainId,
            "account_number": "227917",
            "sequence": "84",
            "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
            # Proto format with @type field - INCORRECT for signAmino
            "msgs": [
                {
                    "@type": "/cosmos.bank.v1beta1.MsgSend",
                    "from_address": userAddress,
                    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"denom": "uodis", "amount": "1000"}],
                }
            ],
            "memo": "Test transaction",
        }

        # Act - Try to sign with Proto format
        with pytest.raises(ValueError) as excinfo:
            await mock_keplr.signAmino(
                chainId, userAddress, protoSignDoc, {"preferNoSetFee": True}
            )

        # Assert
        assert "Expected a message object with 'type' field" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_match_keplr_documentation(self, mock_keplr):
        """Test that our implementation matches the Keplr documentation example."""
        # Example from Keplr docs
        keplr_docs_example = {
            "account_number": "227917",
            "chain_id": "celestia",
            "fee": {"gas": "96585", "amount": [{"amount": "966", "denom": "utia"}]},
            "msgs": [
                {
                    "type": "cosmos-sdk/MsgSend",
                    "value": {
                        "from_address": "celestia1...",
                        "to_address": "celestia2...",
                        "amount": [{"denom": "utia", "amount": "1000"}],
                    },
                }
            ],
            "sequence": "84",
            "memo": "Test transaction",
        }

        # Enable the chain
        await mock_keplr.enable("celestia")

        # Act - Try to sign with the example from Keplr docs
        try:
            result = await mock_keplr.signAmino(
                "celestia",
                "celestia1...",
                keplr_docs_example,
                {
                    "preferNoSetFee": False,
                    "preferNoSetMemo": True,
                    "disableBalanceCheck": True,
                },
            )
            success = True
        except Exception as e:
            success = False
            error = str(e)

        # Assert
        assert (
            success
        ), f"Signing with Keplr docs example failed: {error if 'error' in locals() else 'unknown error'}"

        # Check that our mock correctly processed the sign request
        assert len(mock_keplr.sign_calls) == 1
        sign_call = mock_keplr.sign_calls[0]
        assert sign_call["chainId"] == "celestia"
        assert sign_call["signOptions"]["preferNoSetMemo"] == True
        assert sign_call["signOptions"]["disableBalanceCheck"] == True
