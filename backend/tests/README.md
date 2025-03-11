# DocSync API Tests

These tests verify the external behavior of the DocSync API endpoints.

## Setup

1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Make sure the DocSync API server is running at http://localhost:8000

## Running Tests

To run all tests:
```bash
python -m unittest test_api.py
```

To run a specific test:
```bash
python -m unittest test_api.TestDocSyncAPI.test_health_check
```

## Test Coverage

The tests cover:
- Health check endpoint
- Document creation
- Document retrieval
- Document listing with pagination
- Document history tracking
- Error handling for:
  - Non-existent documents
  - Invalid pagination parameters
  - Invalid document data
- Validation of document data

## Running Specific Test Groups

```bash
# Run pagination tests
python -m unittest test_api.TestDocSyncAPI.test_list_documents_pagination

# Run history tests
python -m unittest test_api.TestDocSyncAPI.test_document_history
```

## Notes

- Tests are designed to run against a running instance of the API
- Tests are independent and can be run in any order
- Database state may affect test results
