"""
Python module representation of transaction.js for testing purposes.
This simulates the JavaScript functions and objects from the transaction.js file.
"""
import json

# A mock window object for Keplr wallet integration tests
class MockWindow:
    """Mock browser window object with Keplr wallet instance."""
    
    def __init__(self):
        self.keplr = None


# Create a window instance for tests to access
window = MockWindow()

# Mock transaction functions
async def signAmino(chain_id, signer, sign_doc, sign_options=None):
    """
    Mock Keplr signAmino function.
    
    Args:
        chain_id (str): Chain ID
        signer (str): Signer address
        sign_doc (dict): Document to sign
        sign_options (dict): Options for signing
        
    Returns:
        dict: Mock signature response
    """
    if not window.keplr:
        raise Exception("Keplr not available")
    
    # Enable the chain first (if not already enabled)
    if not hasattr(window.keplr, "enabled_chains") or chain_id not in window.keplr.enabled_chains:
        await window.keplr.enable(chain_id)
    
    # Call the signAmino method of the Keplr wallet
    return await window.keplr.signAmino(chain_id, signer, sign_doc, sign_options)

def validateSignDoc(sign_doc):
    """
    Validate a sign doc format.
    
    Args:
        sign_doc (dict): Document to validate
        
    Returns:
        bool: True if valid
    """
    required_fields = [
        "chain_id", "account_number", "sequence",
        "fee", "msgs", "memo"
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in sign_doc:
            return False
    
    # Check messages format
    for msg in sign_doc["msgs"]:
        if "type" not in msg or "value" not in msg:
            return False
    
    return True

def parse_memo_format(memo):
    """
    Parse structured memo format like "tx:123|hash:abc|role:owner"
    
    Args:
        memo (str): Memo string to parse
        
    Returns:
        dict: Parsed memo fields
    """
    parts = memo.split('|')
    result = {}
    
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            result[key] = value
            
    return result

def create_amino_sign_doc(account_data, tx_id, content_hash, role="owner"):
    """
    Create a sign doc in Amino format for Keplr
    
    Args:
        account_data (dict): User account data
        tx_id (str): Transaction ID
        content_hash (str): Content hash
        role (str): Signer role
        
    Returns:
        dict: Amino format sign document
    """
    return {
        "chain_id": "odiseotestnet_1234-1",
        "account_number": account_data.get("account_number", "0"),
        "sequence": account_data.get("sequence", "0"),
        "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
        "msgs": [
            {
                "type": "cosmos-sdk/MsgSend",
                "value": {
                    "from_address": account_data.get("address", ""),
                    "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                    "amount": [{"denom": "uodis", "amount": "1000"}],
                },
            }
        ],
        "memo": f"tx:{tx_id}|hash:{content_hash}|role:{role}",
    }