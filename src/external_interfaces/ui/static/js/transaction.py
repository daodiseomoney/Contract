"""
Python module representation of transaction.js for testing purposes.
This simulates the JavaScript functions and objects from the transaction.js file.
"""

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
    
    return await window.keplr.signAmino(chain_id, signer, sign_doc, sign_options)

async def validateSignDoc(sign_doc):
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