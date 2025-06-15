# DAODISEO Clean Architecture Documentation

## Overview

DAODISEO implements Clean Architecture as defined by Robert C. Martin, organizing code into four distinct layers with clear dependency rules and boundaries.

## The Clean Architecture Diagram

```
    🌐 External Interfaces (Layer 3)
    ┌─────────────────────────────────────┐
    │  Flask • Vue.js • Database • APIs  │
    │  ┌───────────────────────────────┐  │
    │  │ Interface Adapters (Layer 2) │  │
    │  │  Controllers • Gateways •    │  │
    │  │  Presenters • Repositories   │  │
    │  │  ┌─────────────────────────┐ │  │
    │  │  │ Use Cases (Layer 1)    │ │  │
    │  │  │  Application Business  │ │  │
    │  │  │  Rules                 │ │  │
    │  │  │  ┌─────────────────┐   │ │  │
    │  │  │  │ Entities (L0)  │   │ │  │
    │  │  │  │ Enterprise     │   │ │  │
    │  │  │  │ Business Rules │   │ │  │
    │  │  │  └─────────────────┘   │ │  │
    │  │  └─────────────────────────┘ │  │
    │  └───────────────────────────────┘  │
    └─────────────────────────────────────┘
```

## Dependency Rule

**Critical Rule**: Dependencies can only point inward. Inner layers cannot know about outer layers.

- ✅ **Allowed**: Layer 3 → Layer 2 → Layer 1 → Layer 0
- ❌ **Forbidden**: Layer 0 → Layer 1, Layer 1 → Layer 2, etc.

## Layer Breakdown

### Layer 0: Entities (Enterprise Business Rules)

**Purpose**: Core business models and enterprise-wide rules that would exist regardless of the application.

**Location**: `src/layer0_entities/`

**Contents**:
- `bim_model.py` - BIM model domain logic with elements, analysis, and validation
- `property.py` - Real estate property models with tokenization rules
- `stakeholder.py` - Stakeholder profiles and permissions
- `role.py` - User role management and authorization
- `dashboard_aggregate.py` - Dashboard metrics aggregation and business rules

**Key Characteristics**:
- No dependencies on other layers
- Pure business logic
- Framework-independent
- Highest level of abstraction

**Example**:
```python
class RealEstateProperty:
    def __init__(self, name: str, property_type: PropertyType, location: Location):
        self.name = name
        self.property_type = property_type
        self.location = location
        
    def can_be_tokenized(self) -> bool:
        # Business rule: Property must have minimum value
        return self.financials.current_valuation >= 100000
```

### Layer 1: Use Cases (Application Business Rules)

**Purpose**: Application-specific business rules. Contains the business logic that is specific to this application.

**Location**: `src/layer1_use_cases/`

**Contents**:
- `get_network_status.py` - Blockchain network health monitoring
- `get_token_metrics.py` - ODIS token data processing
- `get_asset_metrics.py` - Portfolio analytics and calculations
- `upload_bim_model.py` - BIM file processing workflow
- `analyze_bim_model.py` - AI-powered model analysis
- `tokenize_property.py` - Property tokenization orchestration
- `dashboard_metrics_use_case.py` - Dashboard data aggregation and processing
- `validate_compliance.py` - Property compliance validation workflows

**Key Characteristics**:
- Orchestrates entities
- Contains application-specific business logic
- Uses interfaces to interact with external services
- Independent of UI, database, and frameworks

**Example**:
```python
class GetNetworkStatusUseCase:
    def __init__(self, blockchain_gateway: BlockchainGatewayInterface):
        self.blockchain_gateway = blockchain_gateway
    
    def execute(self) -> Dict[str, Any]:
        # Application business logic
        network_data = self.blockchain_gateway.get_network_health()
        status = self._interpret_network_status(network_data)
        return self._format_network_response(status, network_data)
```

### Layer 2: Interface Adapters

