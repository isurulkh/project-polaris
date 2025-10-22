# 🚀 Project Polaris - Advanced RAG System

> Production-ready intelligent document management system with multi-agent architecture, powered by Google Gemini 2.5 and advanced RAG techniques.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

Project Polaris is a comprehensive document intelligence system designed for **Part 2 of the AI Agent Engineer Assessment**. It provides:

- **Advanced RAG Pipeline**: HyDE, hybrid search, reranking, and reciprocal rank fusion
- **Multi-Agent Architecture**: Specialized agents for routing, querying, and summarization
- **Production-Ready**: FastAPI backend, Streamlit UI, Docker support, monitoring
- **Gemini 2.5 Integration**: Flash for speed, Pro for quality
- **Supabase PGVector**: Direct connection to existing n8n workflow database

## 🎯 Key Features

### Advanced RAG Capabilities
- ✨ **HyDE (Hypothetical Document Embeddings)** - Improved query understanding
- 🔍 **Hybrid Search** - Vector similarity + keyword matching with BM25
- 🎯 **Cross-Encoder Reranking** - Accurate relevance scoring
- 🔄 **Reciprocal Rank Fusion** - Intelligent result combination
- 📊 **Multi-Query Generation** - Multiple query perspectives

### Multi-Agent System
- 🧠 **Router Agent** - Intelligent query classification and routing
- 💬 **Query Agent** - Information retrieval with Gemini Flash
- 📄 **Summary Agent** - Document analysis with Gemini Pro
- 🛠️ **Tool Agent** - Extensible function execution

### Production Features
- 🚀 **FastAPI Backend** - High-performance REST API
- 🎨 **Streamlit UI** - Beautiful, interactive interface
- 📊 **Prometheus Metrics** - Comprehensive monitoring
- 🐳 **Docker Support** - Containerized deployment
- 🔒 **Security** - JWT authentication, rate limiting
- 📝 **Comprehensive Logging** - Structured logging with rotation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  FastAPI REST API  │  Streamlit UI  │  CLI Tool             │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Agent Layer (LangChain)                 │
│  Router Agent  │  Query Agent  │  Summary Agent             │
│  (Gemini Flash)   (Gemini Flash)  (Gemini Pro)              │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Advanced RAG Pipeline                           │
│  HyDE → Hybrid Search → Reranking → Generation              │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  Supabase PGVector  │  Redis Cache  │  Conv. History        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (M4 Pro optimized)
- **Google AI API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Supabase Project** with PGVector (from n8n workflow)
- **Redis** (optional, for caching)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/project-polaris.git
cd project-polaris

# Create virtual environment (Python 3.11+ recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Add your API keys and database URL
```

### Configuration

Edit `.env` file with your credentials:

```bash
# Google Gemini API (Required)
GOOGLE_API_KEY="your_gemini_api_key_here"

# Supabase Database (Required)
DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"

# Collection name (must match n8n workflow)
COLLECTION_NAME="google_drive_documents"

# Optional: Redis for caching
REDIS_URL="redis://localhost:6379/0"

# Optional: Environment settings
ENVIRONMENT="development"
LOG_LEVEL="INFO"
```

### Verify Setup

```bash
# Test database connection and API keys
python scripts/test_connection.py

# Expected output:
# ✅ Database connection successful
# ✅ Vector store accessible  
# ✅ Google Gemini API working
# ✅ Collection 'google_drive_documents' found with X documents

# Quick functionality test
python scripts/quick_test.py
```

### Run the Application

#### Option 1: Development Mode (Recommended)

```bash
# Terminal 1: Start FastAPI server
source venv/bin/activate
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start Streamlit UI
source venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8501

# Access the application:
# - API Documentation: http://localhost:8000/docs
# - Streamlit UI: http://localhost:8501
# - System Info: http://localhost:8000/api/v1/system/info
```

#### Option 2: Production Mode

```bash
# Start API server (production settings)
source venv/bin/activate
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Start Streamlit (in another terminal)
source venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8501 --server.headless true
```

#### Option 3: Docker Compose

```bash
# Build and run all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Access:
# - API: http://localhost:8000
# - UI: http://localhost:8501
# - Prometheus: http://localhost:9090
# - Redis: localhost:6379
```

## 📦 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or individual services
docker build -t polaris-api -f Dockerfile .
docker run -p 8000:8000 --env-file .env polaris-api
```

## 🔧 Project Structure

