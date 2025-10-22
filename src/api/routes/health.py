"""
Health Check and Monitoring Endpoints
"""

import logging
from fastapi import APIRouter, Depends
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/health/detailed")
async def detailed_health_check(
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """
    Detailed health check with component status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    try:
        # Check vector store
        try:
            stats = polaris.vector_store.get_collection_stats()
            health_status["components"]["vector_store"] = {
                "status": "healthy",
                "details": stats
            }
        except Exception as e:
            health_status["components"]["vector_store"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check LLM
        try:
            test_response = polaris.llm.get_flash_model().invoke("test")
            health_status["components"]["llm"] = {
                "status": "healthy",
                "models": {
                    "flash": polaris.llm.flash_model.model_name,
                    "pro": polaris.llm.pro_model.model_name
                }
            }
        except Exception as e:
            health_status["components"]["llm"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check agents
        health_status["components"]["agents"] = {
            "status": "healthy",
            "router": polaris.router_agent.name,
            "query": polaris.query_agent.name,
            "summary": polaris.summary_agent.name
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/ready")
async def readiness_check(
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """
    Kubernetes readiness probe
    Returns 200 if system is ready to accept requests
    """
    try:
        # Quick check if components are initialized
        if polaris.vector_store and polaris.retriever and polaris.query_agent:
            return {"ready": True}
        else:
            return {"ready": False}, 503
    except Exception:
        return {"ready": False}, 503


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    Returns 200 if application is alive
    """
    return {"alive": True}