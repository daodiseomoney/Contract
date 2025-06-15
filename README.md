# DAODISEO - Real Estate Tokenization Platform

A sophisticated blockchain real estate investment platform that leverages cutting-edge technologies to simplify cryptocurrency workflows and enhance developer productivity.

## 🏗️ Clean Architecture

This project follows Clean Architecture principles with a 4-layer structure:

```
src/
├── layer0_entities/           # Enterprise Business Rules
├── layer1_use_cases/          # Application Business Rules  
├── layer2_interface_adapters/ # Controllers, Gateways, Presenters
└── layer3_external_interfaces/ # Frameworks & Drivers (Flask, Vue, DB)
```

## 🛠️ Technical Stack

**Backend:**
- Flask (Python web framework)
- Clean Architecture with 4-layer separation
- OpenAI API (AI integration with o3-mini)
- Cosmos SDK (Blockchain interaction)

**Frontend:**
- Vue.js 3 (Reactive UI framework)
- Pinia (State management)
- Chart.js (Data visualization)
- Tailwind CSS (Styling framework)
- Three.js (3D BIM rendering)

**Blockchain:**
- Cosmos-based Odiseo network
- Keplr wallet integration
- ODIS token economics
- IBC protocol support

## ✨ Features

**Dashboard:**
- Real-time Odiseo testnet metrics with Chart.js visualization
- Network health monitoring (50 validators, live block height)
- ODIS token distribution analytics
- 3D IFC property rendering with Three.js
- Mobile-inspired glassmorphism design

**Workflow:**
- Upload → Viewer → Broadcast → Asset Management
- Authentic 3D geometry processing
- Blockchain integration via Cosmos SDK
- Keplr wallet connectivity

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (DATABASE_URL environment variable)

### Local Development
```bash
# Clone repository
git clone https://github.com/your-org/daodiseo.git
cd daodiseo

# Python environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend build
cd src/layer3_external_interfaces/ui
npm install && npm run build
cd ../../..

# Run server
python main.py
```

### Environment Variables
```bash
SESSION_SECRET="your-secure-session-secret"
DATABASE_URL="postgresql://user:pass@localhost/dbname"
OPENAI_API_KEY="sk-..."  # Optional for AI features
```

## 🚀 Deployment

### Replit
1. Fork this repository on Replit
2. Set environment variables in Secrets tab
3. Run automatically via `.replit` configuration

### Docker
```bash
docker build -t daodiseo .
docker run -p 8080:8080 --env-file .env daodiseo
```

### Heroku
```bash
heroku create your-app-name
heroku config:set SESSION_SECRET=your-secret
git push heroku main
```
export DATABASE_URL="postgresql://..."  # Optional

# Install dependencies (already installed in Replit)
pip install -r requirements.txt

# Run development server
python main.py
```

The application will be available at `http://localhost:5000`

### Local Development

**Static Assets:** Vite build output is served from `src/layer3_external_interfaces/ui/static/` directory. Flask automatically serves JS bundles from `/static/js/main.js` and CSS from `/static/css/style.css`.

### Production Deployment
```bash
# Build frontend assets (if using separate build process)
npm run build

# Start production server
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🏛️ Architecture Overview

### Data Flow
```
UI Component → API Controller → Use Case → Entity → Gateway → External Service
     ↑                                                              ↓