```
project-polaris/
├── .env.example            # Environment template
├── .gitignore             # Git ignore patterns
├── Architecture.md        # Detailed system architecture
├── SETUP_GUIDE.md        # Comprehensive setup guide
├── docker-compose.yml    # Docker orchestration
├── Dockerfile            # API container
├── Dockerfile.streamlit  # UI container
├── requirements.txt      # Python dependencies
├── config/               # Configuration management
│   ├── __init__.py
│   ├── settings.py       # Pydantic settings
│   └── logging_config.py # Logging configuration
├── src/                  # Source code
│   ├── __init__.py
│   ├── core/            # Core components
│   │   ├── __init__.py
│   │   ├── embeddings.py    # Gemini embeddings
│   │   ├── llm.py          # Gemini LLM wrapper
│   │   └── vector_store.py # PGVector integration
│   ├── agents/          # Multi-agent system
│   │   ├── __init__.py
│   │   ├── base_agent.py   # Base agent class
│   │   ├── router_agent.py # Query routing
│   │   ├── query_agent.py  # Information retrieval
│   │   └── summary_agent.py# Summarization
│   ├── rag/             # RAG pipeline
│   │   ├── __init__.py
│   │   ├── retriever.py    # Advanced retriever
│   │   ├── hyde.py         # HyDE implementation
│   │   ├── reranker.py     # Cross-encoder reranking
│   │   └── fusion.py       # Rank fusion
│   ├── chains/          # LangChain chains
│   │   ├── __init__.py
│   │   ├── qa_chain.py     # Q&A chain
│   │   └── summary_chain.py# Summary chain
│   ├── prompts/         # Prompt templates
│   │   ├── __init__.py
│   │   ├── query_prompts.py    # Q&A prompts
│   │   ├── summary_prompts.py  # Summary prompts
│   │   └── agent_prompts.py    # Agent system prompts
│   ├── tools/           # Agent tools
│   │   ├── __init__.py
│   │   └── search_tools.py # Search utilities
│   ├── utils/           # Utility functions
│   │   ├── __init__.py
│   │   ├── cache.py        # Redis caching
│   │   ├── metrics.py      # Prometheus metrics
│   │   └── helpers.py      # Helper functions
│   └── api/             # FastAPI application
│       ├── __init__.py
│       ├── main.py         # FastAPI app
│       ├── dependencies.py # API dependencies
│       └── routes/         # API routes
│           ├── __init__.py
│           ├── health.py   # Health endpoints
│           ├── query.py    # Query endpoints
│           └── summary.py  # Summary endpoints
├── ui/                  # Streamlit interface
│   ├── __init__.py
│   ├── streamlit_app.py    # Main Streamlit app
│   ├── components/         # UI components
│   │   ├── __init__.py
│   │   ├── chat.py        # Chat interface
│   │   ├── sidebar.py     # Sidebar components
│   │   └── metrics.py     # Metrics display
│   └── styles/            # CSS styles
│       └── main.css       # Custom styles
├── scripts/             # Utility scripts
│   ├── __init__.py
│   ├── test_connection.py  # Connection tests
│   ├── quick_test.py      # Quick functionality test
│   └── setup_db.py       # Database setup
├── tests/               # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_agents/       # Agent tests
│   ├── test_rag/          # RAG tests
│   ├── test_api/          # API tests
│   └── test_utils/        # Utility tests
├── logs/                # Log files (created at runtime)
└── docs/                # Documentation
    ├── api.md            # API documentation
    ├── deployment.md     # Deployment guide
    └── troubleshooting.md# Troubleshooting guide
```

## 🎯 Usage Examples

### Query Documents

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "What are the key findings in Q4 reports?",
        "chat_history": [],  # Optional conversation history
        "filters": {},       # Optional metadata filters
        "include_sources": True,
        "include_followup": True
    }
)

result = response.json()
print(result["answer"])
print(f"Sources: {result['num_sources']}")
print("Follow-up questions:", result["followup_questions"])
```

### Generate Summary

```python
response = requests.post(
    "http://localhost:8000/api/v1/summarize",
    json={
        "query": "Summarize all client feedback",
        "summary_type": "executive",  # Options: brief, comprehensive, executive
        "max_docs": 10,
        "filters": {}  # Optional metadata filters
    }
)

result = response.json()
print(result["summary"])
print("Key Points:", result["key_points"])
print("Insights:", result["insights"])
```

### System Information

```python
response = requests.get("http://localhost:8000/api/v1/system/info")
system_info = response.json()

print(f"Status: {system_info['status']}")
print(f"Vector Store: {system_info['vector_store']['total_documents']} documents")
print(f"Models: {system_info['models']}")
```

## 🧪 Testing

### Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/test_agents/ -v      # Agent tests
pytest tests/test_rag/ -v         # RAG pipeline tests  
pytest tests/test_api/ -v         # API endpoint tests
pytest tests/test_utils/ -v       # Utility function tests

# Run tests with markers
pytest -m "not slow" -v          # Skip slow tests
pytest -m "integration" -v       # Run only integration tests
```