**Purpose**: Adapts data between use cases and external interfaces. Converts data from the format convenient for use cases and entities, to the format convenient for external services.

**Location**: `src/layer2_interface_adapters/`

#### Controllers
**Location**: `src/layer2_interface_adapters/controllers/`

- `blockchain_controller.py` - HTTP endpoints for blockchain operations
- `asset_controller.py` - HTTP endpoints for asset management
- `bim_controller.py` - HTTP endpoints for BIM operations
- `dashboard_controller.py` - HTTP endpoints for dashboard metrics
- `account_controller.py` - HTTP endpoints for user account management
- `contract_controller.py` - HTTP endpoints for smart contract operations
- `orchestrator_controller.py` - HTTP endpoints for workflow orchestration
- `consolidated_ai_controller.py` - HTTP endpoints for AI service integrations
- `consolidated_blockchain_controller.py` - HTTP endpoints for unified blockchain operations
- `consolidated_property_controller.py` - HTTP endpoints for property management

**Responsibility**: Handle HTTP requests, validate input, call use cases, return responses.

```python
@bp.route('/network-health', methods=['GET'])
def get_network_health():
    try:
        result = network_status_use_case.execute()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

#### Gateways
**Location**: `src/layer2_interface_adapters/gateways/`

- `blockchain_gateway.py` - Abstracts blockchain RPC calls
- `ai_gateway.py` - Abstracts OpenAI API interactions
- `consolidated_blockchain_gateway.py` - Unified blockchain service gateway
- `storage_gateway.py` - File storage abstraction layer
- `bimserver_gateway.py` - BIM server integration gateway
- `llm_gateway.py` - Large language model service gateway
- `ifc/ifc_gateway.py` - IFC file processing gateway
- `ifc/ifc_parser.py` - IFC file parsing utilities
- `storage_factory.py` - Storage service factory pattern

**Responsibility**: Implement interfaces defined by use cases, hide external service details.

```python
class BlockchainGateway(BlockchainGatewayInterface):
    def get_network_health(self) -> Dict[str, Any]:
        response = requests.get(f"{self.rpc_endpoint}/status")
        return self._process_network_response(response.json())
```

#### Presenters
**Location**: `src/layer2_interface_adapters/presenters/`

**Responsibility**: Format data for specific UI requirements.

### Layer 3: External Interfaces (Frameworks & Drivers)

**Purpose**: Outermost layer consisting of frameworks and tools such as the database, web framework, etc.

**Location**: `src/layer3_external_interfaces/`

#### Web Framework
- Flask application setup (`main.py`)
- Route registration and middleware
- Security headers and CSRF protection

#### UI Components  
**Location**: `src/layer3_external_interfaces/ui/`

- `templates/base.html` - Vue.js SPA container
- `App.vue` - Main Vue application component
- `components/Dashboard.vue` - Dashboard interface component
- `components/Upload.vue` - File upload interface
- `components/Viewer.vue` - 3D model viewer component
- `components/Broadcast.vue` - Blockchain broadcast interface
- `components/Contracts.vue` - Smart contract management
- Vue.js routing and state management
- Tailwind CSS styling with glassmorphism effects
- Vite build tooling and hot module replacement

#### External Services
- PostgreSQL database connections
- Odiseo testnet blockchain RPC endpoints  
- OpenAI API integration for BIM analysis
- File storage systems for BIM/IFC uploads
- Configuration management (`config.py`)
- Device-specific interfaces (`devices/`)
- Web service abstractions (`web/services/`)

## Data Flow Examples

### 1. Dashboard Metrics Retrieval
```
GET /api/metrics
    ↓
DashboardController.get_metrics()
    ↓
DashboardMetricsUseCase.execute()
    ↓
ConsolidatedBlockchainGateway.get_network_health()
    ↓
External Odiseo testnet RPC API
    ↓
Response aggregated with other metrics
    ↓
