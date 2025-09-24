# AI Agent Call Assistant

A FastAPI-based API service for managing pharmacy data with phone number search capabilities, integrated with LangChain agents for intelligent conversational interactions. Built with Python 3.13 and managed with the uv package manager.

## Project Structure

```
ai_agent_call_assistant/
├── src/
│   ├── agents/           # LangChain agent implementations
│   │   └── tools/        # Custom tools for agents
│   ├── clients/          # External API clients
│   ├── endpoints/        # FastAPI endpoints
│   │   └── swagger/      # OpenAPI/Swagger configurations
│   ├── models/           # Pydantic data models
│   ├── routes/           # API route definitions
│   ├── services/         # Business logic services
│   ├── utils/            # Utility functions
│   ├── websocket/        # WebSocket handlers
│   └── dependencies.py   # Dependency injection
├── config/               # Configuration files
├── docs/                 # Documentation
├── spec/                 # API specifications
├── test_*.py             # Integration test files
├── main.py               # Application entry point
├── Makefile              # Build automation
├── pyproject.toml        # Project dependencies
├── .env                  # Environment configuration (git-ignored)
├── .env.example          # Environment template
└── CLAUDE.md             # Claude Code AI instructions
```

## Prerequisites

- Python 3.13
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai_agent_call_assistant
```

2. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync
```

4. Set up environment configuration:
```bash
cp .env.example .env
```

5. Edit `.env` and configure:
   - Update `PHARMACY_API__BASE_URL` with your pharmacy API URL
   - Set your `OPENAI_API_KEY` for LangChain agents
   - Adjust other settings as needed

## Running the API

### Using uv directly:
```bash
uv run python main.py
```

### Using Makefile:
```bash
make run
```

The server will start on `http://0.0.0.0:8000`

### Available endpoints:
- `GET /` - API documentation (Swagger UI)
- `GET /health` - Health check endpoint
- `GET /pharmacies` - List all pharmacy companies
- `GET /pharmacies/search?phone={phone}` - Search pharmacy by phone
- `DELETE /pharmacies/cache` - Clear pharmacy cache
- `WS /ws/{session_id}` - WebSocket for agent interactions

## Running Tests

### Run all test files:
```bash
# Test agents
uv run python test_agents_simple.py

# Test collection agent integration
uv run python test_collection_agent_integration.py

# Test info agent integration
uv run python test_info_agent_integration.py

# Test WebSocket comprehensive
uv run python test_websocket_comprehensive.py
```

### Run integration tests suite:
```bash
uv run python run_integration_tests.py
```

### Validate code quality:
```bash
make validate
```

This runs pre-commit hooks for code quality checks.

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options:

- **Environment**: `development`, `staging`, or `production`
- **Server**: Host, port, and log level settings
- **API Configuration**: Timeout, retry settings
- **Cache**: TTL (Time To Live) in seconds
- **LangChain**: OpenAI API key and model settings
- **Agent**: Model, temperature, token limits

Configuration supports both nested format (`SERVER__HOST`) and JSON format.

## Development

### Virtual Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate when done
deactivate
```

### Code Quality

The project uses pre-commit hooks for maintaining code quality. Run validation:

```bash
make validate
```

## Dependencies

Key dependencies:
- **FastAPI** (>=0.116.2) - Web framework
- **Pydantic** (>=2.11.9) - Data validation
- **httpx** (>=0.28.2) - Async HTTP client
- **LangChain** (>=0.3.27) - AI/LLM integration
- **uvicorn[standard]** - ASGI server with uvloop

## Security Notes

- Never commit actual secrets to the repository
- Use environment variables or secret management systems
- The `.env` file is git-ignored by default
- In production, manage sensitive values through container orchestration secrets

## License

[Your License Here]
