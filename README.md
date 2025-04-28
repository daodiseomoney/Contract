# Real Estate Tokenization Platform

A blockchain-powered real estate tokenization platform that enables secure and transparent property investment through advanced blockchain technology, with comprehensive transaction management and wallet integration.

## Key Technologies

- Flask web framework
- Cosmos blockchain (Odiseo testnet)
- CosmPy for blockchain interactions
- Keplr wallet browser integration
- BIMserver for advanced BIM file management
- PostgreSQL database

## Features

- Upload and validate Building Information Modeling (BIM) files
- Tokenize real estate properties on the blockchain
- Distribute budget allocations among stakeholders
- Multi-signature transaction processing
- Comprehensive transaction tracking
- Advanced error handling for blockchain transactions
- Interactive micro-rewards system with blockchain animations
- PingPub integration for validator transactions

## BIMserver Integration

The platform now features integration with [BIMserver](https://github.com/opensourceBIM/BIMserver), a dedicated Building Information Modeling server that provides:

- Project and revision management for BIM files
- Model-driven architecture (storing BIM as objects rather than files)
- Advanced querying and validation capabilities
- Format conversion between IFC, XML, and JSON
- Multi-user collaboration support

### Configuration

To enable BIMserver integration, set the following environment variables:

```bash
# Enable BIMserver integration
export BIMSERVER_ENABLED=True

# BIMserver connection settings
export BIMSERVER_URL=http://your-bimserver-instance:8080
export BIMSERVER_USERNAME=your_username
export BIMSERVER_PASSWORD=your_password
```

Without these variables, the system will automatically fall back to local file storage.

## PingPub Blockchain Integration

The platform integrates with the Odiseo blockchain network through PingPub API, enabling:

- Secure transaction broadcasting to the Odiseo blockchain
- Multi-signature validation through the validator network
- IFC file hash verification on-chain
- Transparent transaction history via block explorer

### Configuration

Configure the blockchain connection with these environment variables:

```bash
# PingPub API endpoint for Odiseo testnet
export PINGPUB_API_URL=https://pingpub-testnet.daodiseo.com/api/

# Blockchain network settings
export CHAIN_ID=odiseotestnet_1234-1
export CONTRACT_ADDRESS=odiseo1qg5ega6dykkxc307y25pecuv380qje7zp9qpxt
export VALIDATOR_POOL_ADDRESS=odiseo1k5vh4mzjncn4tnvan463whhrkkcsvjzgxm384q
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional, for BIMserver integration)
4. Start the application:

```bash
python main.py
```

## System Architecture

See [architecture.md](architecture.md) for a detailed overview of the system architecture.

## API Documentation

For BIMserver API integration details, see [bimserver_api.html](bimserver_api.html).

## Testing

Run the test suite to validate the application:

```bash
python -m pytest
```

## License

Copyright © 2025 Real Estate Tokenization Platform. All rights reserved.