# WebSocket Agent Integration Tests

This directory contains comprehensive integration tests for the WebSocket-based pharmacy agent system. The tests verify the functionality of both InfoAgent (for existing pharmacies) and CollectionAgent (for new pharmacy registration).

## Test Files

### 1. `test_info_agent_integration.py`
Tests the InfoAgent for existing pharmacy queries. This agent handles queries about pharmacies already in the database.

**Test Coverage:**
- Connection establishment
- Agent initialization with existing pharmacy phone
- Prescription queries
- Pharmacy details queries
- Specific drug availability queries
- Conversation context/memory testing

**Expected Pharmacy Data:**
```json
{
  "id": 1,
  "name": "HealthFirst Pharmacy",
  "phone": "+1-555-123-4567",
  "email": "contact@healthfirst.com",
  "city": "New York",
  "state": "NY",
  "prescriptions": [
    {"drug": "Lisinopril", "count": 42},
    {"drug": "Atorvastatin", "count": 38},
    {"drug": "Metformin", "count": 20}
  ]
}
```

### 2. `test_collection_agent_integration.py`
Tests the CollectionAgent for new pharmacy registration through conversational data collection.

**Test Coverage:**
- Connection establishment
- Agent initialization with new phone number
- Sequential data collection (name, location, email)
- Prescription data collection (optional)
- Email validation
- Bulk information extraction
- Collection completion verification

### 3. `test_websocket_comprehensive.py`
Comprehensive test suite covering both agents with edge cases and performance testing.

**Test Coverage:**
- Both InfoAgent and CollectionAgent scenarios
- Edge cases (invalid phones, rapid messages, long messages)
- Performance metrics (connection time, response time)
- Concurrent connection testing
- Error handling verification

### 4. `test_agents_simple.py`
Simple, quick verification test for both agents with minimal complexity.

**Test Coverage:**
- Basic InfoAgent prescription query
- Basic CollectionAgent data collection flow
- Quick pass/fail verification

### 5. `run_integration_tests.py`
Master test runner with interactive menu and batch execution options.

**Features:**
- Interactive menu for test selection
- Individual or batch test execution
- Server availability checking
- Formatted test results and summary

## Prerequisites

### 1. Start the Server
```bash
# Using uv
uv run python main.py

# Or using make
make run
```

The server should be running on `http://localhost:8000`

### 2. Environment Variables
Ensure `.env` file contains:
```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Install Dependencies
The project uses `uv` for dependency management. All tests should be run with:
```bash
uv run python <test_file>
```

## Running Tests

### Option 1: Run Individual Tests
```bash
# Test InfoAgent
uv run python test_info_agent_integration.py

# Test CollectionAgent
uv run python test_collection_agent_integration.py

# Run comprehensive tests
uv run python test_websocket_comprehensive.py

# Run simple verification
uv run python test_agents_simple.py
```

### Option 2: Use Test Runner

**Interactive mode:**
```bash
uv run python run_integration_tests.py
```

**Run specific test suite:**
```bash
# Run InfoAgent tests
uv run python run_integration_tests.py --test info

# Run CollectionAgent tests
uv run python run_integration_tests.py --test collection

# Run comprehensive tests
uv run python run_integration_tests.py --test comprehensive

# Run all tests
uv run python run_integration_tests.py --test all
```

**Skip server check:**
```bash
uv run python run_integration_tests.py --no-check --test all
```

## Expected Test Results

### Successful InfoAgent Test Output:
```
✅ Connection Establishment: PASS
✅ InfoAgent Initialization: PASS
✅ Prescription Query: PASS
✅ Pharmacy Details Query: PASS
✅ Specific Drug Query: PASS
✅ Conversation Context: PASS
```

### Successful CollectionAgent Test Output:
```
✅ Connection Establishment: PASS
✅ CollectionAgent Initialization: PASS
✅ Name Collection: PASS
✅ Location Collection: PASS
✅ Email Collection: PASS
✅ Collection Complete: PASS
```

## Test Data

### Existing Pharmacy Phones (InfoAgent)
- `+1-555-123-4567` - HealthFirst Pharmacy
- `+1-555-987-6543` - QuickMeds Rx
- `+1-555-666-7777` - MediCare Plus
- `+1-555-222-3333` - CityPharma
- `+1-555-444-5555` - Wellness Hub

### New Phone Numbers (CollectionAgent)
Any phone number not in the above list will trigger the CollectionAgent for new registration.

## WebSocket Protocol

### Connection Flow:
1. Client connects to `ws://localhost:8000/ws/pharmacy-agent`
2. Server sends `connection_established` with session ID
3. Client sends `init` message with phone number
4. Server responds with `agent_ready` and agent type
5. Conversation begins with `message` type exchanges
6. Client sends `close` to terminate

### Message Types:

**Client → Server:**
```json
{"type": "init", "phone": "+1-555-123-4567"}
{"type": "message", "content": "user message"}
{"type": "close"}
```

**Server → Client:**
```json
{"type": "connection_established", "session_id": "uuid"}
{"type": "agent_ready", "agent_type": "info|collection"}
{"type": "response", "content": "agent response"}
{"type": "collection_progress", "fields_collected": [], "fields_remaining": []}
{"type": "collection_complete", "pharmacy_data": {}}
{"type": "error", "message": "error description"}
```

## Troubleshooting

### Connection Timeout
- Verify server is running: `curl http://localhost:8000/health`
- Check WebSocket endpoint: `ws://localhost:8000/ws/pharmacy-agent`
- Ensure OPENAI_API_KEY is set in environment

### Agent Not Initializing
- Verify phone number format (use full format: +1-555-XXX-XXXX)
- Check if phone exists in database (affects agent type selection)
- Review server logs for LLM API errors

### Collection Not Completing
- Ensure all required fields are provided: name, email, city, state
- Email must be valid format (contains @)
- Phone is automatically set from initialization

### Test Failures
- Check server logs for detailed error messages
- Verify OpenAI API is accessible
- Ensure memory management is working (30-minute timeout)

## Performance Expectations

- Connection establishment: < 500ms
- Agent initialization: < 2s
- Query response time: 2-5s (depends on LLM)
- Collection completion: 10-30s (full flow)

## Notes

- Tests use real LLM calls (OpenAI API)
- Each test creates a new WebSocket session
- Sessions timeout after 30 minutes of inactivity
- Agent memory is thread-safe and session-isolated
- Collection data is not persisted (in-memory only)
