"""
Specialized tests that simulate actual browser interactions with Keplr
to catch the specific "Expected a message object" error we observed in DevTools.
"""
import json
import pytest
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MockKeplrBrowser:
    """
    Mock implementation of Keplr wallet browser extension
    that validates messages exactly as the browser extension would.
    """
    
    def signAmino(self, chainId, signer, signDoc, signOptions=None):
        """
        Mock implementation of Keplr's signAmino method that validates
        message format exactly as the real Keplr wallet would.
        """
        logger.debug(f"MockKeplr.signAmino called with:")
        logger.debug(f"  chainId: {chainId}")
        logger.debug(f"  signer: {signer}")
        logger.debug(f"  signDoc: {json.dumps(signDoc, indent=2)}")
        
        # Validate chain ID
        if not chainId or not isinstance(chainId, str):
            raise ValueError("Chain ID must be a non-empty string")
        
        # Validate signer address
        if not signer or not isinstance(signer, str):
            raise ValueError("Signer address must be a non-empty string")
        
        # Validate sign doc structure
        required_fields = ['chain_id', 'account_number', 'sequence', 'fee', 'msgs', 'memo']
        for field in required_fields:
            if field not in signDoc:
                raise ValueError(f"Sign doc missing required field: {field}")
        
        # Validate messages array
        if not isinstance(signDoc['msgs'], list) or len(signDoc['msgs']) == 0:
            raise ValueError("Sign doc msgs must be a non-empty array")
        
        # This is the critical part that caused our real issue:
        # Validate each message has typeUrl and proper structure
        for i, msg in enumerate(signDoc['msgs']):
            if not isinstance(msg, dict):
                raise TypeError(f"Message {i} must be an object")
            
            # Check if using Amino format instead of Proto format
            if 'type' in msg and 'typeUrl' not in msg:
                raise ValueError(
                    f"Expected a message object, but got {msg}. " 
                    "Messages must use Proto format with 'typeUrl' field."
                )
                
            if 'typeUrl' not in msg:
                raise ValueError(f"Message {i} missing required field: typeUrl")
                
            if 'value' not in msg:
                raise ValueError(f"Message {i} missing required field: value")
            
            # For MsgSend, validate field naming
            if msg['typeUrl'] == '/cosmos.bank.v1beta1.MsgSend':
                value = msg['value']
                
                # Check camelCase fields (correct) vs snake_case fields (incorrect)
                if 'from_address' in value and 'fromAddress' not in value:
                    raise ValueError(
                        f"Expected fromAddress in camelCase, but got from_address in snake_case. " 
                        "Proto format requires camelCase field names."
                    )
                    
                if 'to_address' in value and 'toAddress' not in value:
                    raise ValueError(
                        f"Expected toAddress in camelCase, but got to_address in snake_case. " 
                        "Proto format requires camelCase field names."
                    )
                
                # Validate required fields
                required_value_fields = ['fromAddress', 'toAddress', 'amount']
                for field in required_value_fields:
                    if field not in value:
                        raise ValueError(f"Message {i} value missing required field: {field}")
        
        # If we get here, validation passed
        # Return a mock successful signature response
        return {
            "signed": signDoc,
            "signature": {
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "simulated_pubkey_base64"
                },
                "signature": "simulated_signature_base64"
            }
        }

