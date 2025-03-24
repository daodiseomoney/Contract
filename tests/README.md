# Test Suite for Real Estate Tokenization Platform

This directory contains the comprehensive test suite for our Real Estate Tokenization platform, focusing heavily on ensuring compatibility with Keplr wallet and proper blockchain transaction handling.

## Test Organization

The tests are organized into several categories:

### API Endpoint Tests
- `test_api_endpoints.py`: Basic API endpoint tests that verify core HTTP functionality

### End-to-End Tests
- `test_end_to_end.py`: Simulated end-to-end flows through the application with mocked external dependencies

### Isolated Tests
- `test_isolated_client.py`: Tests using a dedicated Flask test client to prevent interference
- `test_isolated_flow.py`: Business logic tests isolated from the full application

### Keplr Integration Tests
- `test_kepler_gateway.py`: Tests for our gateway to the Keplr wallet
- `test_keplr_frontend_compatibility.py`: Tests that confirm our JavaScript conversion functions work correctly
- `test_keplr_message_browser_simulation.py`: Tests that simulate actual browser behavior with Keplr wallet
- `test_keplr_message_formats.py`: Tests for the strict message format requirements of the Keplr wallet

### Message Format Tests
- `test_message_formats.py`: Tests for conversion between Amino and Proto message formats

### Service Tests
- `test_transaction_service.py`: Tests for the transaction service that interacts with the blockchain

### Utility Tests
- `test_utils.py`: Tests for utility functions used throughout the application

## Testing Approach

Our test suite uses a combination of approaches:

1. **Mocks**: Many tests use mocks to avoid real blockchain interactions and external dependencies
2. **Browser Simulation**: Key tests simulate actual browser behavior to catch integration issues
3. **Format Validation**: Strict format validation to ensure compatibility with Keplr wallet expectations

## Key Test Areas

The test suite focuses heavily on several critical areas:

1. **Message Format Conversion**: Testing conversion between Amino and Proto formats
2. **Field Name Conversion**: Testing snake_case to camelCase conversion
3. **Error Scenario Reproduction**: Reproducing and fixing the "Expected a message object" error
4. **Memo Parsing**: Testing both legacy and simplified memo format parsing

## Coverage Notes

While traditional coverage metrics may not show high percentages due to the heavy use of mocks, our tests thoroughly validate the interfaces, formats, and behaviors that are critical to the application's functionality.

The tests intentionally focus on the interface boundaries (especially the Keplr wallet integration) rather than testing internal implementation details, as the integration points are where most failures occurred.

## Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_keplr_message_formats.py

# Run with coverage report
python -m pytest --cov=src tests/
```