### Test Configuration

Tests use the following configuration:
- Test database: Separate Supabase project or local PostgreSQL
- Mock API keys for Gemini (set in `tests/conftest.py`)
- Redis: Uses fakeredis for testing
- Fixtures: Shared test data in `tests/fixtures/`

### Performance Testing

```bash
# Load testing with locust (install: pip install locust)
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Memory profiling
python -m memory_profiler scripts/profile_memory.py

# API response time testing
python tests/performance/test_response_times.py
```

## 📊 Monitoring

### Prometheus Metrics

Access metrics at: `http://localhost:9090/metrics`

Available metrics:
- Request latency
- Token usage
- Agent execution times
- Error rates
- Cache hit rates

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00Z"
# }

# System information (detailed health)
curl http://localhost:8000/api/v1/system/info

# Response includes:
# - System status and uptime
# - Vector store statistics
# - Model information
# - Performance metrics
# - Cache statistics
```

## 🔧 Configuration Options

### RAG Configuration

```python
# In .env or settings
ENABLE_HYDE=true                # Enable HyDE
ENABLE_RERANKING=true          # Enable cross-encoder reranking
ENABLE_HYBRID_SEARCH=true      # Enable hybrid search
TOP_K_RETRIEVAL=20             # Initial retrieval count
TOP_K_FINAL=5                  # Final results
SIMILARITY_THRESHOLD=0.7       # Minimum similarity score
```

### Model Configuration

```python
GEMINI_MODEL_FLASH="gemini-2.5-flash-latest"  # Fast queries
GEMINI_MODEL_PRO="gemini-2.5-pro-latest"      # Summaries
GEMINI_TEMPERATURE=0.1                         # Response randomness
```

## 🚀 Cloud Deployment

### Railway.app

```bash
railway init
railway variables set GOOGLE_API_KEY="your_key"
railway variables set DATABASE_URL="your_db_url"
railway up
```

### Google Cloud Run

```bash
gcloud run deploy polaris-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### AWS ECS

See `docs/deployment.md` for detailed AWS deployment guide.

## 📚 API Documentation

Full interactive API documentation is available at `/docs` when running the server.

### Authentication

Currently, the API is open for development. In production, JWT authentication can be enabled:

```bash
# Enable authentication in .env
ENABLE_AUTH=true
JWT_SECRET_KEY="your-secret-key"
JWT_ALGORITHM="HS256"
```

### Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Query endpoints: 60 requests per minute
- Summary endpoints: 30 requests per minute  
- Health endpoints: 120 requests per minute

### Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (if auth enabled)
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

### Main Endpoints

- `POST /api/v1/query` - Query documents with advanced RAG
  - Request: `{"query": "string", "chat_history": [], "filters": {}, "include_sources": true, "include_followup": true}`
  - Response: Answer with sources and follow-up questions
- `POST /api/v1/summarize` - Generate document summaries
  - Request: `{"query": "string", "summary_type": "comprehensive|brief|executive", "max_docs": 10, "filters": {}}`
  - Response: Summary with key points and insights
- `GET /api/v1/health` - Basic health check
  - Response: `{"status": "healthy", "timestamp": "ISO-8601"}`
- `GET /api/v1/system/info` - Detailed system information
  - Response: System stats, model info, and performance metrics

## 🛠️ Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install black ruff mypy pytest

# Setup pre-commit hooks
pre-commit install

# Run linters
black src/
ruff check src/
mypy src/
```

### Adding New Agents

1. Create agent in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Register in router agent
5. Add tests

### Customizing Prompts

Edit templates in `src/prompts/`:
- `query_prompts.py` - Q&A prompts
- `summary_prompts.py` - Summary prompts
- `agent_prompts.py` - Agent system prompts

## 🔒 Security

- JWT authentication for API endpoints
- Rate limiting per client
- Input validation with Pydantic
- SQL injection prevention
- Secure password hashing
- Environment variable encryption

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📞 Support

- **Documentation**: Check `/docs` directory
- **Issues**: Create GitHub issue
- **API Docs**: http://localhost:8000/docs

## 🙏 Acknowledgments

- Built with LangChain, FastAPI, and Streamlit
- Powered by Google Gemini 2.5 models
- Vector storage with Supabase PGVector
- Integrates with n8n workflow from Part 1

---

**Project Polaris** - Advanced Document Intelligence System
Made with ❤️ for WireApps AI Agent Engineer Assessment