Presenter ← Data Formatter ← Repository ← Service Implementation ←
```

### Layer Responsibilities

**Layer 0 - Entities (Enterprise Business Rules)**
- Core business models: Property, BIMModel, Stakeholder
- Domain logic and validation rules
- Framework-independent business rules

**Layer 1 - Use Cases (Application Business Rules)**  
- Application-specific business logic
- Orchestrates entity interactions
- Independent of UI and database concerns

**Layer 2 - Interface Adapters**
- Controllers: Handle HTTP requests/responses
- Gateways: Abstract external service interactions  
- Presenters: Format data for UI consumption

**Layer 3 - External Interfaces**
- Flask web framework and routing
- Vue.js frontend application
- Database connections and external APIs

## 🔑 Key Features

### Real Estate Tokenization
- Upload BIM/IFC files for property modeling
- AI-powered property valuation and analysis
- Smart contract generation and deployment
- Blockchain-based token creation

### Investment Management
- Real-time portfolio tracking
- Asset performance analytics
- ROI calculations and projections
- Risk assessment tools

### Blockchain Integration
- Live Odiseo testnet connectivity
- Network health monitoring
- Validator information display
- Transaction history tracking

## 🤖 AI Integration

DAODISEO uses OpenAI's API for:
- **Property Analysis**: Investment scoring and ROI projections
- **BIM Model Analysis**: Quality, sustainability, and complexity scoring
- **Market Intelligence**: Trend analysis and risk assessment
- **Portfolio Optimization**: Asset allocation recommendations

## 🌐 API Endpoints

### Blockchain
- `GET /api/network-health` - Network status and health
- `GET /api/odis-value` - ODIS token metrics
- `GET /api/validators` - Validator information

### Assets
- `GET /api/asset-metrics` - Portfolio metrics
- `GET /api/hot-asset` - Featured investment
- `GET /api/properties` - Property listings
- `POST /api/tokenize` - Tokenize property

### BIM
- `POST /api/bim/upload` - Upload BIM model
- `POST /api/bim/analyze/{id}` - Analyze model
- `GET /api/bim/models` - List models

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_entities.py
```

## 📁 Project Structure

```
src/
├── layer0_entities/
│   ├── bim_model.py          # BIM model domain logic
│   ├── property.py           # Property domain logic
│   ├── role.py              # User role management
│   └── stakeholder.py       # Stakeholder profiles
├── layer1_use_cases/
│   ├── get_network_status.py    # Network health use case
│   ├── get_token_metrics.py     # Token data use case  
│   ├── get_asset_metrics.py     # Portfolio metrics use case
│   ├── upload_bim_model.py      # BIM upload use case
│   ├── analyze_bim_model.py     # AI analysis use case
│   └── tokenize_property.py     # Property tokenization use case
├── layer2_interface_adapters/
│   ├── controllers/
│   │   ├── blockchain_controller.py # Blockchain API endpoints
│   │   ├── asset_controller.py      # Asset API endpoints
│   │   └── bim_controller.py        # BIM API endpoints
│   └── gateways/
│       ├── blockchain_gateway.py    # Blockchain service gateway
│       └── ai_gateway.py           # AI service gateway
├── layer3_external_interfaces/
│   └── ui/
│       ├── templates/base.html     # Vue.js SPA container
│       └── static/favicon.svg     # Application assets
└── security_utils.py              # Security utilities
```

## 🔒 Security Features

- CSRF protection for all state-changing operations
- Secure session management with HTTP-only cookies
- Security headers (XSS protection, content type options)
- Rate limiting for API endpoints
- Input sanitization and validation
- Wallet ownership verification

## 🌟 Development Guidelines

1. **Follow Clean Architecture**: Never allow dependencies to point inward
2. **Dependency Injection**: Use interfaces for external services
3. **Testing**: Write tests for all layers, especially business logic
4. **Error Handling**: Implement comprehensive error handling
5. **Documentation**: Keep README and ARCHITECTURE.md updated

## 🚀 Deployment

### Replit Deployment
This application is configured for Replit deployment with:
- Automatic dependency management
- Environment variable configuration
- Production-ready Gunicorn setup

### Manual Deployment
1. Set up environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations if using database
4. Start with: `gunicorn -w 4 -b 0.0.0.0:5000 main:app`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow Clean Architecture principles
4. Write tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Odiseo Testnet](https://testnet.daodiseo.chaintools.tech)
- [Keplr Wallet](https://www.keplr.app/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Vue.js Documentation](https://vuejs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)