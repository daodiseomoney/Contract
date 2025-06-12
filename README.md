<<<<<<< HEAD
# DAODISEO 🏗️

A cutting-edge blockchain real estate investment platform that transforms complex cryptocurrency interactions into intuitive, user-friendly experiences through advanced AI and blockchain technologies.

## 📋 What is DAODISEO

DAODISEO is a tokenized real estate investment platform built on Clean Architecture principles, integrating:

- **Real Estate Tokenization**: Convert physical properties into blockchain assets
- **AI-Powered Analysis**: o3-mini investment intelligence and risk assessment
- **Blockchain Integration**: Cosmos-based network with Keplr wallet support
- **BIM Visualization**: 3D property modeling and investment analytics
- **Responsive Dashboard**: Real-time network metrics and portfolio tracking

## 🔐 Wallet Connection

### Connecting Keplr Wallet

1. **Install Keplr Extension**: Download from [keplr.app](https://keplr.app)
2. **Network Configuration**: DAODISEO uses Odiseo testnet (`ithaca-1`)
3. **Connect**: Click "Connect Wallet" in the dashboard header
4. **Authorize**: Approve the connection in Keplr popup

**Testnet Details:**
- Chain ID: `ithaca-1`
- RPC Endpoint: `https://testnet-rpc.daodiseo.chaintools.tech`
- Token: ODIS

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/daodiseo/app.git
cd app

# Install dependencies
npm install
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_key"
export SESSION_SECRET="your_session_secret"

# Run development server
python main.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

```bash
# Build frontend assets
npm run build

# Start production server
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🧠 AI Integration

DAODISEO uses OpenAI's o3-mini model for:

- **Property Analysis**: Investment scoring and ROI projections
- **Market Intelligence**: Trend analysis and risk assessment
- **Portfolio Optimization**: Asset allocation recommendations
- **Network Analytics**: Blockchain performance insights

**AI Orchestrator Location**: `src/external_interfaces/ai_agents/orchestrator.py`

## 🌐 Network Integration

### Blockchain Endpoints

- **Network Status**: Real-time block height and health
- **Validators**: Active validator set and voting power
- **Transactions**: Transaction history and analytics
- **Staking**: Delegation and rewards tracking

### API Architecture

```
Frontend → Flask Routes → Use Cases → Blockchain Gateway
    ↑                                         ↓
Presenter ← Interface Adapter ← Repository ←
```

## 💼 Investment Features

### Property Management
- Upload BIM/IFC files for property modeling
- AI-powered property valuation
- Tokenization workflow and smart contracts
- Investment opportunity analysis

### Portfolio Dashboard
- Real-time asset performance tracking
- Staking rewards and delegation management
- Network analytics and validator insights
- Risk assessment and recommendations

## 🛠️ Technical Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- OpenAI API (AI integration)
- Cosmos SDK (Blockchain interaction)

**Frontend:**
- Vue.js (Reactive UI framework)
- Chart.js (Data visualization)
- Tailwind CSS (Styling framework)
- Three.js (3D BIM rendering)

**Blockchain:**
- Cosmos-based network
- Keplr wallet integration
- ODIS token economics
- IBC protocol support

## 📁 Project Structure

```
src/
├── entities/             # Core business models
├── use_cases/            # Application logic
├── interface_adapters/   # Gateways and repositories
└── external_interfaces/  # Controllers and UI
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...           # OpenAI API key for AI features
SESSION_SECRET=random_string    # Flask session secret
DATABASE_URL=postgresql://...   # Database connection

# Optional
FLASK_ENV=development          # Development mode
DEBUG=True                     # Enable debug logging
```

### Network Configuration

The platform connects to the Odiseo testnet by default. For mainnet deployment, update the RPC endpoints in the configuration files.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Join our Discord community
- Contact the development team

---

Built with ❤️ by the DAODISEO team
=======
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
export CHAIN_ID=ithaca-1
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

For BIMserver API integration details, see [docs/api/bimserver_api.html](docs/api/bimserver_api.html).

## Testing

Run the test suite to validate the application:

```bash
python -m pytest
```

## License

Copyright © 2025 Real Estate Tokenization Platform. All rights reserved.
>>>>>>> fb24633dab07b7e0a60328f87ead6e6396c2f113
