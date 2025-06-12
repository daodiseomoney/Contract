# DAODISEO Clean Architecture

## Overview

DAODISEO is a cutting-edge blockchain real estate investment platform that follows Clean Architecture principles with strict separation of concerns and dependency rule enforcement. The system enables real estate tokenization through blockchain integration, AI-powered investment analysis, and BIM visualization capabilities.

## Clean Architecture Layers

### Layer Structure
```
External Interfaces
├── Flask Routes (Controllers)
├── Vue UI Components  
├── AI Agents (o3-mini)
└── Static Assets

Interface Adapters
├── Gateways (Blockchain, OpenAI)
├── Repositories (Data Access)
├── Presenters (Data Formatting)
└── Security Utils

Use Cases (Application Logic)
├── Dashboard Analytics
├── Investment Analysis
├── Orchestrator Control
└── Property Management

Entities (Core Domain)
├── Asset Models
├── Wallet Models
├── Validator Models
└── Transaction Models
```

## Component Flow

### Request Flow
```
Vue Component → Flask Route → Use Case → Entity
     ↑                                     ↓
Presenter ← Interface Adapter ← Repository ←
```

### AI Analysis Flow
```
User Action → Orchestrator Use Case → o3-mini Agent → Analysis Result
     ↑                                                        ↓
UI Component ← Presenter ← Interface Adapter ← Processing ←
```

## Directory Structure

```
src/
├── controllers/                 # External interface controllers
│   ├── rpc_controller.py       # Blockchain RPC endpoints
│   ├── orchestrator_controller.py # AI orchestration endpoints
│   └── bim_analysis_controller.py # Property analysis endpoints
│
├── services/                    # Application services
│   ├── rpc_service.py          # Blockchain data service
│   └── ai/
│       └── openai_agents_orchestrator.py # o3-mini integration
│
├── external_interfaces/         # UI and static assets
│   └── ui/
│       ├── templates/          # Flask templates
│       └── static/             # CSS, JS, assets
│
└── security_utils.py           # Security and rate limiting
```

Current Implementation Files:
- main.py - Application entry point
- src/controllers/ - API endpoint controllers
- src/services/ - Business logic services
- src/external_interfaces/ui/ - Frontend templates and assets

## Data Flow

### Blockchain Data
1. **RPC Gateway** → fetches from `testnet-rpc.daodiseo.chaintools.tech`
2. **Repository** → processes and caches data
3. **Use Case** → applies business logic
4. **Presenter** → formats for UI consumption
5. **Vue Component** → renders user interface

### AI Analysis
1. **User Trigger** → button click or data load
2. **Orchestrator Use Case** → coordinates analysis request
3. **AI Gateway** → sends prompt to o3-mini
4. **Analysis Presenter** → formats AI response
5. **Component Update** → displays inline results

## API Endpoints

### Core Endpoints
- `/api/rpc/validators` - Validator data from blockchain
- `/api/rpc/network-status` - Network health metrics
- `/api/rpc/transactions` - Transaction history

### Analysis Endpoints
- `/api/orchestrator/token-metrics` - Token analysis via o3-mini
- `/api/orchestrator/staking-metrics` - Staking analysis
- `/api/orchestrator/analyze-property` - Property investment analysis
- `/api/orchestrator/investment-analysis` - Investment opportunity analysis

## Dependency Rules

1. **Entities** have no dependencies on outer layers
2. **Use Cases** depend only on Entities
3. **Interface Adapters** depend on Use Cases and Entities
4. **External Interfaces** depend on all inner layers

## AI Integration

### o3-mini Orchestrator
Located in `src/external_interfaces/ai_agents/orchestrator.py`

**Capabilities:**
- Real-time blockchain data analysis
- Property investment scoring
- Market trend identification
- Risk assessment calculations

**Response Format:**
```json
{
  "analysis": "Detailed AI analysis text",
  "confidence": 0.85,
  "metrics": {
    "investment_score": "8.2/10",
    "roi_projection": "12.5% annually"
  }
}
```

## Security

- Rate limiting on all API endpoints
- CSRF protection for form submissions
- Secure headers applied to all responses
- Wallet address validation for transactions

## Performance

- Component-level lazy loading
- On-demand AI analysis (click-to-load)
- Efficient data caching in repositories
- Throttled API requests to prevent rate limits