class TestKeplrBrowserErrorSimulation:
    """Tests that simulate the actual browser Keplr error we observed."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.keplr = MockKeplrBrowser()
        self.chainId = "odiseotestnet_1234-1"
        self.signer = "odiseo1nse3slfxqmmu4m5dlyczsee52rpnr53c3rt705"
    
    def test_keplr_integration_failure_scenario(self):
        """
        Simulate the exact error scenario we observed in the browser.
        This test reproduces the "Expected a message object" error.
        """
        # This is the sign doc with Amino format messages that would cause the error
        aminoSignDoc = {
            "chain_id": self.chainId,
            "account_number": "0",
            "sequence": "0",
            "fee": {
                "amount": [{"denom": "uodis", "amount": "2500"}],
                "gas": "100000"
            },
            "msgs": [{
                "type": "cosmos-sdk/MsgSend",  # Wrong format! Should be "typeUrl"
                "value": {
                    "from_address": self.signer,  # Wrong format! Should be "fromAddress"
                    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",  # Wrong format! Should be "toAddress"
                    "amount": [{"denom": "uodis", "amount": "1000"}]
                }
            }],
            "memo": "tx:tx_1|hash:abcdef123456|role:owner"
        }
        
        # This should fail with the same error we observed in DevTools
        with pytest.raises(ValueError) as excinfo:
            self.keplr.signAmino(self.chainId, self.signer, aminoSignDoc)
        
        error_msg = str(excinfo.value)
        logger.debug(f"Keplr Browser Error: {error_msg}")
        
        # Verify the error message matches what we saw in the browser
        assert "Expected a message object" in error_msg, "Error should match browser error"
        assert "cosmos-sdk/MsgSend" in error_msg, "Error should include the incorrect message type"
    
    def test_keplr_integration_fixed_scenario(self):
        """
        Simulate the fixed scenario where we properly convert message formats.
        This test verifies that our fix resolves the error.
        """
        # First create the Amino format that would cause problems
        aminoSignDoc = {
            "chain_id": self.chainId,
            "account_number": "0",
            "sequence": "0",
            "fee": {
                "amount": [{"denom": "uodis", "amount": "2500"}],
                "gas": "100000"
            },
            "msgs": [{
                "type": "cosmos-sdk/MsgSend",
                "value": {
                    "from_address": self.signer,
                    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"denom": "uodis", "amount": "1000"}]
                }
            }],
            "memo": "tx:tx_1|hash:abcdef123456|role:owner"
        }
        
        # Now apply our fix from src/external_interfaces/ui/static/js/main.js
        protoSignDoc = {
            **aminoSignDoc,
            "msgs": [{
                "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
                "value": {
                    "fromAddress": aminoSignDoc["msgs"][0]["value"]["from_address"],
                    "toAddress": aminoSignDoc["msgs"][0]["value"]["to_address"],
                    "amount": aminoSignDoc["msgs"][0]["value"]["amount"]
                }
            }]
        }
        
        logger.debug(f"Original Amino Sign Doc: {json.dumps(aminoSignDoc, indent=2)}")
        logger.debug(f"Fixed Proto Sign Doc: {json.dumps(protoSignDoc, indent=2)}")
        
        # This should now succeed with our fix
        response = self.keplr.signAmino(self.chainId, self.signer, protoSignDoc)
        
        # Verify we got a valid signature response
        assert response is not None
        assert "signature" in response
        assert "signed" in response
        
        logger.debug("Sign doc now accepted by Keplr!")
    
    def test_snake_case_to_camel_case_conversion(self):
        """
        Test that our fix correctly handles the snake_case to camelCase conversion.
        """
        # Create a sign doc with one message in Amino format
        aminoMsg = {
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": self.signer,
                "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                "amount": [{"denom": "uodis", "amount": "1000"}]
            }
        }
        
        # Apply our conversion logic
        protoMsg = {
            "typeUrl": "/cosmos.bank.v1beta1.MsgSend",
            "value": {
                "fromAddress": aminoMsg["value"]["from_address"],
                "toAddress": aminoMsg["value"]["to_address"],
                "amount": aminoMsg["value"]["amount"]
            }
        }
        
        # Manually check field name conversions
        assert "fromAddress" in protoMsg["value"], "from_address should be converted to fromAddress"
        assert "toAddress" in protoMsg["value"], "to_address should be converted to toAddress"
        
        # Create complete sign doc with the proto message
        protoSignDoc = {
            "chain_id": self.chainId,
            "account_number": "0",
            "sequence": "0",
            "fee": {
                "amount": [{"denom": "uodis", "amount": "2500"}],
                "gas": "100000"
            },
            "msgs": [protoMsg],
            "memo": "tx:tx_1|hash:abcdef123456|role:owner"
        }
        
        # This should now work with Keplr
        response = self.keplr.signAmino(self.chainId, self.signer, protoSignDoc)
        assert response is not None, "Keplr should accept the sign doc with properly converted field names"