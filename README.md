# Real Estate Tokenization Platform

The Real Estate Tokenization Platform is a blockchain-powered application that enables secure and transparent property investment through advanced blockchain technology, with comprehensive transaction management and Keplr wallet integration.

## Key Features

- Blockchain-based property tokenization using Cosmos SDK (Odiseo testnet)
- Multi-signature transaction management for real estate contracts
- Keplr wallet integration for transaction signing
- File upload and content hashing for property documentation
- Transaction status tracking and management

## Technical Stack

- **Backend**: Flask web framework
- **Blockchain**: Cosmos (Odiseo testnet)
- **SDK**: CosmPy for blockchain interactions
- **Wallet**: Keplr browser extension integration
- **Security**: Multi-signature wallet interactions

## Recent Fixes

### Keplr Wallet Integration Fix (March 24, 2025)

Fixed a critical issue with Keplr wallet transaction signing where messages weren't being properly formatted. The specific error was:

```
Expected a message object, but got {'type': 'cosmos-sdk/MsgSend', 'value': {...}}
```

The fix transforms messages from the nested Amino format to a flattened format that Keplr expects:

**Old Format (Amino):**
```json
{
  "type": "cosmos-sdk/MsgSend",
  "value": {
    "from_address": "odiseo1...",
    "to_address": "odiseo1...",
    "amount": [...]
  }
}
```

**New Format (Keplr-compatible):**
```json
{
  "@type": "/cosmos.bank.v1beta1.MsgSend",
  "from_address": "odiseo1...",
  "to_address": "odiseo1...",
  "amount": [...]
}
```

The fix has been implemented across the frontend JavaScript files that interact with Keplr wallet.

## Development

To run the application locally:

```bash
python main.py
```

The application will be available at http://localhost:5000
