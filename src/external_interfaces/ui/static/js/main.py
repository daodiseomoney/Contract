"""
Python module representation of main.js for testing purposes.
This simulates the JavaScript functions and objects from the main.js file.
"""
import json

# Mock Keplr wallet integration functions
async def convert_amino_to_proto(msg):
    """
    Convert Amino message format to Proto format.
    This is a Python simulation of the JavaScript function.
    
    Args:
        msg (dict): Message in Amino format
    
    Returns:
        dict: Message in Proto format
    """
    if msg.get("type") == "cosmos-sdk/MsgSend":
        # Convert MsgSend from Amino to Proto format
        return {
            "@type": "/cosmos.bank.v1beta1.MsgSend",
            "from_address": msg["value"]["from_address"],
            "to_address": msg["value"]["to_address"],
            "amount": msg["value"]["amount"],
        }
    
    # For other message types
    return msg

# Mock fetch API for tests
async def fetch(url, options=None):
    """Mock fetch implementation for tests"""
    response = {
        "ok": True,
        "status": 200,
        "json": lambda: {"result": "success", "data": {"test": "value"}}
    }
    return response

def mock_js_convert_amino_to_proto(msg):
    """Non-async version for tests"""
    if msg.get("type") == "cosmos-sdk/MsgSend":
        return {
            "@type": "/cosmos.bank.v1beta1.MsgSend", 
            "fromAddress": msg["value"]["from_address"],
            "toAddress": msg["value"]["to_address"],
            "amount": msg["value"]["amount"]
        }
    return msg

def parse_memo_data(memo):
    """Parse the transaction memo to extract data"""
    parts = memo.split('|')
    result = {}
    
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            result[key] = value
    
    return result

class TransactionHelper:
    """Helper class for transaction related functions"""
    
    @staticmethod
    def create_sign_doc(account_info, tx_data):
        """Create a sign doc for Keplr"""
        return {
            "chain_id": "odiseotestnet_1234-1",
            "account_number": account_info.get("account_number", "0"),
            "sequence": account_info.get("sequence", "0"),
            "fee": {"amount": [{"denom": "uodis", "amount": "2500"}], "gas": "100000"},
            "msgs": [
                {
                    "type": "cosmos-sdk/MsgSend",
                    "value": {
                        "from_address": account_info.get("address", ""),
                        "to_address": "odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt",
                        "amount": [{"denom": "uodis", "amount": "1000"}],
                    },
                }
            ],
            "memo": f"tx:{tx_data.get('tx_id', '')}|hash:{tx_data.get('content_hash', '')}|role:{tx_data.get('role', 'user')}",
        }