JSON response to Vue.js Dashboard component
```

### 2. BIM Model Upload and Analysis
```
POST /api/bim/upload (multipart IFC file)
    ↓
BIMController.upload_bim_model()
    ↓
UploadBIMModelUseCase.execute()
    ↓
BIMModel entity validation
    ↓
StorageGateway.save_file()
    ↓
IFCGateway.parse_ifc_file()
    ↓
AIGateway.analyze_bim_model()
    ↓
Response with model metadata and AI insights
```

### 3. Property Tokenization Workflow
```
Vue.js Broadcast Component
    ↓
POST /api/contracts/tokenize
    ↓
ConsolidatedPropertyController.tokenize_property()
    ↓
TokenizePropertyUseCase.execute()
    ↓
RealEstateProperty.can_be_tokenized()
    ↓
ValidateComplianceUseCase.execute()
    ↓
ConsolidatedBlockchainGateway.deploy_contract()
    ↓
Odiseo testnet smart contract deployment
    ↓
Transaction hash and contract address returned
```

## Interface Definitions

### Use Case Interfaces
```python
# Gateways implement these interfaces
class ConsolidatedBlockchainGatewayInterface(ABC):
    @abstractmethod
    def get_network_health(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    def get_token_metrics(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    def deploy_smart_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]: pass

class AIGatewayInterface(ABC):
    @abstractmethod
    def analyze_bim_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]: pass
    
    @abstractmethod
    def generate_property_insights(self, property_data: Dict[str, Any]) -> Dict[str, Any]: pass

class StorageGatewayInterface(ABC):
    @abstractmethod
    def save_file(self, file_data: bytes, filename: str) -> str: pass
    
    @abstractmethod
    def get_file(self, file_id: str) -> bytes: pass
```

### Dependency Injection
Use cases receive their dependencies through constructor injection:

```python
class GetNetworkStatusUseCase:
    def __init__(self, blockchain_gateway: BlockchainGatewayInterface):
        self.blockchain_gateway = blockchain_gateway
```

## Testing Strategy

### Layer-Specific Testing

**Layer 0 (Entities)**:
- Unit tests for business logic
- Validation rule testing
- No external dependencies

```python
def test_property_tokenization_validation():
    property = RealEstateProperty(...)
    assert property.can_be_tokenized() == True
```

**Layer 1 (Use Cases)**:
- Mock external dependencies (gateways)
- Test business logic flows
- Integration between entities

```python
def test_get_network_status_use_case():
    mock_gateway = Mock(spec=BlockchainGatewayInterface)
    use_case = GetNetworkStatusUseCase(mock_gateway)
    result = use_case.execute()
    assert result['network_healthy'] == True
```

**Layer 2 (Interface Adapters)**:
- Test controllers with mock use cases
- Test gateways with mock external services
- HTTP response format validation

**Layer 3 (External Interfaces)**:
- End-to-end testing
- Frontend component testing
- API integration tests

## Clean Architecture Benefits

### 1. **Independence**
- **Framework Independence**: Business logic doesn't depend on Flask, Vue.js, or any framework
- **Database Independence**: Can switch from PostgreSQL to MongoDB without changing business logic
- **UI Independence**: Business logic is separate from Vue.js components

### 2. **Testability**
- Business logic can be tested without UI, database, or external services
- Each layer can be tested in isolation
- Mock implementations for external dependencies

### 3. **Flexibility**
- Easy to add new interfaces (mobile app, CLI)
- Switch external services without affecting business logic
- Modify UI without touching business rules

### 4. **Maintainability**
- Clear separation of concerns
- Changes in one layer don't affect others
- Easy to understand and modify

## Common Patterns

### 1. **Dependency Inversion**
```python
# Use case depends on interface, not implementation
class AnalyzeBIMModelUseCase:
    def __init__(self, ai_gateway: AIGatewayInterface):
        self.ai_gateway = ai_gateway  # Interface, not concrete class
