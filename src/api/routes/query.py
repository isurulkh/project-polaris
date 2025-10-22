"""
Query API Endpoints
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class QueryRequest(BaseModel):
    """Query request model"""
    query: str = Field(..., description="User question", min_length=1, max_length=2000)
    chat_history: Optional[List[tuple]] = Field(default=None, description="Conversation history")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")
    include_sources: bool = Field(default=True, description="Include source documents")
    include_followup: bool = Field(default=True, description="Generate follow-up questions")


class QueryResponse(BaseModel):
    """Query response model"""
    success: bool
    answer: str
    sources: List[Dict[str, Any]]
    num_sources: int
    followup_questions: List[str]
    metadata: Dict[str, Any]


class SearchRequest(BaseModel):
    """Document search request"""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """
    Query the document knowledge base
    
    This endpoint uses the multi-agent system to:
    1. Route the query to the appropriate agent
    2. Retrieve relevant documents using advanced RAG
    3. Generate a comprehensive answer with citations
    4. Optionally suggest follow-up questions
    """
    try:
        logger.info(f"Received query: {request.query[:100]}...")
        
        # Route query through router agent
        routing_result = polaris.router_agent.execute({
            "query": request.query
        })
        
        if not routing_result.success:
            raise HTTPException(status_code=500, detail="Routing failed")
        
        target_agent = routing_result.data["target_agent"]
        logger.info(f"Routed to: {target_agent}")
        
        # Execute query agent
        result = polaris.query_agent.execute({
            "query": request.query,
            "chat_history": request.chat_history or [],
            "filters": request.filters
        })
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        # Prepare response
        response_data = result.data
        
        return QueryResponse(
            success=True,
            answer=response_data["answer"],
            sources=response_data["sources"] if request.include_sources else [],
            num_sources=response_data["num_sources"],
            followup_questions=response_data["followup_questions"] if request.include_followup else [],
            metadata={
                "routing": routing_result.data,
                "execution_time": result.metadata.get("execution_time"),
                "num_documents_retrieved": result.metadata.get("num_documents_retrieved")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_documents(
    request: SearchRequest,
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """
    Search for relevant documents without generating an answer
    
    Returns raw document chunks for custom processing
    """
    try:
        documents = polaris.query_agent.search_documents(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Format documents
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            formatted_docs.append({
                "rank": i,
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": doc.metadata.get("rerank_score") or doc.metadata.get("score")
            })
        
        return {
            "success": True,
            "query": request.query,
            "num_results": len(formatted_docs),
            "documents": formatted_docs
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_query_stats(
    polaris=Depends(lambda: __import__('src.api.main', fromlist=['polaris']).polaris)
):
    """Get query agent statistics"""
    try:
        return {
            "success": True,
            "agent_stats": polaris.query_agent.get_stats(),
            "routing_stats": polaris.router_agent.get_routing_stats()
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))