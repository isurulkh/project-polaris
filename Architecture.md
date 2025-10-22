# Project Polaris - Detailed Architecture Documentation

## 🏗️ System Architecture Overview

Project Polaris implements a production-ready, multi-agent RAG (Retrieval-Augmented Generation) system with advanced retrieval techniques and intelligent query routing.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  Web Browser │ Mobile App │ API Client │ CLI Tool               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Layer (FastAPI)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Health  │  │  Query   │  │ Summary  │  │  Search  │       │
│  │ Endpoint │  │ Endpoint │  │ Endpoint │  │ Endpoint │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
│  Middleware: Auth │ Rate Limit │ CORS │ Logging                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestration Layer                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Router Agent                             │  │
│  │  • Intent Classification                                  │  │
│  │  • Agent Selection                                        │  │
│  │  • Query Preprocessing                                    │  │
│  │  Model: Gemini 2.5 Flash                                  │  │
│  └──────────────┬───────────────┬───────────────┬────────────┘  │
│                 │               │               │               │
│      ┌──────────▼────┐ ┌───────▼──────┐ ┌─────▼──────┐       │
│      │  Query Agent  │ │Summary Agent │ │ Tool Agent  │       │
│      │ Gemini Flash  │ │ Gemini Pro   │ │Gemini Flash │       │
│      └───────────────┘ └──────────────┘ └─────────────┘       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Pipeline Layer                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 1: Query Analysis & Enhancement                    │   │
│  │  • HyDE (Hypothetical Document Embeddings)              │   │
│  │  • Query Expansion                                       │   │
│  │  • Multi-Query Generation                                │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   ▼                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 2: Hybrid Retrieval                                │   │
│  │  ┌─────────────┐         ┌─────────────┐                │   │
│  │  │   Vector    │         │   Keyword   │                │   │
│  │  │   Search    │         │   Search    │                │   │
│  │  │  (Cosine)   │         │   (BM25)    │                │   │
│  │  └──────┬──────┘         └──────┬──────┘                │   │
│  │         │                       │                        │   │
│  │         └───────────┬───────────┘                        │   │
│  │                     ▼                                    │   │
│  │         ┌───────────────────────┐                        │   │
│  │         │ Reciprocal Rank Fusion│                        │   │
│  │         └───────────┬───────────┘                        │   │
│  └─────────────────────┼─────────────────────────────────────   │
│                        ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 3: Reranking                                       │   │
│  │  • Cross-Encoder Scoring                                 │   │
│  │  • Relevance Filtering                                   │   │
│  │  • Context Optimization                                  │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   ▼                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 4: Generation                                      │   │
│  │  • Context Assembly                                      │   │
│  │  • Prompt Construction                                   │   │
│  │  • Response Generation (Gemini)                          │   │
│  │  • Post-Processing                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Supabase   │  │    Redis    │  │Conversation │            │
│  │  PGVector   │  │    Cache    │  │   History   │            │
│  │  (Primary)  │  │  (Optional) │  │   (SQLite)  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Deep Dive

### 1. Vector Store Layer (Supabase PGVector)

**Purpose**: Persistent storage for document embeddings with vector similarity search.

**Key Features**:
- **Direct Connection**: Uses existing n8n workflow database
- **Vector Operations**: Cosine similarity, L2 distance, inner product
- **HNSW Indexing**: Fast approximate nearest neighbor search
- **Metadata Filtering**: Filter by filename, type, date, etc.
- **Hybrid Capabilities**: Full-text search + vector search

**Schema**:
```sql
-- Collection table (created by n8n)
langchain_pg_collection (
    uuid UUID PRIMARY KEY,
    name VARCHAR,
    cmetadata JSONB
)

-- Embedding table (created by n8n)
langchain_pg_embedding (
    uuid UUID PRIMARY KEY,
    collection_id UUID,
    embedding VECTOR(768),  -- Gemini embedding dimension
    document TEXT,
    cmetadata JSONB
)

-- Indexes
CREATE INDEX idx_embedding_vector ON langchain_pg_embedding 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_document_gin ON langchain_pg_embedding 
USING gin(to_tsvector('english', document));
```

**Connection Flow**:
```python
DATABASE_URL → SQLAlchemy Engine → PGVector Store → LangChain Interface
```

---

### 2. Embedding Layer (Google Gemini)

**Model**: `models/text-embedding-004`
**Dimension**: 768
**Task Types**: 
- `retrieval_document` - For indexing documents
- `retrieval_query` - For search queries

**Why This Model**:
- Multilingual support
- Long context window
- Cost-effective
- Consistent with n8n workflow

**Usage**:
```python
# Document embedding
embeddings.embed_documents(["doc1", "doc2"])

# Query embedding  
embeddings.embed_query("user question")
```

---

### 3. Advanced RAG Pipeline

