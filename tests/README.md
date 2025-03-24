# End-to-End Tests for Real Estate Tokenization Platform

This directory contains end-to-end pytest tests for the Real Estate Tokenization Platform.

## Overview

The test suite in `test_end_to_end.py` verifies the complete flow of the application from:
1. File upload
2. Transaction creation
3. Keplr wallet signature simulation
4. Transaction broadcasting
5. Contract status verification

## Running the Tests

To run all tests:

```bash
pytest tests/
```

To run specific tests with detailed output:

```bash
pytest tests/test_end_to_end.py::TestEndToEndFlow::test_full_e2e_flow -v
```

To generate a coverage report:

```bash
pytest --cov=src tests/
```

## Test Structure

- **TestEndToEndFlow** - Main test class that verifies the entire application workflow
  - `test_file_upload` - Verifies file upload functionality
  - `test_account_info` - Tests account data retrieval
  - `test_sign_transaction` - Tests transaction signing with mocked Keplr signature
  - `test_broadcast_transaction` - Tests transaction broadcasting
  - `test_contracts_endpoint` - Verifies contracts API endpoint
  - `test_full_e2e_flow` - Simulates the complete end-to-end flow from upload to signed transaction

- **TestUtilities** - Tests for application utility functions
  - `test_memo_parsing` - Tests both legacy and new memo formats
  - `test_message_format_conversion` - Tests conversion between Amino and Proto message formats

## Mock Data

The tests use fixtures to provide mock data:
- `sample_bim_file` - Creates a sample BIM file for testing
- `mock_account_data` - Provides mock account data from blockchain
- `mock_keplr_signature` - Simulates Keplr wallet signature response
- `mock_broadcast_response` - Mock successful transaction broadcast response

## Debugging

Tests include detailed logging. Set the log level to DEBUG for more information:

```python
logging.basicConfig(level=logging.DEBUG)
```