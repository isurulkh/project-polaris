"""
Project Polaris FastAPI Application
Production-ready API with comprehensive endpoints
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from config.settings import settings
from src.core.embeddings import get_gemini_embeddings
from src.core.llm import get_gemini_llm
from src.core.vector_store import SupabasePGVectorStore
from src.rag.retriever import AdvancedRAGRetriever
from src.agents.router_agent import RouterAgent
from src.agents.query_agent import QueryAgent
from src.agents.summary_agent import SummaryAgent

from src.api.routes import query, summary, health

logger = logging.getLogger(__name__)


class PolarisSystem:
    """Global system state"""
    vector_store: SupabasePGVectorStore = None
    retriever: AdvancedRAGRetriever = None
    router_agent: RouterAgent = None
    query_agent: QueryAgent = None
    summary_agent: SummaryAgent = None
    llm = None
    embeddings = None


polaris = PolarisSystem()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    Initialize components on startup, cleanup on shutdown
    """
    logger.info("🚀 Starting Project Polaris...")
    
    try:
        # Initialize embeddings
        logger.info("Initializing Gemini embeddings...")
        polaris.embeddings = get_gemini_embeddings()
        
        # Initialize LLM
        logger.info("Initializing Gemini LLM...")
        polaris.llm = get_gemini_llm()
        
        # Initialize vector store
        logger.info("Connecting to Supabase PGVector...")
        polaris.vector_store = SupabasePGVectorStore(
            embedding_function=polaris.embeddings
        )
        
        # Get collection stats
        stats = polaris.vector_store.get_collection_stats()
        logger.info(f"Connected to vector store: {stats}")
        
        # Initialize retriever
        logger.info("Initializing Advanced RAG Retriever...")
        polaris.retriever = AdvancedRAGRetriever(
            vector_store=polaris.vector_store
        )
        
        # Initialize agents
        logger.info("Initializing AI agents...")
        
        # Router agent (Flash model)
        polaris.router_agent = RouterAgent(
            llm=polaris.llm.get_flash_model()
        )
        
        # Query agent (Flash model)
        polaris.query_agent = QueryAgent(
            llm=polaris.llm.get_flash_model(),
            retriever=polaris.retriever
        )
        
        # Summary agent (Pro model)
        polaris.summary_agent = SummaryAgent(
            llm=polaris.llm.get_pro_model(),
            retriever=polaris.retriever
        )
        
        logger.info("✅ Project Polaris initialized successfully!")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"API running on {settings.api_host}:{settings.api_port}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise
    
    finally:
        logger.info("Shutting down Project Polaris...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Advanced RAG System with Multi-Agent Architecture",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Prometheus metrics endpoint
if settings.enable_prometheus:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(summary.router, prefix="/api/v1", tags=["Summary"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.environment,
        "docs": "/docs"
    }


@app.get("/api/v1/system/info")
async def system_info():
    """Get system information and statistics"""
    try:
        # Get collection stats
        collection_stats = polaris.vector_store.get_collection_stats()
        
        # Get retriever stats
        retriever_stats = polaris.retriever.get_retriever_stats()
        
        # Get agent stats
        router_stats = polaris.router_agent.get_routing_stats()
        
        return {
            "system": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
            },
            "vector_store": collection_stats,
            "retriever": retriever_stats,
            "agents": {
                "router": router_stats,
                "query": polaris.query_agent.get_stats(),
                "summary": polaris.summary_agent.get_stats(),
            },
            "models": {
                "flash": settings.gemini_model_flash,
                "pro": settings.gemini_model_pro,
                "embeddings": settings.gemini_embedding_model,
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# Dependency injection
def get_polaris_system():
    """Dependency to inject Polaris system"""
    return polaris


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.api_workers,
        log_level=settings.log_level.lower()
    )