#### 3.1 HyDE (Hypothetical Document Embeddings)

**Purpose**: Generate hypothetical answers to improve retrieval accuracy.

**Process**:
1. Use LLM to generate hypothetical document that would answer query
2. Embed hypothetical document
3. Search using hypothetical embedding
4. Combine with regular search results

**Benefits**:
- Better semantic matching
- Handles ambiguous queries
- Improves recall

**Example**:
```
Query: "What was our revenue growth?"
HyDE Generated: "Our revenue grew by 25% in Q4 2024, reaching $50M..."
Search with HyDE embedding → Better matches
```

#### 3.2 Hybrid Search

**Purpose**: Combine vector similarity with keyword matching.

**Components**:
- **Vector Search**: Semantic similarity using cosine distance
- **Keyword Search**: BM25 algorithm on PostgreSQL full-text search
- **Fusion**: Reciprocal Rank Fusion (RRF) to combine results

**Formula (RRF)**:
```
score(d) = Σ (1 / (k + rank_i(d)))
where k = 60 (constant)
```

**Benefits**:
- Captures both semantic and lexical matches
- Better for specific terms/names
- Robust to different query types

#### 3.3 Cross-Encoder Reranking

**Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Purpose**: Precise relevance scoring of retrieved candidates.

**Process**:
1. Initial retrieval: Get top-20 candidates
2. Reranking: Score each query-document pair
3. Selection: Return top-5 most relevant

**Why Cross-Encoder**:
- More accurate than bi-encoder
- Considers query-document interaction
- Better than similarity scores alone

---

### 4. Multi-Agent System

#### 4.1 Router Agent

**Model**: Gemini 2.5 Flash
**Purpose**: Query intent classification and routing

**Categories**:
- `QUERY` → Query Agent (information retrieval)
- `SUMMARY` → Summary Agent (document summarization)
- `ANALYSIS` → Summary Agent (deep analysis)
- `METADATA` → Tool Agent (statistics, exports)
- `GENERAL` → Query Agent (default)

**Classification Process**:
```python
User Query → LLM Classification → Category + Reasoning → Target Agent
```

**Benefits**:
- Optimized agent selection
- Better resource utilization
- Specialized handling

#### 4.2 Query Agent

**Model**: Gemini 2.5 Flash
**Purpose**: Fast information retrieval and Q&A

**Capabilities**:
- Single document queries
- Multi-document queries
- Conversational context
- Follow-up questions
- Source citations

**Process**:
```
Query → Advanced Retrieval → Context Assembly → 
LLM Generation → Answer + Sources + Follow-ups
```

#### 4.3 Summary Agent

**Model**: Gemini 2.5 Pro
**Purpose**: High-quality document summarization

**Summary Types**:
- **Brief**: 3-5 sentences
- **Comprehensive**: Multi-paragraph analysis
- **Executive**: Business-focused with recommendations

**Strategies**:
- **Direct**: For <10 documents
- **Map-Reduce**: For larger document sets

**Process**:
```
Topic → Document Retrieval → Summarization Strategy Selection →
Generation → Structured Output (Summary + Key Points + Insights)
```

---

### 5. LangChain Integration

**Chains Used**:

1. **QA Chain**:
   ```python
   Context + Question → LLM → Answer
   Context + Question + History → LLM → Contextual Answer
   ```

2. **Summary Chain**:
   ```python
   Documents → [Map Phase] → Individual Summaries →
   [Reduce Phase] → Combined Summary
   ```

3. **Conversation Chain**:
   ```python
   Query + History → Context-Aware Response
   ```

**Custom Components**:
- Custom retriever with advanced features
- Custom document loaders
- Custom prompt templates
- Custom callbacks for monitoring

---

### 6. Caching Strategy (Redis)

**What's Cached**:
- Query results (TTL: 1 hour)
- Embedding vectors (TTL: 24 hours)
- System stats (TTL: 5 minutes)

**Cache Keys**:
```python
query:{hash(query)} → results
embedding:{hash(text)} → vector
stats:system → system_info
```

**Benefits**:
- Reduced API calls
- Faster response times
- Lower costs

---

### 7. API Layer (FastAPI)

**Architecture**:
```
Request → Middleware → Router → Endpoint → 
Agent Execution → Response
```

**Middleware Stack**:
1. CORS
2. Authentication (JWT)
3. Rate Limiting
4. Logging
5. Error Handling

**Endpoints**:
- `/api/v1/query` - Question answering
- `/api/v1/summarize` - Document summarization
- `/api/v1/search` - Document search
- `/api/v1/system/info` - System status
- `/api/v1/health` - Health checks

---

## 🔄 Request Flow Examples

### Example 1: Simple Query

