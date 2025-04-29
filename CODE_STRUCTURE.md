# Daodiseo Real Estate Tokenization Platform - Code Structure

This document outlines the code organization for the Daodiseo platform, following a clean architecture approach.

## Directory Structure

```
daodiseo/
├── docs/                   # Documentation files
│   └── api/                # API documentation
├── src/                    # Source code
│   ├── controllers/        # Web controllers (HTTP layer)
│   ├── data/               # Data storage files (JSON, etc.)
│   ├── entities/           # Domain entities
│   ├── external_interfaces/ # Interfaces to external systems (UI, APIs)
│   │   ├── config/         # Configuration for external interfaces
│   │   └── ui/             # User interface components
│   │       ├── static/     # Static assets (CSS, JS, images)
│   │       └── templates/  # HTML templates
│   ├── gateways/           # Gateway implementations for external services
│   │   └── ifc/            # IFC file handling gateways
│   ├── services/           # Domain services
│   │   └── ai/             # AI services for analysis
│   └── use_cases/          # Application use cases
├── tests/                  # Test suite
├── uploads/                # Uploaded files storage
└── main.py                 # Application entry point
```

## Architectural Layers

The codebase follows a clean architecture pattern with the following layers:

1. **Domain Layer** (`src/entities/`)
   - Core business entities
   - Business rules
   - No dependencies on other layers

2. **Application Layer** (`src/use_cases/`)
   - Implements use cases using entities
   - Orchestrates flow between domain and infrastructure
   - Depends on domain layer only

3. **Interface Adapters** (`src/controllers/`, `src/gateways/`)
   - Converts data between application and external formats
   - Controllers handle HTTP requests
   - Gateways adapt external services to domain needs

4. **Infrastructure Layer** (`src/external_interfaces/`, `src/services/`)
   - Implements interfaces defined by inner layers
   - Handles communication with external systems
   - UI components, databases, external APIs, etc.

## Key Components

### BIM Components (`src/gateways/ifc/`)
Building Information Modeling components that handle 3D model data, IFC file processing, and integrations with BIM providers.

### Controllers (`src/controllers/`)
HTTP controllers that handle web requests and responses. These convert between HTTP and domain objects.

### Entities (`src/entities/`)
Domain entities that represent core business concepts like Property, Transaction, User, etc.

### External Interfaces (`src/external_interfaces/`)
Implementations of adapters for external systems, including UI templates and frontend assets.

### Gateways (`src/gateways/`)
Interface adapters for external services like blockchain APIs, authentication services, etc.

### Services (`src/services/`)
Domain services that implement business logic that spans multiple entities.

### Use Cases (`src/use_cases/`)
Application use cases that orchestrate the flow of data between the domain and infrastructure layers.

## Dependencies Flow

Dependencies point inward, with the domain layer having no dependencies on other layers:

```
Infrastructure → Interface Adapters → Application → Domain
```

This ensures that business rules and entities are isolated from external concerns.

## Code Quality

To check code quality:

1. Run the code quality script:
   ```
   python code_check.py
   ```

2. Or run flake8 directly:
   ```
   flake8
   ```

The project is configured with flake8 settings in `setup.cfg`.