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
git clone <your-repo-url>
cd project-polaris

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Add your API keys
```

### Configuration

Edit `.env` file with your credentials:

```bash
# Google Gemini API
GOOGLE_API_KEY="your_api_key_here"

# Supabase Database
DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres"

# Collection name (must match n8n workflow)
COLLECTION_NAME="google_drive_documents"
```

### Verify Setup

```bash
# Run connection tests
python scripts/test_connection.py

# Run functionality tests
python scripts/quick_test.py
```

### Run the Application

```bash
# Terminal 1: Start API Server
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Start Streamlit UI
streamlit run ui/streamlit_app.py --server.port 8501
```

Access the application:
- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **System Info**: http://localhost:8000/api/v1/system/info

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
├── config/                  # Configuration management
│   ├── settings.py         # Pydantic settings
│   └── logging_config.py   # Logging configuration
├── src/
│   ├── core/               # Core components
│   │   ├── embeddings.py   # Gemini embeddings
│   │   ├── llm.py          # Gemini LLM wrapper
│   │   └── vector_store.py # PGVector integration
│   ├── agents/             # Multi-agent system
│   │   ├── router_agent.py # Query routing
│   │   ├── query_agent.py  # Information retrieval
│   │   └── summary_agent.py# Summarization
│   ├── rag/                # RAG pipeline
│   │   ├── retriever.py    # Advanced retriever
│   │   ├── hyde.py         # HyDE implementation
│   │   ├── reranker.py     # Cross-encoder reranking
│   │   └── fusion.py       # Rank fusion
│   ├── chains/             # LangChain chains
│   │   ├── qa_chain.py     # Q&A chain
│   │   └── summary_chain.py# Summary chain
│   ├── prompts/            # Prompt templates
│   └── api/                # FastAPI application
├── ui/                     # Streamlit interface
├── scripts/                # Utility scripts
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## 🎯 Usage Examples

### Query Documents

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "What are the key findings in Q4 reports?",
        "include_sources": True,
        "include_followup": True
    }
)

result = response.json()
print(result["answer"])
print(f"Sources: {result['num_sources']}")
```

### Generate Summary

```python
response = requests.post(
    "http://localhost:8000/api/v1/summarize",
    json={
        "query": "Summarize all client feedback",
        "summary_type": "executive",
        "max_docs": 10
    }
)

result = response.json()
print(result["summary"])
print("Key Points:", result["key_points"])
```

### Search Documents

```python
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "financial performance",
        "top_k": 10
    }
)

docs = response.json()["documents"]
for doc in docs:
    print(f"Rank {doc['rank']}: {doc['content'][:100]}...")
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific tests
pytest tests/test_agents/ -v
pytest tests/test_rag/ -v
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
# Basic health
curl http://localhost:8000/api/v1/health

# Detailed health
curl http://localhost:8000/api/v1/health/detailed

# Readiness probe
curl http://localhost:8000/api/v1/ready
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

Full API documentation available at `/docs` when running the server.

### Main Endpoints

- `POST /api/v1/query` - Query documents
- `POST /api/v1/summarize` - Generate summaries
- `POST /api/v1/search` - Search documents
- `GET /api/v1/system/info` - System information
- `GET /api/v1/health` - Health check

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