```
1. User: "What are the Q4 results?"
2. API receives request
3. Router Agent: Classifies as QUERY
4. Query Agent activated
5. RAG Pipeline:
   - Retrieves top-20 documents
   - Reranks to top-5
   - Assembles context
6. Gemini Flash generates answer
7. Response with answer + sources + follow-ups
```

### Example 2: Summary Request

```
1. User: "Summarize all client feedback"
2. API receives request
3. Router Agent: Classifies as SUMMARY
4. Summary Agent activated
5. RAG Pipeline:
   - Retrieves top-10 relevant documents
   - Applies map-reduce if needed
6. Gemini Pro generates comprehensive summary
7. Response with summary + key points + insights
```

### Example 3: Complex Query with HyDE

```
1. User: "What improvements were suggested?"
2. Router → Query Agent
3. RAG Pipeline:
   a. HyDE: Generates hypothetical answer
   b. Hybrid Search:
      - Vector search with HyDE embedding
      - Keyword search for "improvements"
      - Fusion of results
   c. Reranking with cross-encoder
   d. Context assembly
4. Gemini Flash generates detailed answer
5. Response with comprehensive answer
```

---

## 🎯 Design Decisions

### Why Gemini 2.5?

**Flash Model**:
- Fast inference (<1s)
- Cost-effective
- Good for queries and routing
- Large context window (1M tokens)

**Pro Model**:
- Highest quality
- Better for summaries
- Complex reasoning
- Multimodal capabilities

### Why Supabase PGVector?

- Already used in n8n workflow
- Native PostgreSQL integration
- HNSW indexing for speed
- Full-text search support
- Easy to scale
- Great developer experience

### Why Multi-Agent Architecture?

- Specialized agents for specific tasks
- Better resource allocation
- Easier to maintain and extend
- Supports different LLM models per agent
- Clear separation of concerns

### Why Advanced RAG?

- **HyDE**: Better query understanding
- **Hybrid Search**: Handles all query types
- **Reranking**: Precision improvements
- **RRF**: Robust result combination

---

## 📈 Performance Characteristics

### Latency Targets

- Simple Query: <2 seconds
- Complex Query: <5 seconds
- Summary (5 docs): <8 seconds
- Summary (20 docs): <15 seconds

### Throughput

- Concurrent users: 100+
- Queries per second: 50+
- Cache hit rate: >60%

### Cost Optimization

- Cache frequently asked questions
- Use Flash model by default
- Pro model only for summaries
- Batch embedding operations

---

## 🔒 Security Architecture

### Authentication Flow

```
Client → JWT Token → Validation → Rate Limit Check → 
Authorization → Endpoint Access
```

### Security Measures

1. **API Key Protection**: Environment variables
2. **JWT Tokens**: Short-lived access tokens
3. **Rate Limiting**: Per-client limits
4. **Input Validation**: Pydantic models
5. **SQL Injection Prevention**: Parameterized queries
6. **CORS**: Configurable origins
7. **HTTPS**: TLS 1.3 in production

---

## 📊 Monitoring & Observability

### Metrics Collected

- Request count and latency
- Agent execution times
- Token usage per request
- Cache hit/miss rates
- Error rates by endpoint
- Database query performance

### Logging Strategy

- **Structured Logging**: JSON format
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Rotation**: Daily, 30-day retention
- **Centralization**: Supports external log aggregation

### Health Checks

- **/health**: Basic liveness
- **/health/detailed**: Component status
- **/ready**: Kubernetes readiness probe
- **/metrics**: Prometheus metrics

---

## 🚀 Scalability Considerations

### Horizontal Scaling

- Stateless API design
- Load balancer compatible
- Shared cache (Redis)
- Connection pooling

### Vertical Scaling

- Configurable worker count
- Adjustable context windows
- Batch size tuning
- Cache size optimization

### Database Scaling

- PGVector supports billions of vectors
- HNSW index for fast search
- Read replicas for queries
- Connection pooling (20-100 connections)

---

## 🔧 Configuration & Tuning

### RAG Tuning Parameters

```python
TOP_K_RETRIEVAL = 20      # Initial candidates
TOP_K_FINAL = 5           # Final results
SIMILARITY_THRESHOLD = 0.7 # Minimum score
CHUNK_SIZE = 1000         # Document chunk size
CHUNK_OVERLAP = 200       # Overlap between chunks
```

### LLM Parameters

```python
TEMPERATURE = 0.1         # Deterministic responses
MAX_OUTPUT_TOKENS = 8192  # Long responses
TOP_P = 0.95             # Nucleus sampling
TOP_K = 40               # Token selection
```

### Cache Configuration

```python
CACHE_TTL = 3600         # 1 hour TTL
ENABLE_CACHE = true      # Toggle caching
REDIS_URL = ...          # Cache backend
```

---

This architecture provides a production-ready, scalable, and maintainable system for intelligent document management and retrieval.