```

### 2. **Data Transfer Objects (DTOs)**
```python
# Simple data structures for crossing boundaries
@dataclass
class PropertyTokenizationRequest:
    property_id: str
    token_supply: int
    initial_price: float
```

### 3. **Repository Pattern**
```python
class PropertyRepositoryInterface(ABC):
    @abstractmethod
    def save(self, property: RealEstateProperty) -> str: pass
    
    @abstractmethod
    def find_by_id(self, property_id: str) -> Optional[RealEstateProperty]: pass
```

## Error Handling

### Layer-Specific Error Handling

**Entities**: Raise domain-specific exceptions
```python
class InvalidPropertyValueError(Exception): pass
```

**Use Cases**: Handle business logic errors
```python
try:
    result = self.ai_gateway.analyze_bim_model(model_data)
except AIServiceUnavailableError:
    return self._fallback_analysis(model_data)
```

**Controllers**: Convert to HTTP responses
```python
try:
    result = use_case.execute()
    return jsonify({"success": True, "data": result})
except ValidationError as e:
    return jsonify({"success": False, "error": str(e)}), 400
```

## Security Considerations

### 1. **Input Validation**
- Controllers validate all input
- Entities enforce business rules
- Use cases handle authorization

### 2. **Data Sanitization**
- External interfaces sanitize input
- Entities maintain data integrity
- Gateways handle external data safely

### 3. **Authorization**
- Use cases check permissions
- Controllers authenticate requests
- Entities define access rules

## Migration Strategy

When implementing Clean Architecture in existing projects:

1. **Start with Entities**: Extract core business logic
2. **Create Use Cases**: Move application logic from controllers
3. **Build Interface Adapters**: Create boundary abstractions
4. **Isolate External Interfaces**: Separate framework dependencies

## Lessons Learned

### 5-Whys Analysis Results

**Problem 1: CSP Blocking RPC Calls**
- Why blocked? → connect-src directive too restrictive
- Why limited? → Only allowed self and api.streamswap.io
- Why missing testnet? → Configuration predated integration
- Why direct vs proxy? → Real-time data requirements
- Root cause: Missing testnet-rpc.daodiseo.chaintools.tech in CSP whitelist

**Problem 2: Logo Import Failures**
- Why broken image? → Wrong import path structure
- Why wrong path? → Used /static/ instead of /src/assets/
- Why not Vite processed? → Vite expects assets in specific directory
- Why build failed? → Asset import didn't follow Vite conventions
- Root cause: Improper asset handling strategy for Vite bundler

**Problem 3: Code Quality Issues**
- Why whitespace violations? → No automated formatting on commit
- Why long lines? → Missing line length enforcement
- Why inconsistent style? → No pre-commit hooks configured
- Why accumulated tech debt? → Rapid development without cleanup cycles
- Root cause: Missing code quality automation in development workflow

### Technical Debt Drivers & Barriers

| Issue | Driver | Barrier | Resolution |
|-------|--------|---------|------------|
| Unused dependencies | Fast prototyping | No dependency audit | Regular pip check runs |
| Wrong layer placement | Speed over structure | Insufficient architecture review | Layer validation scripts |
| CSP misconfiguration | Security-first approach | Incomplete external service mapping | Comprehensive service inventory |
| Asset import issues | Framework migration | Insufficient build tool knowledge | Proper Vite documentation study |trollers
3. **Add Interfaces**: Abstract external dependencies
4. **Refactor Controllers**: Make them thin adapters
5. **Test Each Layer**: Ensure isolation and testability

## Conclusion

This Clean Architecture implementation provides:
- **Sustainable Development**: Easy to maintain and extend
- **Business Logic Protection**: Core rules are isolated and protected
- **Technology Flexibility**: Easy to adopt new frameworks and tools
- **Team Productivity**: Clear boundaries enable parallel development
- **Quality Assurance**: Comprehensive testing at every layer

The architecture ensures that DAODISEO can evolve with changing requirements while maintaining its core business value and stability.